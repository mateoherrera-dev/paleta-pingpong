# Plan de trabajo

**Condiciones:** somos 3. Se trabaja de forma presencial los viernes de 9 a 18 y de forma asincronica durante la semana (desarrollo de software, modelado 3D, analisis de datos y simulaciones). P2 tiene disponibilidad presencial los viernes exclusivamente en el bloque de la tarde (14:00 a 18:00), por lo que la mañana tecnica (9:00 a 13:00) queda a cargo de P1 + P3 (con P3 como suplente y apoyo de hardware).

**Calendario:** el MVP tiene que estar terminado el **viernes 13/11**. Despues viene la fase 2, hasta la entrega final.

| Clase | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Fecha | 9/10 | 16/10 | 23/10 | 30/10 | 6/11 | **13/11 · MVP** |

No hay un viernes de colchon al final. El margen sale de dos lados: el bloque de cierre de 16:30 a 18:00 de cada viernes, y el 13/11, que esta pensado para cerrar y arreglar, no para agregar cosas.

**Objetivo del MVP:** alguien pega un golpe y el celular muestra **que golpe fue, con que angulo pego la paleta y la velocidad de swing estimada ($v = \omega \cdot r$)**, junto con un consejo tecnico.

**Definicion de terminado del MVP:**
- Reconoce 4 golpes (topspin y empuje, de derecha y de reves) con **80 % de aciertos o mas**, medido con gente que no se uso para entrenar.
- Inferencia y metricas locales en el ESP32-S3 (TinyML / Edge Impulse) enviadas por paquete BLE liviano (< 20 bytes) al impactar.
- Muestra en el celular el angulo en el impacto y si el pico de aceleracion angular ocurrio antes de la bola.
- Funciona sin cables a la compu: alimentado por powerbank en el bolsillo via USB-C.

YOLO-pose y el analisis de postura van en la **fase 2**, despues del 13/11.

---

### Diagnostico: Cuellos de botella y adaptacion

1. **El cuello de botella de la Clase 2:** En la Clase 1 no se pudo probar el sensor con la paleta y no se logro un montaje funcional. Es necesario ir hacia atras: soldar un nuevo sensor desde cero en el pomo con chicotes protegidos y rehacer el conexionado. Si el viernes 16/10 no se reorganiza la mañana tecnica (09:00 a 13:00) para resolver el montaje antes del mediodia, el equipo gastaria la tarde soldando y perderia el acceso a la mesa de ping pong, postergando la captura del Dataset v1 y retrasando el entrenamiento en Edge Impulse.
2. **La ausencia matutina de P2:** Toda actividad presencial de P2 se concentra obligatoriamente en la franja de 14:00 a 18:00. P3 acompaña activamente a P1 en el banco de hardware durante la mañana (09:00 a 13:00) para garantizar que la paleta este operativa antes del almuerzo.
3. **Aprovechamiento del trabajo asincronico:** Habilitar el trabajo remoto en computadora entre semana permite desacoplar desarrollo de software, modelado 3D y analisis de datos de las horas de laboratorio fisico.

---

## 1. Equipo y modulos

Los formatos de datos entre modulos estan fijados en [`CONTRATOS.md`](CONTRATOS.md).

| Persona | Modulos | Que hace | Suplente |
| --- | --- | --- | --- |
| **P1 · Hardware** | Firmware base | Sensor MPU-6500 por SPI a 1000 Hz (interrupciones/DMA), deteccion de impactos (trigger), emision de struct BLE (NimBLE) | P2 |
| **P2 · Datos** | Datos, Modelo + 3D | Grabacion (UART), dataset, entrenamiento Edge Impulse, modulo wrapper C++ (`ml_inference.h`), diseño e impresion de capsula (Fusion 360). Presencial 14:00 a 18:00 | P3 |
| **P3 · Tecnica** | App + UI + BLE | Contrato de payload BLE, App web (Web Bluetooth API), calculo cinematico ($v = \omega \cdot L$), angulos (Madgwick), criterios y consejos. Asistencia y suplente de hardware en mañanas | P1 |

### Reglas

- **El suplente sabe como funciona el modulo** que cubre, por si el dueño falta un viernes. P3 asiste activamente en hardware los viernes por la mañana.
- **Los tres graban datos.** La grabacion es una actividad de grupo, no del modulo de datos solo.
- **Integrar todos los viernes.** Cada viernes a la tarde se prueba de punta a punta lo que haya, aunque sea con datos simulados.
- **Los contratos no se cambian solos:** se discute entre los tres y se actualiza `CONTRATOS.md`.
- **Git:** una rama corta por tarea y PR a `main` (que esta protegida), merge cuando compile y ande. Todo pusheado antes de irse cada viernes. Detalle en [`AGENTS.md`](../AGENTS.md).

---

## 2. Nuevo esquema operativo de los viernes

Con el nuevo horario de almuerzo (13:00 a 14:00) y la disponibilidad de P2 exclusivamente por la tarde, la jornada de cada viernes se divide en dos bloques funcionales bien delimitados:

| Horario | Bloque | Integrantes | Foco principal |
| --- | --- | --- | --- |
| **09:00 – 13:00** | Mañana tecnica | **P1 + P3** | Montaje de hardware, firmware en placa, banco de pruebas y enlace BLE base. |
| **13:00 – 14:00** | Almuerzo | **Todos** | Pausa y puesta en comun del estado de la mañana. P2 se incorpora al grupo. |
| **14:00 – 16:30** | Tarde de mesa | **P1 + P2 + P3** | Ensayos en mesa de ping pong, captura masiva de datos y pruebas con paleta. |
| **16:30 – 18:00** | Integracion y cierre | **P1 + P2 + P3** | Pruebas de punta a punta, segmentacion/subida de datos y acuerdos asincronicos. |

