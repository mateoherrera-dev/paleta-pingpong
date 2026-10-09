# Contratos entre módulos

Estos formatos son lo que permite que cada uno trabaje en su parte sin esperar a los demás.
**Si alguien necesita cambiar algo de acá, lo charla con todo el grupo y lo anota en este archivo antes de tocar el código.**

## 1. Ejes del sensor

Todos los datos usan los mismos ejes, medidos sobre la paleta (no sobre el módulo):

```
            cara roja (frente)
                 ▲ Z
                 │
          ┌──────┴──────┐
          │             │
          │   paleta    │ ──► X  (hacia la punta de la paleta,
          │             │        a lo largo del mango)
          └──────┬──────┘
                 │ mango
                 ●  sensor
       Y = Z × X  (hacia el canto, regla de la mano derecha)
```

- **X**: a lo largo del mango, apuntando hacia la paleta.
- **Z**: perpendicular a la cara, saliendo por la goma **roja**.
- **Y**: hacia el canto, completando un sistema de mano derecha.

Si el módulo no se puede montar con esos ejes, se reordenan en el firmware (`alinearEjes()` en `firmware/paleta/paleta.ino`). Las herramientas de Python y la app asumen siempre estos ejes.

## 2. Muestras crudas (placa → compu, por cable USB)

Una línea de texto por muestra, **1000 muestras por segundo**:

```
t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
```

| Campo | Unidad | Detalle |
| --- | --- | --- |
| `t_us` | microsegundos | Tiempo desde que arrancó la placa |
| `ax_g`, `ay_g`, `az_g` | g | Aceleración, rango ±16 g |
| `gx_dps`, `gy_dps`, `gz_dps` | °/s | Velocidad de giro, rango ±2000 °/s |
| `impacto` | 0 o 1 | 1 si la placa detectó un impacto en esa muestra |

Las líneas que empiezan con `#` son mensajes y se ignoran.

## 3. Archivos de sesión

- Nombre: `AAAA-MM-DD_HHMMSS_jugador_golpe.csv` (lo arma `herramientas/grabar.py`).
- Golpes válidos: `topspin_derecha`, `topspin_reves`, `empuje_derecha`, `empuje_reves`, o `libre` para juego libre.
- Se guardan en `datos/crudos/`. **No se suben a git** (pesan mucho): se comparten en la carpeta de Drive del grupo.

## 4. Interfaz de Inferencia C++ (P1 ↔ P2)

Para aislar el código de adquisición de hardware (P1) del modelo de Machine Learning de Edge Impulse (P2), la comunicación interna del ESP32 se rige estrictamente por el wrapper `firmware/paleta/ml_inference.h`.

- **Entrada (Buffer):** P1 invoca la inferencia pasando un array de **1176 floats** estáticos. Este valor está fijado por la constante `ML_BUFFER_LONGITUD_ESPERADA`, representando 196 ms de captura (196 muestras $\times$ 6 ejes IMU a 1000 Hz).
- **Salida (Struct):** P2 procesa la señal y devuelve un `PrediccionGolpe` purgado de tipos de TensorFlow:
  ```c
  typedef struct {
      const char* etiqueta;      // ej. "topspin_derecha"
      float probabilidad;        // 0.0 a 1.0
      float tiempo_inferencia_ms;
  } PrediccionGolpe;
  ```

## 5. Evento de golpe BLE (P1 ↔ P3)

Para evitar el bloqueo de interrupciones en el ESP32 causado por el parseo y concatenación de strings, el Bluetooth Low Energy transmite un **Struct de C empaquetado (Packed Struct)** binario. Ocupa solo 14 bytes y entra sobradamente en un paquete BLE estándar (MTU 20).

- **Servicio Custom:** `6e400001-b5a3-f393-e0a9-e50e24dcca9e`.
- **Característica de Notificación (Notify):** `6e400003-b5a3-f393-e0a9-e50e24dcca9e`.

### Estructura de Datos (C++ ESP32)
```c
#pragma pack(push, 1)
struct BlePayload {
    uint32_t timestamp;     // 4 bytes: ms desde el arranque del ESP32
    uint16_t numero_golpe;  // 2 bytes: contador de impactos en la sesión
    uint8_t  tipo_golpe;    // 1 byte: 0=TD, 1=TR, 2=ED, 3=ER, 4=Desconocido
    uint8_t  confianza;     // 1 byte: Probabilidad de Edge Impulse (0 a 100)
    int16_t  vel_kmh;       // 2 bytes: Velocidad tangencial estimada
    int16_t  ang_deg;       // 2 bytes: Ángulo de la cara (- cerrada, + abierta; ver abajo)
    int16_t  pico_ms;       // 2 bytes: Tiempo del pico giro vs impacto (- es antes)
}; // Total: 14 bytes
#pragma pack(pop)
```

### Signo del ángulo (`ang_deg`)

Misma convención que [`GOLPES.md`](GOLPES.md), donde están los rangos de cada golpe:

| Valor | Cara de la paleta | Golpe típico |
| --- | --- | --- |
| **0°** | Vertical, perpendicular a la mesa | — |
| **Negativo** | **Cerrada**: mira hacia la mesa | Topspin (ideal entre −35° y −10°) |
| **Positivo** | **Abierta**: mira hacia el techo | Empuje (ideal entre +25° y +50°) |

### Recepción (Web App P3)
P3 se suscribe a la característica usando la **Web Bluetooth API**. Al recibir el buffer binario, lo decodifica usando un `DataView` estándar de JavaScript en formato **Little-Endian**:
```javascript
let timestamp = dataView.getUint32(0, true);
let tipo_golpe = dataView.getUint8(6);
let vel_kmh = dataView.getInt16(8, true);
```
