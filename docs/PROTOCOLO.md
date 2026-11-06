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

## 5. Prueba ciega con jugadores de afuera (hito del 6/11)

Mide el acierto del modelo con gente que **no esta en el entrenamiento** (el modelo v5 ya tiene a p1, p2 y p3, asi que ninguno de los tres sirve). El hito es **80 % o mas**. No es dataset: los archivos van a `datos/pruebas` del Drive, no a `crudos`.

### Antes de empezar
1. **Placa:** con el firmware del PR #29 (filtro: no manda por BLE lo que el modelo llama ruido ni lo que gira a menos de 300 °/s). Por el OTG a la compu, con el cable pegado al antebrazo.
2. **Arranque:** al enchufarla, la paleta tiene que quedar **quieta 1 s** para calibrar el giroscopio. En la serie tiene que salir `Giroscopo calibrado`; si dice que se movio, desenchufar y volver a enchufar sin tocarla.
3. **App:** en el celular, Chrome en Android (en iPhone, Bluefy), con Bluetooth, ubicacion y el permiso "Dispositivos cercanos" de Chrome. Abrir https://mateoherrera-dev.github.io/paleta-pingpong/app/ y **recargarla**. Con datos moviles puede no cargar el visor 3D: usar wifi (la app igual anda sin el visor).
4. **Conectar** la app ("Conectar paleta" → "Paleta") recien con `grabar.py` abierto (paso siguiente). En la serie sale `se suscribio a los golpes`. Como funciona la app y problemas al conectar: [`app/README.md`](../app/README.md).

### Grabar: una sola vez para toda la prueba
Desde `herramientas/`, en PowerShell (cambiar COM7 por el puerto que marque `python grabar.py --listar`):

```
$env:PYTHONIOENCODING = 'utf-8'; python -u grabar.py --puerto COM7 --jugador externos --golpe libre --carpeta ..\datos\pruebas | Tee-Object -FilePath ..\datos\pruebas\log_externos.txt
```

- **No cortar `grabar.py` entre jugadores.** Cerrar y abrir el puerto **resetea la placa**: se corta el Bluetooth (hay que reconectar la app) y vuelve a calibrar el giroscopio (la paleta tiene que estar quieta en ese momento).
- **El log es obligatorio.** Las lineas `# Golpe N: TD 100 % ...` y `# Descartado: ruido 100 % ...` solo salen por pantalla, no van al CSV. Los descartados **no aparecen en la app**: sin el log no se puede contar un golpe real que el modelo llamo ruido.
- `PYTHONIOENCODING` hace falta en Windows: sin eso `--listar` se rompe con la flecha.

### Con cada jugador
1. **Agarre fijo (CONTRATOS 1.1):** derecha con la **goma negra**, reves con la **roja**. Explicarselo antes; al reves, el modelo falla.
2. **10 golpes de cada tipo, en este orden:** TD, ED, TR, ER. Un compañero tira las pelotas en la mesa, de a una.
3. **Anotar en papel, por tanda:** jugador (numero, sin apellido), golpe pedido, hora de inicio y fin (la del reloj de la compu) y cuantas pelotas no toco o le dio con el canto.

| Jugador | Golpe | Inicio | Fin | No toco / canto |
| --- | --- | --- | --- | --- |
| 1 | TD | 15:02 | 15:04 | 1 |

### Como se cuenta
- Para cada tanda, cada impacto del log es un acierto (`# Golpe` con el tipo pedido), un error de tipo (`# Golpe` con otro tipo) o un error de ruido (`# Descartado: ruido` con giro de mas de 300 °/s). Los descartados con menos de 300 °/s ("swing muy lento") suelen ser manipular la paleta: no cuentan.
- Acierto = aciertos / golpes que tocaron la pelota. Por golpe y en total.

### Al terminar
- Ctrl+C en `grabar.py` (una vez; el CSV se guarda igual).
- Subir al Drive (`paleta-pingpong · datos/pruebas`) el CSV, `log_externos.txt` y una foto o copia de las anotaciones.

### Lo que ya se vio el 6/11 con p1 y p3 (modelo v5)
- Cuando acierta, acierta con 100 % de certeza. Los errores son golpes reales rapidos (540-820 °/s) que llama **ruido** (el filtro los tira) y el **topspin de reves**, que lo confunde con empuje de reves (p1: 2/5, p3: 1/10).
- En los empujes de derecha el firmware a veces elige la cara roja y el angulo sale con el signo cambiado (3 de 10); la app ya lo corrige con el cuaternion.
- Detalle por tanda en `datos/pruebas/NOTAS_p3_2026-11-06.md` (Drive) y en el `LEEME.md` de esa carpeta.
