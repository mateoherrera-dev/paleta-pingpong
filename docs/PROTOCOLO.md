# Protocolo de Captura de Datos

Este documento define el estandar de recoleccion de datos para el entrenamiento del modelo de reconocimiento de golpes de ping pong.

## 1. Herramientas y Nomenclatura
Las capturas deben realizarse utilizando el script `herramientas/grabar.py`, que se encarga automaticamente de recolectar los datos por el puerto serie y guardarlos.

Los archivos generados se guardaran en la carpeta `datos/crudos/` siguiendo esta nomenclatura automatica:
`[YYYY-MM-DD_HHMMSS]_[jugador]_[golpe].csv`

**Ejemplo:** `2026-10-04_153000_tomas_topspin_derecha.csv`

Para visualizar los datos y verificar la integridad de la señal, utilizar el script interactivo `herramientas/ver.py`.

## 2. Protocolo de Captura en Mesa (Autopique / Self-feed)
Para garantizar la maxima consistencia y repetibilidad del dataset (evitando la variabilidad e imprecision de un lanzador externo), se utiliza el metodo de **autopique con la mano libre**:

- **No se realiza peloteo abierto ni alimentacion externa erratica:** El propio jugador pica la pelota sobre la mesa y ejecuta el tiro sobre bola viva neutra (sin efecto de corte entrante).
- **Regla critica con el trigger de Jerk:** El jugador debe picar la pelota **exclusivamente con la mano libre**, dejarla rebotar en la mesa y entrarle con el swing. **Queda terminantemente prohibido picar la pelota haciendola rebotar contra la goma de la paleta antes de tirar**, ya que ese contacto previo generaria un falso transitorio de aceleracion que congelaria la ventana del buffer antes del swing real.
- **Posicion de espera neutra:** La mano armada que sostiene la paleta debe permanecer quieta en posicion de espera durante el bote de la pelota para no introducir vibraciones espurias previas al golpe.
- **Tandas continuas de 36 pelotas en rafaga:**
  - Se colocan las 36 pelotas en una caja o canasto junto a la mesa.
  - Se inicia la grabacion continua con `grabar.py` identificando la tanda completa en el argumento `--golpe` (ej. `--golpe topspin_derecha`).
  - El jugador tira las 36 pelotas seguidas con autopique a ritmo parejo (un tiro cada 1.5 a 2 segundos). La tanda completa se ejecuta en menos de 90 segundos.
  - Al vaciar el canasto, se corta la grabacion con `Ctrl+C`.
  - Entre los 3 integrantes juntan las 36 pelotas en ~2 minutos y se procede a la siguiente tanda o cambio de golpe.
  - Con este metodo continuo, capturar ~150 golpes (4 tandas de 36 con juntada incluida) insume menos de 20 minutos y preserva la biomecanica fluida del jugador.

### Las 3 reglas de oro para tirar las 36 pelotas seguidas
1. **Dejar 1 a 2 segundos entre tiro y tiro:** No tirar en modo ametralladora. Realizar una pequeña pausa entre cada golpe para que la paleta desacelere y vuelva a posicion neutra. Asi cada impacto queda como una isla aislada en la señal.
2. **Si se pifia una pelota, no frenar la grabacion:** Si un tiro pega en el canto o sale defectuoso, continuar tirando las restantes sin cortar. Quien opera la consola anota en papel (ej. "Tanda 1, tiro 12 descartar") o se descarta luego por inspeccion de curva. Con 36 pelotas por tanda, aun descartando 3 o 4 pifias quedan mas de 30 muestras excelentes.
3. **No golpear la mesa ni la paleta contra nada entre tiros:** En las tandas de golpes tecnicos, evitar que la paleta choque contra la mesa o contra la mano libre entre pelotas para no introducir picos falsos en el archivo continuo. 

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