---

## 3. Clase 0: hoy

### Organizacion (los tres, primera hora)

- [ ] Confirmar roles: P1, P2 y P3.
- [ ] **Comprar por internet** para recibir antes del 9/10: **2 modulos MPU-6500** (uno de repuesto), cables dupont hembra-hembra, cable USB-C flexible largo (2–3 m) cinta de pintor, cinta bifaz 3M VHB y cinta aisladora. Alternativa de respaldo: 2 discos piezoelectricos chicos por si el trigger por acelerometro mete ruido.
- [ ] Crear el repo en GitHub, subir estructura base y dar permisos al equipo.
- [ ] Crear la carpeta de Drive para los CSV crudos.
- [ ] **Confirmar mesa de ping pong disponible los viernes a la tarde**, red portatil, 2 paletas y minimo 20 pelotas para tiros en rafaga.
- [ ] Averiguar proveedor de impresion 3D y tiempos de entrega (impresion entre Clase 3 y 4).
- [ ] Contactar al jugador de referencia para coordinar su asistencia el viernes 30/10 (Clase 4).

### Codigo y Banco (sin sensor fisico aun)

| Quien | Tarea | Listo cuando… |
| --- | --- | --- |
| **P2** | Escribir modulo wrapper C++ (`ml_inference.h/cpp`) integrando el modelo Edge Impulse sintetico (`firmware/modelo_dummy_sintetico.zip`) | Modulo encapsulado listo con funcion `predecir_golpe()` |
| **P2** | Script receptor en Python por puerto serie (lectura a 921600 baudios) y visualizador `ver.py` | Recibe paquetes simulados a 1000 Hz sin dropping de buffers |
| **P2** | Escribir protocolo de captura (`docs/PROTOCOLO.md`): orden de tiros, estructura y metadatos de CSV | Protocolo cerrado |
| **P3** | App web base (Web Bluetooth API) desplegada en GitHub Pages | Conecta y parsea el string de prueba del contrato |
| **P3** | Definir rangos biomecanicos preliminares (angulos de impacto y velocidad tangencial) | Tabla base en `docs/` |

---

## 4. Fase 1: MVP, viernes por viernes

### Clase 1 · Viernes 9/10 · Banco inicial (Retrospectiva: sin pruebas en paleta)

**Estado alcanzado:**
- Se configuro el entorno del ESP32-S3 y se hicieron pruebas preliminares de conexion con el MPU-6500 en banco.
- **No se pudo probar el sensor con la paleta:** surgieron dificultades mecanicas y de cableado que impidieron fijarlo de forma solida y capturar impactos reales.
- El conexionado previo no resulto util para la adquisicion definitiva; es necesario ir hacia atras para soldar un nuevo sensor desde cero con chicotes limpios en el pomo y asegurar la integridad de la señal.
- **Deuda tecnica arrastrada:** El montaje fisico completo y la adquisicion real se trasladan como maxima prioridad a la mañana de la Clase 2.

---

### Trabajo asincronico previo a Clase 2 (Miercoles 14 y Jueves 15)

Aprovechando la habilitacion del trabajo remoto en computadora entre semana, se adelantan tareas de software, modelado 3D y analisis para llegar al viernes con todo listo para montar y grabar:

* **P1 (Firmware):** Dejar preparado el proyecto base en el IDE para el ESP32-S3 con el bus SPI a 1000 Hz y la logica del calculo de Jerk (`|a[k] - a[k-1]|`, resta de vectores: ver el estado al 16/10 mas abajo).
* **P2 (Datos & 3D):** Validar en su PC que `ver.py` y `segmentar.py` funcionen sin errores usando datos simulados; avanzar el modelado de la Pieza A y Pieza B en Fusion 360 con las medidas del pomo.
  - *Dato critico para Pieza B:* La placa ESP32-S3 conserva sus dos tiras de pines macho de fabrica (desoldarlas con soldador comun arriesga levantar pistas). Por ende, el espesor de la placa pasa de 2 mm planos a **8–10 mm de grosor total**. La cavidad de la vaina debe contemplar esa profundidad para cerrar con holgura.
* **P3 (App & Cinematica):** Probar el algoritmo de orientacion (Madgwick o filtro complementario) con series temporales sinteticas y dejar lista la UI de captura en la Web App. Preparar asistencia tecnica para la mañana de montaje con P1.

---

### Clase 2 · Viernes 16/10 · Montaje de Nuevo Sensor y Grabacion Masiva (Alimentacion: Cable USB-C a PC)

**Materiales a llevar:**
- Placa ESP32-S3 y modulo MPU-6500 (mas repuesto).
- Paleta de ping pong.
- Primera pieza impresa en 3D: Pieza A (Portasensor), traida por P2 si llega a tiempo.
- Cables Dupont hembra-hembra para cortar y estañar como chicotes de 4 a 5 cm (*aclaracion:* no se dispone de cables flexibles dedicados, se cortan Duponts).
- Soldador, estaño, alicate de corte al ras, pistola de silicona caliente (o cinta firme de sujecion).
- Cinta aislante o cinta de pintor (papel) para aislacion electrica (reemplazo de Kapton) y cinta bifaz 3M VHB para fijacion mecanica rigida.
- Regla metalica o calibre para medir la constante geometrica $L$.
- Cable USB-C largo (2–3 m) a PC.
- Canasto o caja con 36 pelotas de ping pong y red portatil.

