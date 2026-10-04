# Protocolo de Captura de Datos

Este documento define el estándar de recolección de datos para el entrenamiento del modelo de reconocimiento de golpes de ping pong en el proyecto de la paleta sensada.

## 1. Nomenclatura de Archivos
Todos los archivos de captura crudos deben exportarse en formato CSV siguiendo estrictamente esta nomenclatura:

`[sujeto]_[golpe]_[sesion].csv`

**Ejemplos:** 
- `tomas_TD_01.csv`
- `jugador1_TR_02.csv`

* **sujeto:** Nombre del jugador en minúsculas y sin espacios (ej. `tomas`, `p1`).
* **golpe:** Acrónimo del tipo de golpe (ver sección 3).
* **sesion:** Número secuencial de la ráfaga de captura a dos dígitos (ej. `01`, `02`).

## 2. Protocolo de Captura en Mesa
Para garantizar que el modelo aprenda aislando el gesto técnico puro (y no ruido de la mesa o peloteos impredecibles), se deben seguir estas reglas durante la captura:

- **No se realiza peloteo abierto.** Toda pelota debe venir de un lanzamiento (multiball).
- El alimentador lanzará **series de 10 a 20 pelotas** con un ritmo y velocidad constante.
- El jugador debe realizar el golpe y retornar brevemente a una **posición neutra** entre cada pelota.
- Si una pelota de la ráfaga se impacta mal de forma notoria, se anota el tiempo o se descarta la ráfaga entera (o se recorta a posteriori).

## 3. Orden de los Golpes
Para minimizar el tiempo perdido en la mesa por cambios de posición y estandarizar el proceso, las sesiones de captura seguirán siempre este orden exacto:

1. **TD** - Topspin de derecha
2. **ED** - Empuje / Corte de derecha
3. **TR** - Topspin de revés
4. **ER** - Empuje / Corte de revés
