# Plan de trabajo

**Condiciones:** somos 3 y trabajamos solo los viernes, de 9 a 16 (a veces hasta las 18). Entre semana no hay trabajo de proyecto, salvo tramites cortos: compras e impresion 3D.

**Calendario:** hoy (viernes 2/10) es la clase 0. El MVP tiene que estar terminado el **viernes 13/11**. Despues viene la fase 2, hasta la entrega final.

| Clase | 1 | 1.5 (extra) | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fecha | 9/10 | Miercoles 14/10 | 16/10 | 23/10 | 30/10 | 6/11 | **13/11 · MVP** |

No hay un viernes de colchon al final. El margen sale de dos lados: el horario de 16 a 18 de cada viernes, y el 13/11, que esta pensado para cerrar y arreglar, no para agregar cosas.

**Objetivo del MVP:** alguien pega un golpe y el celular muestra **que golpe fue, con que angulo pego la paleta y la velocidad de swing estimada ($v = \omega \cdot r$)**, junto con un consejo tecnico.

**Definicion de terminado del MVP:**
- Reconoce 4 golpes (topspin y empuje, de derecha y de reves) con **80 % de aciertos o mas**, medido con gente que no se uso para entrenar.
- Inferencia y metricas locales en el ESP32-S3 (TinyML / Edge Impulse) enviadas por paquete BLE liviano (< 20 bytes) al impactar.
- Muestra en el celular el angulo en el impacto y si el pico de aceleracion angular ocurrio antes de la bola.
- Funciona sin cables a la compu: alimentado por powerbank en el bolsillo via USB-C.

YOLO-pose y el analisis de postura van en la **fase 2**, despues del 13/11.

---

## 1. Equipo y modulos

Los formatos de datos entre modulos estan fijados en [`CONTRATOS.md`](CONTRATOS.md).

| Persona | Modulos | Que hace | Suplente |
| --- | --- | --- | --- |
| **P1 · Hardware** | Firmware base | Sensor MPU-6500 por SPI a 1000 Hz (interrupciones/DMA), deteccion de impactos (trigger), emision de struct BLE (NimBLE) | P2 |
| **P2 · Datos** | Datos, Modelo + 3D | Grabacion (UART), dataset, entrenamiento Edge Impulse, modulo wrapper C++ (`ml_inference.h`), diseño e impresion de capsula (Fusion 360) | P3 |
| **P3 · Tecnica** | App + UI + BLE | Contrato de payload BLE, App web (Web Bluetooth API), calculo cinematico ($v = \omega \cdot L$), angulos (Madgwick), criterios y consejos | P1 |

### Reglas

- **El suplente sabe como funciona el modulo** que cubre, por si el dueño falta un viernes.
- **Los tres graban datos.** La grabacion es una actividad de grupo, no del modulo de datos solo.
- **Integrar todos los viernes.** Cada viernes a la tarde se prueba de punta a punta lo que haya, aunque sea con datos simulados.
- **Los contratos no se cambian solos:** se discute entre los tres y se actualiza `CONTRATOS.md`.
- **Git:** una rama corta por tarea y PR a `main` (que esta protegida), merge cuando compile y ande. Todo pusheado antes de irse cada viernes. Detalle en [`AGENTS.md`](../AGENTS.md).

---

## 2. Como es un viernes

| Horario | Que se hace |
| --- | --- |
| 9:00 – 9:20 | Arranque: que quedo del viernes pasado, que hito tenemos que mostrar hoy |
| 9:20 – 12:30 | **Trabajo por modulos**, cada uno en lo suyo |
| 12:30 – 13:30 | Almuerzo |
| 13:30 – 15:00 | **Bloque de grupo:** grabacion, pruebas con gente o integracion |
| 15:00 – 15:45 | Prueba de punta a punta y control del hito del dia |
| 15:45 – 16:00 | Cierre: commit, tablero, compras y tareas del proximo viernes |
| 16:00 – 18:00 | **Colchon:** solo para lo atrasado, no para cosas nuevas |

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