| P1 | P2 (desde 14:00) | P3 |
| --- | --- | --- |
| **Mañana:** Soldadura de chicotes, montaje en pomo, enlace SPI 1000 Hz y calibracion de Jerk. **Tarde:** Monitoreo y rotacion en mesa | **Tarde:** Validacion de paquetes en `ver.py`, grabacion masiva y segmentacion | **Mañana:** Asistencia mecanica/hardware a P1, medicion de L. **Tarde:** Rotacion en mesa y control de calidad |

#### Cronograma detallado de la jornada:

* **09:00 – 11:30 (P1 + P3) · Soldadura y montaje del nuevo sensor en pomo (con o sin Pieza A):**
  - **Longitud de chicotes (4 a 5 cm):** Como la capsula del ESP32 (Pieza B) todavia no estara y la placa ira sujeta provisoriamente con cinta, no cortar cables cortos al ras de 2 cm. Dejar chicotes de 4 a 5 cm para manipular con comodidad y evitar cables tirantes.
  - **Secuencia estricta de ensamble:**
    1. Cortar pines macho del nuevo MPU-6500 al ras dejando 1 mm de muñon.
    2. Soldar los 7 chicotes de 4 a 5 cm a las pistas SPI (`VCC`, `GND`, `SCL`, `SDA`, `AD0`, `NCS`, `INT`).
    3. Aislar la cara posterior con cinta aislante o de papel (reemplazo de Kapton).
    4. **Alivio mecanico indispensable:** Aplicar una gotita de silicona caliente o una vuelta firme de cinta apretando los 7 chicotes contra el cuerpo de la plaqueta para que la rigidez del cable DuPont no haga palanca ni arranque las pistas de cobre al doblarse.
    5. **Paso por pasacables:** Si la Pieza A (Portasensor) esta disponible, pasar los extremos libres de los 7 cables a traves de los orificios de la capsula hacia afuera antes de cualquier otra union.
    6. **Contacto rigido contra la madera (clave para el Jerk):** Pegar el MPU-6500 con cinta bifaz 3M VHB directo y firme contra la base de madera (previa cinta de sacrificio), nunca flotando suelto ni sobre plastico flexible que amortigue la onda de choque. Calzar la capsula Pieza A encima.
    7. **Conexion al ESP32 (los pines macho quedan puestos):** No intentar desoldar las tiras de pines del ESP32 (se arriesga levantar pistas de cobre o dañar componentes por calor). Se eligen dos alternativas segun preferencia en el banco:
       - *Opcion A (rapida para este viernes): Fichas hembra DuPont encintadas en bloque.* Se conservan las fichas hembra en el extremo del ESP32 y se enchufan a los pines macho. Paso critico: envolver todo el conjunto de conectores y la placa con varias vueltas firmes de cinta aisladora apretada, formando un bloque solido para que la vibracion del impacto no afloje ningun pin.
       - *Opcion B (la mas robusta mecanicamente): Soldar a la patita del pin.* Pelar el cable y soldarlo directo con una gotita de estaño a la base metalica del pin macho del ESP32. Es una union rigida inmune a falsos contactos.
       *(Recordar: realizar la conexion recien cuando los cables hayan atravesado los pasacables de la Pieza A).*
  - **Verificacion de agarre (Shakehand):** Empuñar la paleta en posicion real de juego antes del pegado definitivo para asegurar que la palma, la eminencia tenar y el pulgar no choquen contra los bordes de la pieza.
  - **Plan B si la impresion 3D se demora:** La prioridad absoluta es no frenar el banco de pruebas. Si la Pieza A esta a las 09:00 se monta con capsula; si no llega a tiempo, se monta el sensor de forma provisoria (cinta de pintor + 3M VHB directo en el pomo encintado) para calibrar SPI a las 11:30 y asegurar si o si la grabacion de la tarde.
  - P3 asiste mecanicamente y mide la longitud geometrica $L$ (base del pomo a centro geometrico del sweet spot) para fijar `#define L_PALETA_M` en el firmware.

* **11:30 – 13:00 (P1 + P3) · Validacion SPI a 1000 Hz, ejes y Jerk preliminar:**
  - Levantar firmware base y verificar que no haya lecturas nulas ni cuelgues del bus SPI.
  - Comprobar convencion de `alinearEjes()`:
    - Paleta plana con goma roja hacia arriba: $a_z \approx +1\text{ g}$.
    - Paleta vertical con el pomo en la mesa y punta al techo: $a_x \approx +1\text{ g}$.
  - Calibrar umbral preliminar de Jerk: verificar disparo inmediato ante toques secos de pelota o dedos y rechazo absoluto en swings rapidos al aire.

* **13:00 – 14:00 (Todos) · Almuerzo y reunion de estado:**
  - Pausa para almuerzo. P2 se incorpora presencialmente al grupo y se realiza la puesta en comun del estado del hardware.

* **14:00 – 14:30 (P1 + P2 + P3) · Enlace de telemetria serial:**
  - Conectar la paleta armada a la PC de P2 a 921600 baudios.
  - Correr prueba de 5 minutos con `ver.py` para asegurar recepcion fluida a 1000 Hz sin desborde de bufer (*buffer overflow*).

