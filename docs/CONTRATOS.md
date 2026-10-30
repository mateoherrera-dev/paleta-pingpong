# Contratos entre modulos

Estos formatos son lo que permite que cada uno trabaje en su parte sin esperar a los demas.
**Si alguien necesita cambiar algo de aca, lo charla con todo el grupo y lo anota en este archivo antes de tocar el codigo.**

## 1. Ejes del sensor

Todos los datos usan los mismos ejes, medidos sobre la paleta (no sobre el modulo):

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

Si el modulo no se puede montar directamente con esos ejes (por ejemplo, al montarlo en la base del pomo mirando hacia abajo), se reordenan e invierten en el firmware (`alinearEjes()` en `firmware/paleta/paleta.ino`). Las herramientas de Python y la app asumen siempre estos ejes.

## 2. Muestras crudas (placa → compu, por cable USB)

Una linea de texto por muestra, **1000 muestras por segundo**:

```
t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
```

| Campo | Unidad | Detalle |
| --- | --- | --- |
| `t_us` | microsegundos | Tiempo desde que arranco la placa |
| `ax_g`, `ay_g`, `az_g` | g | Aceleracion, rango ±16 g |
| `gx_dps`, `gy_dps`, `gz_dps` | °/s | Velocidad de giro, rango ±2000 °/s |
| `impacto` | 0 o 1 | 1 si la placa detecto un impacto en esa muestra |

Las lineas que empiezan con `#` son mensajes y se ignoran.

## 3. Archivos de sesion

- Nombre: `AAAA-MM-DD_HHMMSS_jugador_golpe.csv` (lo arma `herramientas/grabar.py`).
- Golpes validos: `topspin_derecha`, `topspin_reves`, `empuje_derecha`, `empuje_reves`, `ruido` (movimientos de descarte / not a swing: acomodar paleta, caminar, festejo), o `libre` para juego libre.
- Se guardan en `datos/crudos/`. **No se suben a git** (pesan mucho): se comparten en la carpeta de Drive del grupo.

## 4. Interfaz de Inferencia C++ (P1 ↔ P2)

Para aislar el codigo de adquisicion de hardware (P1) del modelo de Machine Learning de Edge Impulse (P2), la comunicacion interna del ESP32 se rige estrictamente por el wrapper `firmware/paleta/ml_inference.h`.

- **Entrada (Buffer):** P1 invoca la inferencia pasando un array de **1176 floats** estaticos. Este valor esta fijado por la constante `ML_BUFFER_LONGITUD_ESPERADA`, representando 196 ms de captura (196 muestras $\times$ 6 ejes IMU a 1000 Hz).
- **Salida (Struct):** P2 procesa la señal y devuelve un `PrediccionGolpe` purgado de tipos de TensorFlow:
  ```c
  typedef struct {
      const char* etiqueta;      // ej. "topspin_derecha"
      float probabilidad;        // 0.0 a 1.0
      float tiempo_inferencia_ms;
  } PrediccionGolpe;
  ```

## 5. Evento de golpe BLE (P1 ↔ P3)

Para evitar el bloqueo de interrupciones en el ESP32 causado por el parseo y concatenacion de strings, el Bluetooth Low Energy transmite un **Struct de C empaquetado (Packed Struct)** binario. Ocupa **20 bytes** (los 14 de siempre + 6 de la orientacion) y entra justo en un paquete BLE estandar: con el MTU por defecto de 23 bytes, una notificacion lleva hasta 20 de datos.

- **Servicio Custom:** `6e400001-b5a3-f393-e0a9-e50e24dcca9e`.
- **Caracteristica de Notificacion (Notify):** `6e400003-b5a3-f393-e0a9-e50e24dcca9e`.

### Estructura de Datos (C++ ESP32)
```c
#pragma pack(push, 1)
struct BlePayload {
    uint32_t timestamp;     // 4 bytes: ms desde el arranque del ESP32
    uint16_t numero_golpe;  // 2 bytes: contador de impactos en la sesion
    uint8_t  tipo_golpe;    // 1 byte: 0=TD, 1=TR, 2=ED, 3=ER, 4=Desconocido o Ruido
    uint8_t  confianza;     // 1 byte: Probabilidad de Edge Impulse (0 a 100)
    int16_t  vel_kmh;       // 2 bytes: Velocidad tangencial estimada
    int16_t  ang_deg;       // 2 bytes: Angulo de la cara (- cerrada, + abierta; ver abajo)
    int16_t  pico_ms;       // 2 bytes: Tiempo del pico giro vs impacto (- es antes)
    int16_t  q1, q2, q3;    // 6 bytes: Orientacion en el impacto, cuaternion x 32767 (ver abajo)
}; // Total: 20 bytes
#pragma pack(pop)
```

