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

## 4. Evento de golpe (placa → celular, por Bluetooth)

- Servicio: **Nordic UART** (`6e400001-b5a3-f393-e0a9-e50e24dcca9e`).
- La placa notifica por la característica `6e400003-b5a3-f393-e0a9-e50e24dcca9e`.
- Nombre de la placa: empieza con `Paleta` (por ejemplo `Paleta-01`).
- Un evento por golpe, una línea de texto terminada en `\n`:

```
n,golpe,conf,vel_kmh,ang_deg,pico_ms
23,TD,91,46,28,-40
```

| Campo | Detalle |
| --- | --- |
| `n` | Número de golpe en la sesión |
| `golpe` | `TD` topspin derecha · `TR` topspin revés · `ED` empuje derecha · `ER` empuje revés · `??` no reconocido |
| `conf` | Confianza del modelo, 0 a 100 |
| `vel_kmh` | Velocidad estimada de la paleta, km/h. `-` si todavía no se calcula |
| `ang_deg` | Ángulo de la cara en el impacto. **Positivo = cerrada** (mirando hacia la mesa), negativo = abierta. `-` si no se calcula |
| `pico_ms` | Momento del pico de giro respecto del impacto. **Negativo = el pico fue antes** (frenó antes de pegar). `-` si no se calcula |

El formato es corto a propósito: entra en un solo paquete Bluetooth (20 bytes) aunque el celular no negocie paquetes más grandes.