* **14:30 – 17:00 (P1 + P2 + P3) · Grabacion masiva del Dataset v1 en mesa:**
  - Los 3 integrantes rotan continuamente en 3 roles: jugador con autopique, operador de consola de grabacion y recolector/asistente de pelotas.
  - **Tandas continuas de 36 pelotas:** Se tira el canasto entero de corrido a ritmo constante (1 tiro cada 1.5 a 2 s, < 90 s por tanda) sin frenar la PC entre tiros, siguiendo las 3 reglas de oro de [`PROTOCOLO.md`](PROTOCOLO.md) (pausa neutra entre tiros, no cortar por pifias aisladas y evitar golpes espurios).
  - Capturar los 4 golpes tecnicos: 50 golpes por tipo (Topspin Derecha, Topspin Reves, Empuje Derecha, Empuje Reves).
  - Tanda obligatoria de descarte y ruido (`ruido` / `not_a_swing`) segun [`PROTOCOLO.md`](PROTOCOLO.md#4-protocolo-deliberado-para-la-clase-no-golpe-ruido--not_a_swing) (swings al aire, malabares, acomodar grip, caminata/recogida).
  - Meta: ~600 muestras etiquetadas y balanceadas.

* **17:00 – 18:00 (P1 + P2 + P3) · Segmentacion, integridad y subida:**
  - Segmentar archivos con `segmentar.py`.
  - Chequeo de integridad de CSVs y subida a la carpeta compartida de Google Drive.

**Hito de Clase 2:** Dataset v1 completo grabado con la paleta real en mesa, segmentado y disponible en Drive para iniciar entrenamiento en Edge Impulse.
*⚠️ Criterio de Trigger (Plan B):* Si durante las grabaciones el trigger por Jerk muestra falsos positivos aislados, ajustar UMBRAL_JERK o elevar el refractario temporal antes de considerar sensores adicionales.

#### Estado al 16/10 a las 12:00 (P1)

**Hecho a la mañana** (PR #17, rama `firmware-jerk-pomo`):
- **Jerk** = `|a[k] - a[k-1]|` (resta de vectores) con `UMBRAL_JERK_G = 1.5` en `paleta.ino`, el mismo calculo en `senal.py` y `ver.py`. No se usa la resta de modulos `|a[k]| - |a[k-1]|`: probada, la prueba de orientacion falla, `ejemplo.py` no detecta golpes y en toques reales detecta 1 de 3 (si el choque vibra de costado respecto de la aceleracion del swing, el modulo casi no cambia).
- **Umbral medido** con el sensor en el pomo: swings al aire hasta 1141 °/s → Jerk de 0,2 a 1,02 g; pelota cayendo desde 30 cm → 1,38 a 6,3 g; toques con el dedo → 0,4 a 0,9 g (no se distinguen de acomodar la paleta, no sirven de criterio); apoyar la paleta en la mesa → 3,5 a 23 g (choques reales: para eso esta la clase `ruido`). **`segmentar.py` corta con la columna `impacto` de la placa**, asi que el umbral define las ventanas.
- **Montaje provisorio** (la Pieza A no habia llegado): el modulo de la clase 1 pegado con VHB en la base del pomo, con los dupont de 20 cm. Sus offsets (0.033 / -0.012 / 0.460 g) y sus ejes (`x = -mz; y = my; z = mx`, chip hacia afuera) quedaron en `paleta.ino`.
- **Herramientas nuevas:** `calibrar.py` (offset del acelerometro con 6 posiciones quietas) y `ejes.py` (cuerpo de `alinearEjes()` con 3 posiciones). Uso en el README.
- **`L_PALETA_M = 0.18`** (base del pomo → centro de la cabeza, medido con regla).
- **USB por el conector OTG** (USB nativo, `USB CDC On Boot: Enabled`). Por el TTL el chip CH340 pierde 15 a 24 muestras cada 30 s con el cable largo (y a veces pega dos lineas); por el OTG, con el mismo cable, 0. Un hueco dentro de un golpe deforma la ventana de 196 muestras. `grabar.py` ahora muestra las perdidas en vivo, descarta las lineas pegadas y tiene `--segundos`.

**En curso:** llego la Pieza A. Se suelda el MPU de repuesto con chicotes de 4-5 cm y se monta en el pomo.

**Pendiente para hoy:**
1. Con el modulo nuevo, en este orden: `OFFSET_A*_G` en 0 y `alinearEjes()` sin cambios (`x = mx; y = my; z = mz`) → grabar 6 posiciones → `calibrar.py` → pegar los offsets → grabar 3 posiciones → `ejes.py` → pegar `alinearEjes()` → verificar (acostada roja arriba `az ≈ +1 g`, parada punta arriba `ax ≈ +1 g`). Los pines no cambian.
2. 14:00: prueba de 5 min por el OTG: `python grabar.py --puerto COMx --jugador prueba5min --golpe libre --segundos 300` (el COM lo dice `--listar`). Tiene que terminar con 0 perdidas.
3. 14:30: grabacion masiva. En la primera tanda de 36 pelotas se tienen que marcar 36 impactos; si no, ajustar `UMBRAL_JERK_G`.
4. 17:00: `segmentar.py` y Drive. Las grabaciones de prueba de la mañana (`ejes`, `toques`, `swings`, `prueba*`) no van al dataset.

**Abierto:** la rama `firmware-angulo` de P3 (el angulo en C++ para el firmware) no tiene PR todavia; `cinematica.py` tiene `SENSOR_A_CENTRO_M = 0.09`, que era con el sensor en el cuello (en el pomo es 0,18).

---

### Cronograma reestructurado hacia el MVP (Clases 3 a 6)

Aprovechando que entre semana se trabaja en desarrollo en computadora, el ciclo se apoya en tres tiempos:

```
[Semana: Asincronico]      --> Codigo, entrenamiento ML, modelado 3D, Web App
[Viernes Mañana (P1+P3)]   --> Banco de hardware, electronica, BLE
[Viernes Tarde (P1+P2+P3)] --> Ensayos en mesa, captura con usuarios, integracion
```

### Clase 3 · Viernes 23/10 · Despliegue TinyML y Pase a Inalambrico (Alimentacion: Powerbank en bolsillo)
**Materiales a llevar:** Paleta ensamblada provisional, Powerbank de bolsillo, cable USB-C estandar (bolsillo a paleta), celular de prueba para P3.

* **Semana previa (Asincronica):**
  - **P2:** Entrena modelo en Edge Impulse con Dataset v1, optimiza cuantizacion a `int8`, exporta libreria C++ y genera `ml_inference.h/cpp`.
  - **P2:** Finaliza modelado 3D en Fusion 360 y envia a imprimir piezas (Pieza A y Pieza B).
  - **P3:** Implementa parser del struct BLE de 14 bytes (`BlePayload`) y la interfaz visual en la Web App.

* **Viernes 23/10 · Mañana (09:00 – 13:00 · P1 + P3):**
  - Pasar alimentacion a Powerbank via cable USB-C (verificar que no corte por bajo consumo).
  - Levantar stack NimBLE en ESP32-S3 y emitir struct de prediccion al detectar impacto.

* **Viernes 23/10 · Tarde (14:00 – 18:00 · P1 + P2 + P3):**
  - P2 integra el modelo real en el firmware y enlaza Web App por BLE.
  - Ensayos en mesa con 3 a 5 compañeros externos para medir precision en vivo fuera del dataset de entrenamiento.
  - **Hito:** Precision medida en hardware real ($\ge 80\%$ avanza a integracion final; $60-80\%$ reentrenamiento; $< 60\%$ reducir alcance a 3 golpes).

#### Estado al 23/10 a las 11:00 (P1)

**El dataset v1 no se grabo el 16/10.** Hoy a la mañana se armo la paleta y a la tarde se graba el dataset. Propuesta (a confirmar entre los tres): P2 entrena en Edge Impulse durante la semana y el modelo real, el powerbank y NimBLE pasan a la clase 4.

**Hecho a la mañana** (PR de la rama `firmware-modulo-nuevo`):
- **MPU de repuesto** soldado con chicotes y pegado con VHB en la base del pomo, adentro de la **Pieza A** (encastra bien). Se le saco la camara a la placa (no se usa, y la placa queda mas finita).
- **Calibrado** con `calibrar.py`: offset +0,028 / -0,002 / +0,264 g. **Su eje Z tambien viene corrido** (+0,26 g; el modulo de la clase 1 tenia +0,46; la hoja de datos dice ±0,08): parece del lote, hay que calibrar cada modulo.
- **Ejes** con `ejes.py`: `x = -mz; y = my; z = mx` (chip hacia afuera, igual que el provisorio).
- **Umbral de Jerk bajado a 1,0 g**: pelota desde 30 cm → 1,28 a 18,5 g; swings al aire → 0,06 a 0,17 g. Con el modulo firme los swings casi no dan Jerk (con los dupont colgando llegaban a 1,02 g).
- `grabar.py --carpeta ../datos/pruebas` para las pruebas: `datos/crudos/` queda solo para el dataset (`segmentar.py` procesa todo lo que hay ahi).

**Pieza B: la primera impresion no entro.** Mateo hizo el rediseño en `hardware/CAPSULA.md` (PR #21): interior de 31 × 21 mm y ranura de 26 × 13 mm que deja a la vista los dos USB-C (se usa el OTG). Mientras tanto la placa va sujeta con cinta. Dos cosas de hoy que cambian ese documento:
- **Se le saco la camara** a la placa: queda mas finita que los 18,1 mm que se midieron con camara.
- **Los chicotes de 4-5 cm con dupont no alcanzan** para el armado en la Pieza B: GND, G21 (NCS) y G14 (AD0) estan del lado de los USB-C, a unos 45-50 mm de la punta de la antena. Hay que rehacerlos con el largo de `CAPSULA.md` (35 mm + la distancia del pin a la punta de la antena).

**Pendiente hoy:** 14:00 prueba de 5 min (`grabar.py --puerto COM7 --jugador prueba5min --golpe libre --segundos 300 --carpeta ../datos/pruebas`, el COM lo dice `--listar`); 14:30 grabacion masiva (en la primera tanda de 36 se tienen que marcar 36 impactos); 17:00 `segmentar.py` y Drive.

#### Estado al 23/10 a las 15:45 (P1)

**Dataset v1 grabado y en el Drive** (`paleta-pingpong · datos`): **343 ventanas validas** en `segmentados/`, todas de 196 muestras y sin huecos. Los descartes de cada tanda (red, afuera, golpes sin querer) estan en `segmentados_descartados/` y anotados en `crudos/NOTAS.md`.

| Clase | Validas | Quien |
| --- | --- | --- |
| topspin_derecha | 62 | p2 + p1 |
| topspin_reves | 68 | p2 + p1 |
| empuje_derecha | 78 | p1 + p2 |
| empuje_reves | 63 | p1 + p2 |
| ruido | 72 | p1 + p2 |

- A la mañana cada golpe lo grabo una sola persona (topspins p2, empujes p1): el modelo podia aprender quien pega y no que golpe. A la tarde se grabaron las **tandas cruzadas** y ahora los 4 golpes tienen a p1 y a p2.
- **Para P2:** ya se puede entrenar con las 343. Los swings al aire y la caminata casi no marcan impactos, asi que en `ruido` casi todo es rebotes y golpes contra la mesa (ver `NOTAS.md`).
- **Falta:** las tandas de Mateo (p3) con los 4 golpes, para despues.
- **El USB se corta seguido** (~0,5 s, hasta 4 veces por tanda, a veces con la paleta quieta). `grabar.py` ahora se reconecta solo, pero en el empuje de reves de p2 dos cortes cayeron en medio de un swing y esos golpes se perdieron. Hay que revisar el cable y el conector OTG.

---

### Clase 4 · Viernes 30/10 · Integracion Total y Ensamble Definitivo
**Materiales a llevar:** Piezas impresas en 3D (Capsula y Capuchon traidas por P2), masilla/adhesivo removible, herramientas menores para ensamble.

* **Semana previa (Asincronica):**
  - P2 retira las piezas impresas en 3D y verifica tolerancias mecanicas.
  - P3 integra feedback heuristico en tiempo real en la Web App.
  - P1 prepara el codigo de firmware definitivo unificando adquisicion, filtro de orientacion, inferencia y BLE.

* **Viernes 30/10 · Mañana (09:00 – 13:00 · P1 + P3):**
  - Calce en seco de Pieza A (Portasensor) abrazando el pomo de madera.
  - Verificar paso holgado de chicotes internos hacia Pieza B (vaina ESP32).
  - Encastrar Pieza B sobre Pieza A y comprobar alivio y acceso del conector USB-C.

* **Viernes 30/10 · Tarde (14:00 – 18:00 · P1 + P2 + P3):**
  - Prueba de humo de punta a punta con la paleta 100 % armada en su carcasa final.
  - 20 golpes de cada tipo entre los 3 integrantes para chequear balance de inercia y robustez mecanica.
  - **Hito:** Paleta armada en carcasa definitiva, transmitiendo metricas a celular sin cables a PC.

---

### Clase 5 · Viernes 6/11 · Validacion Ciega y Congelamiento
**Materiales a llevar:** Hardware 100 % ensamblado y funcional, red y pelotas para las pruebas ciegas.

* **Semana previa (Asincronica):**
  - P2 ajusta umbrales de confianza en inferencia para descartar tiros dudosos.
  - P3 pule logica del modo tutorial y sintetizador de voz en la Web App.

* **Viernes 6/11 · Mañana (09:00 – 13:00 · P1 + P3):**
  - Ajuste fino de umbrales de trigger de Jerk para eliminar cualquier falso positivo residual por roces o movimientos previos.
  - Verificacion de estabilidad del enlace BLE bajo movimientos rapidos.

* **Viernes 6/11 · Tarde (14:00 – 18:00 · P1 + P2 + P3):**
  - Sesion de pruebas ciegas con 3 a 5 jugadores externos ajenos al desarrollo.
  - Ajuste final de reglas del modo tutorial segun cinematica real.
  - **Congelamiento definitivo de codigo** al finalizar la jornada.
  - **Hito:** Precision $\ge 80\%$ validada con personas externas y codigo 100% congelado.

---

### Clase 6 · Viernes 13/11 · Entrega del MVP
**Materiales a llevar:** MVP completo, Powerbank cargado al 100%, celular extra con memoria y tripode para filmar la demo.

* **Viernes 13/11 · Mañana (09:00 – 13:00 · P1 + P3):**
  - Ensayos de estres de bateria y estabilidad termica/conexion.
  - Checklist final de hardware y app web.

* **Viernes 13/11 · Tarde (14:00 – 18:00 · P1 + P2 + P3):**
  - Toma de metricas finales (latencia de prediccion, tasa de acierto, autonomia).
  - Filmacion del video de respaldo de la demo completa.
  - Presentacion y entrega del MVP.
  - **Hito: MVP 100 % completado.**

---

### 4.7 Calculo de Angulo y Filtro de Orientacion (Parte del MVP)

**¿Por que esta en el MVP?**
En `CONTRATOS.md`, el struct binario de 14 bytes (`BlePayload`) que P1 le manda por Bluetooth a P3 incluye explicitamente el campo:
```cpp
int16_t ang_deg; // 2 bytes: Angulo de la cara (- cerrada, + abierta)
```
Si no calculan la orientacion de la paleta, ese campo viaja en 0 o con basura, y la Web App de P3 no puede mostrar si el jugador impacto con la paleta abierta o cerrada.

#### 1. Donde SI se necesita un filtro (Calculo del angulo de la cara)
Para completar el campo `ang_deg` y saber si la paleta entro abierta o cerrada, necesitas conocer la orientacion espacial de la madera respecto a la gravedad:
- **El problema fisico:** En medio de un swing de tenis de mesa no podes calcular el angulo simplemente con $\arctan(a_z / a_x)$, porque las aceleraciones centripeta y tangencial superan por mucho a la gravedad ($1\text{ g}$) y falsean el vector vertical.
- **La solucion:** Un algoritmo de orientacion espacial (*attitude estimation*) que integre el giroscopio y use el acelerometro para corregir la deriva (*drift*) lentamente.

#### 2. Como resolverlo sin volverse locos en el MVP
No tienen que programar las ecuaciones de Madgwick desde cero en C++. Hay dos caminos directos:

**Opcion A: La via estandar (Libreria probada en Arduino/ESP-IDF)**
Usar la libreria `MadgwickAHRS` (disponible en el gestor de librerias de Arduino). Son apenas dos llamadas:
```cpp
Madgwick filter;
filter.begin(100); // Se actualiza a 100 Hz, no a 1000 Hz

// En el loop:
filter.updateIMU(gx, gy, gz, ax, ay, az);
float pitch = filter.getPitch(); // o el angulo sobre el eje normal
```

**Opcion B: El "atajo" heuristico de MVP (Filtro complementario de 3 lineas)**
Si Madgwick les da problemas de ajuste de ganancia ($\beta$) durante la Clase 1 o 2:
- Antes del swing (cuando la paleta esta casi quieta), calculan el angulo base con el acelerometro: $\theta_{\text{acc}} = \arctan2(a_z, a_x) \cdot \frac{180}{\pi}$.
- Durante los ~150 ms del golpe rapido, integran puramente el giroscopio: $\Delta\theta = \int g_y \, dt$.
- Angulo al impacto = $\theta_{\text{base}} + \Delta\theta$.

#### 3. Implementacion practica: No calcular a 1000 Hz
No es necesario correr el filtro Madgwick a 1000 Hz durante toda la sesion:
- **Fase de preparacion ($t < -150\text{ ms}$):** El jugador prepara el tiro. Ahi el movimiento es suave. Correr Madgwick o un filtro complementario liviano a 100 o 200 Hz mantiene orientado el cuaternion del sistema.
- **Fase de swing rapido / impacto:** Congelas la correccion del acelerometro (pones $\beta = 0$ para que el choque de la pelota no incline la estimacion) e integras puramente la rotacion del giroscopio durante los 50 ms previos al impacto.

**Conclusion de Fase 1 (MVP actual):** Inferencia de los 4 golpes en el ESP32 + calculo del angulo `ang_deg` e impacto por IMU + envio por BLE al celular.

## 5. Fase 2: Video de Entrega y Tracking de Postura (Post 13/11)

- **Grabacion final:** Una sola toma lateral a 3 metros (altura de cadera), 60 fps, con iluminacion uniforme.
- **Superposicion sincronica:** Procesamiento en Python con YOLOv8-pose / YOLO11-pose para extraer esqueleto (17 keypoints), sincronizado con el impacto del sensor via audio del golpe.
- **Comparacion biomecanica:** Contrastar flexion de rodillas y codo del usuario vs. clips de entrenadores de referencia.

---

### 5.1 Modo Tutorial: Entrenador Biomecanico Interactivo (Feature Practica)

Para que el proyecto tenga rigor tecnico y no hagan promesas falsas ante los profesores, hay que tener claro el alcance del sensor.

#### 1. El limite fisico: que puede y que NO puede decir la app
**Lo que el sensor SI sabe (en la paleta):**
- Angulo de la cara en el momento exacto del impacto (`ang_deg`).
- Velocidad tangencial estimada del golpe (`vel_kmh`).
- Cuando acelero la muñeca respecto al impacto (`pico_ms`).
- Si el movimiento fue de cepillado (*brushing*) o de empuje plano/bloqueo (segun los ratios $\omega / a_z$).

**Lo que el sensor NO sabe (y no deben inventar):**
- Posicion de los pies, cadera o codo (eso requeriria camara o sensores en el cuerpo).

**Regla de oro de los feedbacks:**
- La app **nunca** debe decir: *"Abri mas el codo"* o *"Flexiona las rodillas"*.
- La app **si** debe decir: *"Entraste con la cara 15° demasiado abierta"* o *"Aceleraste despues del impacto; el latigo de muñeca tiene que ser antes"*.

#### 2. Como se estructura el "Modo Tutorial"
En la web app de P3, en vez de limitarse a mostrar una tabla de metricas crudas, se armara una pestaña "Academia / Tutoriales" con objetivos por niveles.

**Modulo: "Aprender Topspin de Derecha (Comba)"**
El usuario entra a una pantalla con 3 pasos guiados:

- **Paso 1: Angulo de ataque (Cerrar la cara)**
  - **Objetivo:** Lograr 5 golpes seguidos con la cara cerrada entre $-15^\circ$ y $-35^\circ$.
  - **Feedback visual:** La app muestra un grafico o indicador de aguja.
  - **Regla:** Si `ang_deg > -5°`, disparar audio/texto: *"Paleta muy vertical. Vas a tirar la pelota afuera; cerra la muñeca hacia la mesa"*.

- **Paso 2: El 'Brushing' (Velocidad de roce vs. Choque)**
  - **Objetivo:** Superar los $15\text{ km/h}$ o cierto umbral de aceleracion angular ($\omega_y > 800^\circ/\text{s}$) asegurando que el tipo de golpe sea clasificado como Topspin por Edge Impulse.
  - **Regla:** Si el modelo clasifica como Empuje pero el jugador intento hacer topspin, disparar audio/texto: *"Estas empujando la pelota plana. Hace un arco ascendente de abajo hacia arriba"*.

- **Paso 3: Timing del latigo (El pico de giro)**
  - **Objetivo:** Con la metrica `pico_ms` del struct: si el pico maximo de rotacion angular ocurrio despues de tocar la pelota (`pico_ms > 0`), el golpe fue trabado.
  - **Feedback:** *"Llegaste tarde con la aceleracion. El pico de velocidad tiene que alcanzarse justo antes del impacto"*.

#### 3. Esfuerzo de desarrollo vs. Impacto real
- **Complejidad de codigo (P3): Baja / Media.**
  Son condicionales puros (`if`/`else`) sobre el `BlePayload` que ya reciben en la web app via Web Bluetooth. Solo implica armar una interfaz con tarjetas de desafios (*"Desafio: 5 topspins con cara cerrada"*), un contador de progreso y un sintetizador de voz del navegador (`window.speechSynthesis`) para que el celular hable en tiempo real mientras el jugador tiene la paleta en la mano.
- **Impacto en la evaluacion: Altisimo.**
  Pasan de presentar *"un hardware con acelerometro que tira numeritos en pantalla"* a presentar *"un entrenador biomecanico interactivo de tenis de mesa"*.



## 6. Matriz de Riesgos y Planes de Contingencia

| Riesgo | Plan B |
| --- | --- |
| P1 trabado con interrupciones del ESP32 a 1000 Hz | Pasar temporalmente a *polling* (`delayMicroseconds(900)`) en el `loop()` para no bloquear la grabacion de P2 |
| MPU-6500 saturado o con ruido en SPI | Bajar frecuencia SPI a 1 MHz; si el bus I2C ya viene armado en la breakout, forzar Fast Mode (400 kHz) |
| Falsos positivos en trigger de impacto por aceleracion | Soldar disco piezoelectrico en pin ADC como comparador analogico puro de vibracion |
| Powerbank se apaga por bajo consumo en reposo | Colocar carga resistiva en paralelo o forzar loop de calculo continuo sin entrar en deep sleep |
| Modelo pesado o latencia alta en ESP32-S3 | Cuantizar a `int8` en Edge Impulse o clasificar por arbol de decision directo sobre picos de $\omega$ |
| Falla en enlace BLE durante la demo | Conexion cableada por puerto serie mostrando los mismos datos en consola/web |

---

## 7. Especificaciones Mecanicas y de Montaje (P2)

### 7.1 Que modelar en Fusion 360
Diseña un **sistema modular de dos piezas acopladas directamente en el pomo** impresas en PETG o PLA (paredes de 1.6 mm a 2.0 mm):

**Pieza A — Portasensor / Base fija (MPU-6500):**
- Medidas de encastre: cavidad que abraza los ultimos 5 a 8 mm del pomo de madera de la paleta (seccion aprox. 34 × 22 mm).
- Aloja la plaqueta del MPU-6500 plana y **rigida contra la madera** (pegada con VHB directo a la base de la madera para transmitir el pulso de choque sin amortiguacion plastica).
- Ventana pasacables interna hacia abajo con traba y alivio mecanico para chicotes cortos.
- Labio perimetral de encastre o guia de fijacion para acoplar la Pieza B.
- Impresion: paredes solidas de 1.6 a 2.0 mm, orientada para maxima rigidez estructural.

**Pieza B — Vaina / Capuchon del ESP32-S3:**
- Diseño tipo vaina que encastra o atornilla firmemente sobre la Pieza A, prolongando el mango hacia abajo en vertical sin aletas laterales.
- Aloja la placa ESP32-S3 orientada de forma vertical (en la misma direccion del eje del mango).
- **Cavidad adaptada a pines macho:** Profundidad util interna de 10 a 12 mm para alojar el grosor total de la placa con sus dos tiras de pines soldadas (8 a 10 mm) sin interferencias mecanicas.
- Abertura en la base inferior centrada para conectar el cable USB-C de alimentacion.
- Aristas redondeadas con filetes (*fillets*) de radio amplio para que el talon de la palma descanse sin molestias.
- **Chau cinta plana exterior:** la longitud de cables SPI pasa de 15 cm exteriores a chicotes internos de 2 a 3 cm, 100 % blindados y protegidos dentro de las piezas plasticas.

### 7.2 Donde ubicar cada componente
- **MPU-6500 y ESP32-S3:** Ambos unificados en el **pomo inferior** (base del mango).
  *Por que ahi:*
  1. **Ergonomia del agarre:** El agarre real *shakehand* del jugador invade por completo la zona de transicion del cuello (apoyo continuo de la eminencia tenar y el pulgar). Un resalto de hasta 10 mm en el cuello arruina la propiocepcion y cambia la biomecanica del golpe.
  2. **Integridad electrica y mecanica:** Elimina la necesidad de pasar un bus digital SPI de 7 vias por el canto del mango expuesto a la friccion de los dedos, torsion y sudor salino.
  3. **Inercia minima ($I = m \cdot r^2$):** Ambos componentes quedan concentrados en el eje de rotacion de la muñeca ($r \approx 0$), por lo que el peso extra tiene un momento de inercia despreciable y la paleta no cabecea.
  4. **Deteccion por Jerk:** Aunque la amplitud bruta es menor que en el cuello, la onda de choque viaja por la madera dura en $< 0.05\text{ ms}$; el trigger por derivada temporal ($\Delta a / \Delta t$) separa limpiamente el choque de la pelota (1-2 ms) de cualquier movimiento muscular humano (30-100 ms).
- **Alimentacion (Powerbank):** En el bolsillo del pantalon.

### 7.3 Como montarlo y cablearlo
- **Fijacion del sensor a la madera del pomo:**
  1. Limpiar la base plana del pomo con alcohol.
  2. Pegar un parche de cinta de pintor estirada (sacrificio) y encima cinta bifaz 3M VHB.
  3. Pegar el MPU-6500 presionando con fuerza directo contra el VHB. El acople debe ser rigido contra la madera para que la onda de choque no se filtre.
- **Interconexion directa (Pieza A $\rightarrow$ Pieza B):**
  - Cortar 7 cables Dupont hembra-hembra a 4-5 cm (para dar margen de conexion con el ESP32 exterior), pelar y estañar las puntas para armar los chicotes.
  - Soldar los chicotes directo a los muñones de pines cortados al ras del MPU.
  - Aislar la cara posterior con cinta aislante o de papel (en reemplazo de Kapton).
  - Aplicar alivio mecanico (gotita de silicona caliente o cinta firme contra la plaqueta) para impedir que la rigidez del cable Dupont arranque pistas o suelte los muñones al doblar.
  - Pasar los chicotes por la ventana pasacables interna de la Pieza A y conectar al ESP32-S3 dentro de la Pieza B.
  - Encastrar la Pieza B sobre la Pieza A. El mango de la paleta queda 100 % limpio y libre de cables o cintas.
- **Alimentacion hacia el cuerpo:**
  - Enchufar un cable USB-C liviano y flexible a la base inferior del capuchon.
  - Pasarlo por dentro de la manga de la remera hacia el powerbank en el bolsillo, con comba floja en el codo para mover el brazo libremente.
