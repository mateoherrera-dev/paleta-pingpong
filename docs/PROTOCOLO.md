# Protocolo de Captura de Datos

Este documento define el estándar de recolección de datos para el entrenamiento del modelo de reconocimiento de golpes de ping pong.

## 1. Herramientas y Nomenclatura
Las capturas deben realizarse utilizando el script `herramientas/grabar.py`, que se encarga automáticamente de recolectar los datos por el puerto serie y guardarlos.

Los archivos generados se guardarán en la carpeta `datos/crudos/` siguiendo esta nomenclatura automática:
`[YYYY-MM-DD_HHMMSS]_[jugador]_[golpe].csv`

**Ejemplo:** `2026-10-04_153000_tomas_topspin_derecha.csv`

Para visualizar los datos y verificar la integridad de la señal, utilizar el script interactivo `herramientas/ver.py`.

## 2. Protocolo de Captura en Mesa
Para garantizar que el modelo aprenda aislando el gesto técnico puro (y no ruido de la mesa o peloteos impredecibles), se deben seguir estas reglas durante la captura:

- **No se realiza peloteo abierto.** Toda pelota debe venir de un lanzamiento (multiball).
- El alimentador lanzará **series de 10 a 20 pelotas** con un ritmo y velocidad constante.
- El jugador debe realizar el golpe y retornar brevemente a una **posición neutra** entre cada pelota.
- El script `grabar.py` reportará los impactos procesados en tiempo real. 

## 3. Orden de los Golpes
Al utilizar `--golpe` en `grabar.py`, los nombres válidos son los que define el sistema en `senal.py`. El orden de grabación en la mesa debe ser siempre el siguiente para optimizar tiempos:

1. `topspin_derecha`
2. `empuje_derecha`
3. `topspin_reves`
4. `empuje_reves`