### Clase 1 · Viernes 9/10 · Señal real y adquisicion a 1000 Hz (Alimentacion: Cable USB-C a PC)
**Materiales a llevar:** Placa ESP32-S3, MPU-6500, cable USB-C largo (2-3 m), paleta, cinta de pintor, cinta bifaz 3M VHB, cinta aisladora / edge tape, pelotas de ping pong.

| P1 | P2 | P3 |
| --- | --- | --- |
| Configurar IDE para ESP32-S3 y linkear `ml_inference.h` (prueba dummy). Mapear pines, conectar MPU-6500 por SPI $\ge 1\text{ MHz}$, y configurar muestreo a 1000 Hz por interrupcion | Modelar capsula de la placa en Fusion 360 midiendo componentes. Validar aislacion del impacto real vs swings al aire | Algoritmo de orientacion (Madgwick/Mahony) en Python procesando las rafagas. Definir contrato de payload BLE (struct C) |

**Tarde:** 
1. **Montaje provisorio (13:30):** Pegar la plaqueta pelada del MPU-6500 a la madera usando cinta de pintor + VHB, y encintar los cables al canto (protocolo 7.3) para evitar ruido mecanico. Al terminar el dia se despega todo.
2. **Grabacion:** 30-40 min de capturas con cable USB largo (swings al aire vs. golpes reales contra pelota).
**Hito:** Señal limpia a 1000 Hz en PC y trigger de impacto validado sin falsos positivos.
*⚠️ Salvavidas (Plan B):* Si a las 11:30 AM P1 no logra estabilizar las interrupciones de hardware, abortar y usar un bucle de *polling* bruto (`delayMicroseconds`) para garantizar la grabacion de la tarde.

### Clase 1.5 · Miercoles 14/10 · Sesion extraordinaria: Banco de pruebas e infraestructura (3 horas)
**Contexto y objetivo:** Sesion intermedia para absorber el atraso de la Clase 1 y reestructurar el montaje hacia el pomo. El unico objetivo real es que **el hardware quede fisicamente armado y escupiendo datos limpios por puerto serie a 1000 Hz**. Nada mas. El trigger fino y la grabacion con pelota se reservan para el viernes.

**Materiales a llevar:** Paleta, MPU-6500 de repuesto, ESP32-S3, alicate, soldador/estaño, cables flexibles para chicotes (3-4 cm), cinta Kapton, cinta de pintor, cinta bifaz 3M VHB, regla metalica o calibre, y cable USB-C a PC.

```
[0:00 - 1:15] Taller de Soldadura y Montaje (P1 + P2)
              └── Chicotes soldados + Montaje pomo + Cable USB asegurado + Medicion L

[1:15 - 2:15] Validacion de Enlace SPI y Signos (P1)
              └── 1000 Hz estables + Signos ax/az verificados en mesa + Offsets

[2:15 - 3:00] Buffer y Telemetria en Python (P2 + P3)
              └── ver.py recibiendo paquetes sin dropear + Paleta a la funda
```

#### 1. Hardware y Montaje (P1 + P2) — 75 min
* Cortar los pines macho del MPU-6500 al ras dejando solo 1 mm de muñon (no desoldar).
* Soldar los 7 cables flexibles cortos (3 a 4 cm) para las lineas SPI (`VCC`, `GND`, `SCL`, `SDA`, `AD0`, `NCS`, `INT`).
* Proteger la cara posterior de las soldaduras con cinta Kapton.
* Montar en el pomo: limpiar con alcohol, cinta de pintor estirada (sacrificio) y cinta 3M VHB directa contra la plaqueta del sensor.
* Fijar el ESP32-S3 abajo en linea con cinta, asegurando que el conector USB-C no reciba esfuerzo mecanico.
* P3 mide la constante geometrica $L$ (base del pomo a centro geometrico del sweet spot) y deja escrito el `#define L_PALETA_M` en el codigo.

