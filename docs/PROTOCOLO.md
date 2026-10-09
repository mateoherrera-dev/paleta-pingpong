# Protocolo de Captura de Datos

Este documento define el estandar de recoleccion de datos para el entrenamiento del modelo de reconocimiento de golpes de ping pong.

## 1. Herramientas y Nomenclatura
Las capturas deben realizarse utilizando el script `herramientas/grabar.py`, que se encarga automaticamente de recolectar los datos por el puerto serie y guardarlos.

Los archivos generados se guardaran en la carpeta `datos/crudos/` siguiendo esta nomenclatura automatica:
`[YYYY-MM-DD_HHMMSS]_[jugador]_[golpe].csv`

**Ejemplo:** `2026-10-04_153000_tomas_topspin_derecha.csv`

Para visualizar los datos y verificar la integridad de la señal, utilizar el script interactivo `herramientas/ver.py`.

## 2. Protocolo de Captura en Mesa
Para garantizar que el modelo aprenda aislando el gesto tecnico puro (y no ruido de la mesa o peloteos impredecibles), se deben seguir estas reglas durante la captura:

- **No se realiza peloteo abierto.** Toda pelota debe venir de un lanzamiento (multiball).
- El alimentador lanzara **series de 10 a 20 pelotas** con un ritmo y velocidad constante.
- El jugador debe realizar el golpe y retornar brevemente a una **posicion neutra** entre cada pelota.
- El script `grabar.py` reportara los impactos procesados en tiempo real. 

## 3. Orden de los Golpes
Al utilizar `--golpe` en `grabar.py`, los nombres validos son los que define el sistema en `senal.py`. El orden de grabacion en la mesa debe ser siempre el siguiente para optimizar tiempos:

1. `topspin_derecha`
2. `empuje_derecha`
3. `topspin_reves`
4. `empuje_reves`