### Estimacion de velocidad tangencial (`vel_kmh`)

Se calcula como $v = \omega_{\text{swing}} \cdot L$:
- $\omega_{\text{swing}}$ es la velocidad de giro en el plano del swing obtenida por el giroscopio.
- $L$ es la distancia radial desde el plano inferior del pomo (donde apoya el sensor) hasta el centro geometrico de la cabeza de la pala (interseccion de ejes mayor y menor).
- **Protocolo de medicion:** $L$ NO debe ser una estimacion a ojo. Se mide fisicamente en la paleta del grupo con calibre o regla y se define como constante en el codigo (ej. `#define L_PALETA_M 0.262f`).

### Signo del angulo (`ang_deg`)

Misma convencion que [`GOLPES.md`](GOLPES.md), donde estan los rangos de cada golpe:

| Valor | Cara de la paleta | Golpe tipico |
| --- | --- | --- |
| **0°** | Vertical, perpendicular a la mesa | — |
| **Negativo** | **Cerrada**: mira hacia la mesa | Topspin (ideal entre −50° y −30° sobre bola neutra) |
| **Positivo** | **Abierta**: mira hacia el techo | Empuje (ideal entre +25° y +50°) |

### Orientacion en el impacto (`q1`, `q2`, `q3`)

Para el visor 3D de la app (acordado entre los tres el 30/10). Es la orientacion completa de la paleta en la muestra del impacto, la misma de la que sale `ang_deg` (`angulo_en_impacto()` en `firmware/paleta/angulo.cpp`).

- **Que es:** un cuaternion unitario (q0, q1, q2, q3), q0 la parte real, que **lleva los vectores de la paleta al mundo**: v_mundo = q · v_paleta · q*. Es la misma convencion que `Object3D.quaternion` de Three.js.
- **Ejes de la paleta:** los de la seccion 1 (X a lo largo del mango hacia la paleta, Z saliendo por la goma roja, Y = Z × X).
- **Ejes del mundo:** **Z para arriba** (lo fija la gravedad). X es la direccion horizontal hacia donde apuntaba el mango al prender la paleta, e Y = Z × X.
- **Rumbo (giro alrededor de Z del mundo):** el sensor no tiene magnetometro, asi que no hay norte. Se mide desde el arranque integrando el giroscopio y **se corre con el tiempo** (unos grados por minuto, menos si la paleta arranco quieta y se calibro el giroscopio). La app no tiene que confiar en el rumbo: conviene ignorarlo o ponerlo en cero en cada golpe para mostrar.
- **Como se manda:** solo q1, q2 y q3, multiplicados por 32767 y redondeados a `int16`. El firmware elige el signo para que q0 ≥ 0 (q y −q son la misma orientacion), asi la app lo reconstruye:
  q0 = √(1 − q1² − q2² − q3²), con q1..q3 ya divididos por 32767 (si por redondeo da negativo adentro de la raiz, usar 0).
- **Caso de prueba:** paleta acostada con la goma roja para arriba y el mango apuntando hacia donde apuntaba al arrancar → q = (1, 0, 0, 0), o sea q1 = q2 = q3 = 0.
- **Three.js usa Y para arriba.** Si el modelo 3D se arma con nuestros ejes rotados a los de Three.js (x → x, z → y, y → −z), el cuaternion para Three.js es `(x, y, z, w) = (q1, q3, −q2, q0)`.
- **Calibracion del giroscopio:** al arrancar, el firmware promedia 1 s de giroscopio con la paleta quieta y lo resta en todo lo que manda (tambien en el CSV de `grabar.py`). Si la paleta se movio, avisa por serie y no calibra.

### Recepcion (Web App P3)
P3 se suscribe a la caracteristica usando la **Web Bluetooth API**. Al recibir el buffer binario, lo decodifica usando un `DataView` estandar de JavaScript en formato **Little-Endian**:
```javascript
let timestamp = dataView.getUint32(0, true);
let tipo_golpe = dataView.getUint8(6);
let vel_kmh = dataView.getInt16(8, true);
// solo si llegaron 20 bytes (el firmware viejo manda 14):
let q1 = dataView.getInt16(14, true) / 32767;
let q2 = dataView.getInt16(16, true) / 32767;
let q3 = dataView.getInt16(18, true) / 32767;
let q0 = Math.sqrt(Math.max(0, 1 - q1 * q1 - q2 * q2 - q3 * q3));
```

**Compatibilidad:** los primeros 14 bytes no cambian de lugar. La app acepta mensajes de **14 o 20 bytes** segun `byteLength`: con 14 no hay orientacion (como hasta el 30/10) y con 20 si. Asi el firmware y la app se pueden actualizar por separado.