#### 2. Validacion de Enlace SPI y Signos (P1) — 60 min
* Levantar el firmware base leyendo el MPU-6500 por SPI a 1000 Hz.
* Verificar con la paleta apoyada en la mesa que no haya cuelgues de bus ni lecturas en cero continuo.
* Comprobar la convencion de `alinearEjes()`:
  - Paleta plana con goma roja hacia arriba: $a_z \approx +1\text{ g}$.
  - Paleta vertical con el pomo en la mesa y punta al techo: $a_x \approx +1\text{ g}$.
* Correr `calibrar.py` para fijar los offsets en reposo y cargarlos en `OFFSET_A*_G` de `paleta.ino`.

#### 3. Enlace con Python y Guardado (P2 + P3) — 45 min
* Conectar la paleta a la PC a 921600 baudios y abrir `ver.py`.
* Mover la paleta en la mano y verificar que las curvas grafiquen fluido y sin *buffer overflow*.
* Confirmar que la estructura del buffer circular retenga los paquetes temporales previstos.
* Guardar la paleta armada en su funda protectora, lista e intacta para el viernes.

**Criterio de corte del Miercoles:** Se van a sus casas cuando vean en la pantalla de la compu las 6 curvas (3 aceleraciones, 3 giroscopios) moviendose en tiempo real a 1000 Hz con el sensor firme en el pomo.

---

### Clase 2 · Viernes 16/10 · Calibracion de Trigger y Grabacion Masiva (Alimentacion: Cable USB-C a PC)
**Materiales a llevar:** Paleta ya ensamblada en Clase 1.5 (en su funda intacta), cable USB-C a PC, pelotas de ping pong (minimo 20), red portatil y cinta de repuesto por contingencia.
*Nota de compras:* Ya NO hace falta comprar cinta plana de 7 vias, tramos largos de termocontraible ni edge tape para tapar cables en el mango. El mango queda 100 % libre.

| P1 | P2 | P3 |
| --- | --- | --- |
| **Mañana:** Implementar y calibrar trigger por Jerk. **Tarde:** Monitoreo de buffer circular | **Mañana:** Validacion de recepcion de eventos. **Tarde:** Grabacion masiva y segmentacion | **Mañana:** Pruebas de estimacion $v = \omega \cdot L$. **Tarde:** Multiball y control de calidad |

**Plan de la jornada (Viernes 16/10):**
1. **Mañana (9:00 - 12:30) · Calibracion del Trigger por Jerk e Impacto:**
   - Implementar $Jerk[k] = (|a[k]| - |a[k-1]|) \cdot 1000$ en firmware.
   - Ajuste de umbral: tirar 10 swings rapidos al aire (**no debe disparar**) vs. toques secos con pelota o dedos (**debe disparar al instante**).
   - Validar congelamiento de la ventana de 196 ms alrededor del impacto en el buffer circular.
