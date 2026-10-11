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
5. `ruido`

## 4. Protocolo deliberado para la clase "No golpe" (ruido / not_a_swing)

Para que el modelo aprenda a rechazar perturbaciones reales sin confundirlas con tiros, se capturan deliberadamente cuatro tipos de movimientos dinamicos que no son tiros:

1. **Swings al aire sin pelota (Falsos swings):**
   - Realizar el gesto tecnico completo de drive o reves pero al aire, sin impactar la bola.
   - *Objetivo:* Enseña a la red a no predecir un golpe si falta el transitorio de desaceleracion brusco del choque de la pelota.

2. **Rebotes de control y malabares:**
   - Hacer picar la pelota suavemente hacia arriba sobre la goma de forma continua.
   - *Objetivo:* Enseña a la red que un impacto vertical suave sin aceleracion angular previa ($\omega \approx 0$) no es un golpe de ataque ni de empuje.

3. **Manipulacion de la paleta y reacomodo de grip:**
   - Pasarse la paleta de mano, rotarla entre los dedos, secarse el sudor en la mesa o acomodar la postura de espera activa (pequeños saltos y balanceo de muñeca).
   - *Objetivo:* Evita disparos de inferencia mientras el punto no esta en juego.

4. **Caminata y recogida de pelotas:**
   - Caminar por la sala con la paleta en la mano y agacharse a juntar pelotas del piso.
   - *Objetivo:* Filtra las aceleraciones corporales de baja frecuencia producidas por el paso del jugador.

### Proporcion y balance en el Dataset
- **Tamaño relativo:** La clase `ruido` debe representar entre el **20 % y 25 %** del total de muestras del dataset. Para ~200 golpes validos (50 por cada uno de los 4 tipos), se recolectan entre **50 y 60 ventanas deliberadas** de no golpes.
- **Segmentacion identica:** Estas muestras deben recortarse usando exactamente la misma ventana temporal de 196 muestras (~196 ms, 120 antes del centro + 76 despues) que los golpes validos para que los tensores de entrada a Edge Impulse tengan dimensiones identicas (1176 floats).
