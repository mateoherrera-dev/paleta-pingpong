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

## 5. Validacion ciega con jugadores externos (clase 5, 6/11)

Mide si el modelo de la placa reconoce los golpes de gente que nunca vio (hito del PLAN: **80 % o mas**). Estas tandas **son solo para validar**: no se suben a Edge Impulse ni se entrena con ellas, si no el numero deja de valer. Por eso van a `datos/validacion/` y no a `datos/crudos/` (`segmentar.py` lee `datos/crudos/`).

- **Firmware:** la paleta tiene que tener el modelo cargado (el de `main`): por cada impacto la placa imprime `# Golpe N: TD 87 % ...`. `grabar.py` lo guarda en un `_placa.txt` al lado del CSV.
- **Jugadores:** de 3 a 5 personas ajenas al proyecto. En los archivos van como `e1`, `e2`, ... (sin nombres). En `NOTAS_externos.md` se anota de cada uno solo el nivel (nunca jugo / juega a veces / federado) y si es diestro o zurdo.
- **Tandas de 12 pelotas por golpe**, mismo orden que la seccion 3 (sin la de ruido): 4 tandas y 48 tiros por persona, unos 10 minutos con la juntada. Mismo autopique y las 3 reglas de oro de la seccion 2.
- **Antes de cada tanda** se le muestra el golpe una vez (no se le corrige la tecnica: se mide como le pega una persona cualquiera). Si no sabe hacer un golpe (por ejemplo el topspin de reves), se saltea esa tanda y se anota.
- **No mirar la app mientras tira**, para no corregirlo segun lo que dice el modelo.

```
python grabar.py --puerto COM7 --jugador e1 --golpe topspin_derecha --carpeta ../datos/validacion
python grabar.py --puerto COM7 --jugador e1 --golpe empuje_derecha --carpeta ../datos/validacion
python grabar.py --puerto COM7 --jugador e1 --golpe topspin_reves --carpeta ../datos/validacion
python grabar.py --puerto COM7 --jugador e1 --golpe empuje_reves --carpeta ../datos/validacion
```

**Descartes:** se anotan en `datos/validacion/NOTAS_externos.md` con la misma tabla que `crudos/NOTAS.md` (el numero es el contador de impactos de `grabar.py`). Se descarta lo que no fue el golpe pedido (pifia, paleta contra la mesa, un golpe sin querer); **la pelota que va a la red o afuera NO se descarta** si el golpe fue el pedido, porque igual es el golpe que el modelo tiene que reconocer.

```
| Archivo | Impacto | Segundo | t_us | Motivo |
| --- | --- | --- | --- | --- |
| `2026-11-06_150000_e1_topspin_derecha.csv` | 4 | | | Le pego al canto (no es un topspin) |
```

**Resultado** (desde `herramientas/`, como los otros scripts):

```
python validar.py
python validar.py --confianza-min 60
```

Muestra los aciertos de cada tanda, la matriz de confusion por jugador y la total, y si se llega al 80 %. Un golpe que el modelo llama `ruido` cuenta como error. Con el filtro del PR #29 en la placa, lo que sale como `# Descartado` no le llega a la app: cuenta como `ruido` o como `lento` (giro maximo < 300 °/s), los dos error. Con `--confianza-min` los golpes por debajo de esa certeza cuentan como `dudoso` (tambien error): sirve para elegir el umbral de confianza de la app.