2. **Tarde (13:30 - 16:00) · Grabacion Masiva del Dataset v1:**
   - Los 4 golpes tecnicos: 50 golpes por tipo (Topspin Der/Rev, Empuje Der/Rev) $\approx$ 600 tiros utiles con alimentacion constante (multiball).
   - Tanda obligatoria de 50 a 60 muestras de descarte (`ruido` / `not_a_swing`) siguiendo [`PROTOCOLO.md`](PROTOCOLO.md#4-protocolo-deliberado-para-la-clase-no-golpe-ruido--not_a_swing) (falsos swings al aire, malabares, acomodar grip, caminata/recogida).
   - Segmentar con `segmentar.py` y subir el Dataset v1 a Drive.

**Hito:** Dataset v1 completo (4 golpes + clase de ruido balanceada) listo para entrenar el modelo en la Clase 3.
*⚠️ Criterio de Trigger (Plan B):* Si durante las grabaciones el trigger por Jerk muestra falsos positivos aislados, ajustar UMBRAL_JERK o elevar el refractario temporal antes de considerar sensores adicionales.

### Clase 3 · Viernes 23/10 · Despliegue TinyML y Pase a Inalambrico (Alimentacion: Powerbank en bolsillo)
**Materiales a llevar:** Paleta ensamblada provisional, Powerbank de bolsillo, cable USB-C estandar (bolsillo a paleta), celular de prueba para P3.

| P1 | P2 | P3 |
| --- | --- | --- |
| Pasar a alimentacion por Powerbank (verificar que no corte) y emitir struct de prediccion por NimBLE al detectar impacto | Entrenar modelo en Edge Impulse, optimizar cuantizacion INT8, exportar C++ y actualizar `ml_inference.h` | Conectar app web con el BLE real: parsear struct (payload C cerrado) y actualizar UI al impacto |

**Tarde:** Capturar a 3–5 compañeros de la facultad con la paleta inalambrica para validar precision fuera del dataset de entrenamiento.
**Hito:** Precision medida en hardware real.
- $\ge 80\%$: se avanza a integracion final.
- $60\% - 80\%$: reentrenamiento con golpes ambiguos.
- $< 60\%$: reducir alcance a 3 golpes.

**Durante la semana:** P2 envia la capsula y el capuchon a imprimir en 3D (medidas y parametros de impresion en la seccion 7.1).

### Clase 4 · Viernes 30/10 · Integracion Total y Ensamble Definitivo
**Materiales a llevar:** Piezas impresas en 3D (Capsula y Capuchon traidas por P2), adhesivo removible / masilla, herramientas menores para ensamble final.

| P1 | P2 | P3 |
| --- | --- | --- |
| Calce en seco de la Pieza A (Portasensor) abrazando el pomo de madera, verificar paso holgado de chicotes internos hacia la Pieza B (Vaina ESP32), encastrar Pieza B sobre Pieza A y verificar alivio y acceso USB-C | Cargar modelo exportado de Edge Impulse en firmware y verificar estabilidad SPI a 1000 Hz | Enlazar Web App por BLE (struct 14 bytes) y validar refresco de UI con golpes en vivo |

**Tarde (los tres):** Prueba de humo de punta a punta con la paleta ensamblada. 20 golpes de cada tipo entre los integrantes del grupo para chequear autonomia y robustez mecanica.  
**Hito:** Paleta armada en su carcasa definitiva, transmitiendo metricas al celular sin cables a la PC.

---

### Clase 5 · Viernes 6/11 · Validacion Ciega y Ajuste Heuristico
**Materiales a llevar:** Hardware 100% ensamblado y funcional, red y pelotas para las pruebas ciegas.

| P1 | P2 | P3 |
| --- | --- | --- |
| Calibrar umbrales de trigger de impacto para eliminar falsos positivos por roces | Ajustar umbral de confianza en inferencia (descartar tiros ambiguos a clase 4) | Pulir reglas heuristicas de consejos segun cinematica teorica (angulos y pico de giro) |

**Tarde:** Sesion de pruebas de usabilidad y acierto ciego con 3 a 5 compañeros ajenos a la carrera para medir la generalizacion del modelo.  
**Congelamiento de codigo al finalizar la jornada.**  
**Hito:** Precision $\ge 80\%$ validada en personas externas al entrenamiento y codigo 100% congelado.

### Clase 6 · Viernes 13/11 · MVP Terminado
**Materiales a llevar:** MVP completo, Powerbank cargado al 100%, camara o celular extra con buen almacenamiento y tripode para filmar la demo.

- **Mañana:** Calibraciones menores y pruebas de estres de bateria/enlace BLE.
- **Tarde:** Medicion de metricas finales (latencia, acierto, bateria), ensayo general y **filmacion de la demo de respaldo**.

**Hito: MVP 100 % completado.**

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
  - Soldar chicotes de cables flexibles cortos (2 a 3 cm) directo a los muñones de pines cortados al ras del MPU.
  - Pasar los chicotes por la ventana pasacables interna de la Pieza A y conectar al ESP32-S3 dentro de la Pieza B.
  - Encastrar la Pieza B sobre la Pieza A. El mango de la paleta queda 100 % limpio y libre de cables o cintas.
- **Alimentacion hacia el cuerpo:**
  - Enchufar un cable USB-C liviano y flexible a la base inferior del capuchon.
  - Pasarlo por dentro de la manga de la remera hacia el powerbank en el bolsillo, con comba floja en el codo para mover el brazo libremente.
