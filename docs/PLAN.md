# Plan de trabajo

**Condiciones:** somos 3 y trabajamos solo los viernes, de 9 a 16 (a veces hasta las 18). Entre semana no hay trabajo de proyecto, salvo trámites cortos: compras e impresión 3D.

**Calendario:** hoy (viernes 2/10) es la clase 0. El MVP tiene que estar terminado el **viernes 13/11**. Después viene la fase 2, hasta la entrega final.

| Clase | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Viernes | 9/10 | 16/10 | 23/10 | 30/10 | 6/11 | **13/11 · MVP** |

No hay un viernes de colchón al final. El margen sale de dos lados: el horario de 16 a 18 de cada viernes, y el 13/11, que está pensado para cerrar y arreglar, no para agregar cosas.

**Objetivo del MVP:** alguien pega un golpe y el celular muestra **qué golpe fue, con qué ángulo pegó la paleta y la velocidad de swing estimada ($v = \omega \cdot r$)**, junto con un consejo técnico.

**Definición de terminado del MVP:**
- Reconoce 4 golpes (topspin y empuje, de derecha y de revés) con **80 % de aciertos o más**, medido con gente que no se usó para entrenar.
- Inferencia y métricas locales en el ESP32-S3 (TinyML / Edge Impulse) enviadas por paquete BLE liviano (< 20 bytes) al impactar.
- Muestra en el celular el ángulo en el impacto y si el pico de aceleración angular ocurrió antes de la bola.
- Funciona sin cables a la compu: alimentado por powerbank en el bolsillo vía USB-C.

YOLO-pose y el análisis de postura van en la **fase 2**, después del 13/11.

---

## 1. Equipo y módulos

Los formatos de datos entre módulos están fijados en [`CONTRATOS.md`](CONTRATOS.md).

| Persona | Módulos | Qué hace | Suplente |
| --- | --- | --- | --- |
| **P1 · Hardware** | Firmware base | Sensor MPU-6500 por SPI a 1000 Hz (interrupciones/DMA), detección de impactos (trigger), emisión de struct BLE (NimBLE) | P2 |
| **P2 · Datos** | Datos, Modelo + 3D | Grabación (UART), dataset, entrenamiento Edge Impulse, módulo wrapper C++ (`ml_inference.h`), diseño e impresión de cápsula (Fusion 360) | P3 |
| **P3 · Técnica** | App + UI + BLE | Contrato de payload BLE, App web (Web Bluetooth API), cálculo cinemático ($v = \omega \cdot L$), ángulos (Madgwick), criterios y consejos | P1 |

### Reglas

- **El suplente sabe cómo funciona el módulo** que cubre, por si el dueño falta un viernes.
- **Los tres graban datos.** La grabación es una actividad de grupo, no del módulo de datos solo.
- **Integrar todos los viernes.** Cada viernes a la tarde se prueba de punta a punta lo que haya, aunque sea con datos simulados.
- **Los contratos no se cambian solos:** se discute entre los tres y se actualiza `CONTRATOS.md`.
- **Git:** ramas `firmware`, `datos`, `app`, merge a `main` cuando compile y ande. Commit antes de irse cada viernes.

---

## 2. Cómo es un viernes

| Horario | Qué se hace |
| --- | --- |
| 9:00 – 9:20 | Arranque: qué quedó del viernes pasado, qué hito tenemos que mostrar hoy |
| 9:20 – 12:30 | **Trabajo por módulos**, cada uno en lo suyo |
| 12:30 – 13:30 | Almuerzo |
| 13:30 – 15:00 | **Bloque de grupo:** grabación, pruebas con gente o integración |
| 15:00 – 15:45 | Prueba de punta a punta y control del hito del día |
| 15:45 – 16:00 | Cierre: commit, tablero, compras y tareas del próximo viernes |
| 16:00 – 18:00 | **Colchón:** solo para lo atrasado, no para cosas nuevas |

---

## 3. Clase 0: hoy

### Organización (los tres, primera hora)

- [ ] Confirmar roles: P1, P2 y P3.
- [ ] **Comprar por internet** para recibir antes del 9/10: **2 módulos MPU-6500** (uno de repuesto), cables dupont hembra-hembra, cable USB-C flexible largo (2–3 m) cinta de pintor, cinta bifaz 3M VHB y cinta aisladora. Alternativa de respaldo: 2 discos piezoeléctricos chicos por si el trigger por acelerómetro mete ruido.
- [ ] Crear el repo en GitHub, subir estructura base y dar permisos al equipo.
- [ ] Crear la carpeta de Drive para los CSV crudos.
- [ ] **Confirmar mesa de ping pong disponible los viernes a la tarde**, red portátil, 2 paletas y mínimo 20 pelotas para tiros en ráfaga.
- [ ] Averiguar proveedor de impresión 3D y tiempos de entrega (impresión entre Clase 3 y 4).
- [ ] Contactar al jugador de referencia para coordinar su asistencia el viernes 30/10 (Clase 4).

### Código y Banco (sin sensor físico aún)

| Quién | Tarea | Listo cuando… |
| --- | --- | --- |
| **P2** | Escribir módulo wrapper C++ (`ml_inference.h/cpp`) integrando el modelo Edge Impulse sintético (`firmware/modelo_dummy_sintetico.zip`) | Módulo encapsulado listo con función `predecir_golpe()` |
| **P2** | Script receptor en Python por puerto serie (lectura a 921600 baudios) y visualizador `ver.py` | Recibe paquetes simulados a 1000 Hz sin dropping de buffers |
| **P2** | Escribir protocolo de captura (`docs/PROTOCOLO.md`): orden de tiros, estructura y metadatos de CSV | Protocolo cerrado |
| **P3** | App web base (Web Bluetooth API) desplegada en GitHub Pages | Conecta y parsea el string de prueba del contrato |
| **P3** | Definir rangos biomecánicos preliminares (ángulos de impacto y velocidad tangencial) | Tabla base en `docs/` |

---

## 4. Fase 1: MVP, viernes por viernes

### Clase 1 · Viernes 9/10 · Señal real y adquisición a 1000 Hz (Alimentación: Cable USB-C a PC)
**?? Materiales a llevar:** Placa ESP32-S3, MPU-6500, cable USB-C largo (2-3 m), paleta, cinta de pintor, cinta bifaz 3M VHB, cinta aisladora / edge tape, pelotas de ping pong.

| P1 | P2 | P3 |
| --- | --- | --- |
| Configurar IDE para ESP32-S3 y linkear `ml_inference.h` (prueba dummy). Mapear pines, conectar MPU-6500 por SPI $\ge 1\text{ MHz}$, y configurar muestreo a 1000 Hz por interrupción | Modelar cápsula de la placa en Fusion 360 midiendo componentes. Validar aislación del impacto real vs swings al aire | Algoritmo de orientación (Madgwick/Mahony) en Python procesando las ráfagas. Definir contrato de payload BLE (struct C) |

**Tarde:** 
1. **Montaje provisorio (13:30):** Pegar la plaqueta pelada del MPU-6500 a la madera usando cinta de pintor + VHB, y encintar los cables al canto (protocolo 7.3) para evitar ruido mecánico. Al terminar el día se despega todo.
2. **Grabación:** 30-40 min de capturas con cable USB largo (swings al aire vs. golpes reales contra pelota).
**Hito:** Señal limpia a 1000 Hz en PC y trigger de impacto validado sin falsos positivos.
*⚠️ Salvavidas (Plan B):* Si a las 11:30 AM P1 no logra estabilizar las interrupciones de hardware, abortar y usar un bucle de *polling* bruto (`delayMicroseconds`) para garantizar la grabación de la tarde.

### Clase 2 · Viernes 16/10 · Grabación masiva del Dataset (Alimentación: Cable USB-C a PC)
**?? Materiales a llevar:** Setup f�sico de Clase 1, m�nimo 20 pelotas de ping pong y red port�til.

| P1 | P2 | P3 |
| --- | --- | --- |
| Implementar buffer circular en ESP32-S3 (congelar ventana de 200 ms alrededor del impacto) y testear BLE en dummy | Script de segmentación automática de impactos y formateo directo para Edge Impulse | Pruebas de estimación de velocidad tangencial ($v = \omega_{\text{swing}} \cdot L$) y visualización en tiempo real |

**Tarde: Grabación masiva.** Los tres: 50 golpes por tipo (Topspin Der/Rev, Empuje Der/Rev) $\approx$ 600 tiros.
**Hito:** Dataset v1 subido a Drive y segmentado para entrenamiento.
*⚠️ Criterio de Trigger (Plan B):* Evaluar si el acelerómetro detecta limpiamente el impacto sin falsos positivos. Si anda bien, se descarta el piezoeléctrico. Si mete ruido, el piezoeléctrico entra al diseño 3D y hardware de inmediato.

### Clase 3 · Viernes 23/10 · Despliegue TinyML y Pase a Inalámbrico (Alimentación: Powerbank en bolsillo)
**?? Materiales a llevar:** Paleta ensamblada provisional, Powerbank de bolsillo, cable USB-C est�ndar (bolsillo a paleta), celular de prueba para P3.

| P1 | P2 | P3 |
| --- | --- | --- |
| Pasar a alimentación por Powerbank (verificar que no corte) y emitir struct de predicción por NimBLE al detectar impacto | Entrenar modelo en Edge Impulse, optimizar cuantización INT8, exportar C++ y actualizar `ml_inference.h` | Conectar app web con el BLE real: parsear struct (payload C cerrado) y actualizar UI al impacto |

**Tarde:** Capturar a 3–5 compañeros de la facultad con la paleta inalámbrica para validar precisión fuera del dataset de entrenamiento.
**Hito:** Precisión medida en hardware real.
- $\ge 80\%$: se avanza a integración final.
- $60\% - 80\%$: reentrenamiento con golpes ambiguos.
- $< 60\%$: reducir alcance a 3 golpes.

**Durante la semana:** P2 envía la cápsula a imprimir en 3D.

### Clase 4 · Viernes 30/10 · Integración Total y Ensamble Definitivo
**?? Materiales a llevar:** Piezas impresas en 3D (C�psula y Capuch�n tra�das por P2), herramientas menores para ensamble final.

| P1 | P2 | P3 |
| --- | --- | --- |
| Montar electrónica en la carcasa 3D final, fijar sensor al cuello y verificar alivio de tensión USB | Cargar modelo exportado de Edge Impulse en firmware y verificar estabilidad SPI a 1000 Hz | Enlazar Web App por BLE (struct 14 bytes) y validar refresco de UI con golpes en vivo |

**Tarde (los tres):** Prueba de humo de punta a punta con la paleta ensamblada. 20 golpes de cada tipo entre los integrantes del grupo para chequear autonomía y robustez mecánica.  
**Hito:** Paleta armada en su carcasa definitiva, transmitiendo métricas al celular sin cables a la PC.

---

### Clase 5 · Viernes 6/11 · Validación Ciega y Ajuste Heurístico
**?? Materiales a llevar:** Hardware 100% ensamblado y funcional, red y pelotas para las pruebas ciegas.

| P1 | P2 | P3 |
| --- | --- | --- |
| Calibrar umbrales de trigger de impacto para eliminar falsos positivos por roces | Ajustar umbral de confianza en inferencia (descartar tiros ambiguos a clase 4) | Pulir reglas heurísticas de consejos según cinemática teórica (ángulos y pico de giro) |

**Tarde:** Sesión de pruebas de usabilidad y acierto ciego con 3 a 5 compañeros ajenos a la carrera para medir la generalización del modelo.  
**Congelamiento de código al finalizar la jornada.**  
**Hito:** Precisión $\ge 80\%$ validada en personas externas al entrenamiento y código 100% congelado.

### Clase 6 · Viernes 13/11 · MVP Terminado
**?? Materiales a llevar:** MVP completo, Powerbank cargado al 100%, c�mara o celular extra con buen almacenamiento y tr�pode para filmar la demo.

- **Mañana:** Calibraciones menores y pruebas de estrés de batería/enlace BLE.
- **Tarde:** Medición de métricas finales (latencia, acierto, batería), ensayo general y **filmación de la demo de respaldo**.

**Hito: MVP 100 % completado.**

---


### 4.7 Cálculo de Ángulo y Filtro de Orientación (Parte del MVP)

**¿Por qué está en el MVP?**
En `CONTRATOS.md`, el struct binario de 14 bytes (`BlePayload`) que P1 le manda por Bluetooth a P3 incluye explícitamente el campo:
```cpp
int16_t ang_deg; // 2 bytes: Ángulo de la cara (+ cerrada, - abierta)
```
Si no calculan la orientación de la paleta, ese campo viaja en 0 o con basura, y la Web App de P3 no puede mostrar si el jugador impactó con la paleta abierta o cerrada.

#### 1. Dónde SÍ se necesita un filtro (Cálculo del ángulo de la cara)
Para completar el campo `ang_deg` y saber si la paleta entró abierta o cerrada, necesitás conocer la orientación espacial de la madera respecto a la gravedad:
- **El problema físico:** En medio de un swing de tenis de mesa no podés calcular el ángulo simplemente con $\arctan(a_z / a_x)$, porque las aceleraciones centrípeta y tangencial superan por mucho a la gravedad ($1\text{ g}$) y falsean el vector vertical.
- **La solución:** Un algoritmo de orientación espacial (*attitude estimation*) que integre el giroscopio y use el acelerómetro para corregir la deriva (*drift*) lentamente.

#### 2. Cómo resolverlo sin volverse locos en el MVP
No tienen que programar las ecuaciones de Madgwick desde cero en C++. Hay dos caminos directos:

**Opción A: La vía estándar (Librería probada en Arduino/ESP-IDF)**
Usar la librería `MadgwickAHRS` (disponible en el gestor de librerías de Arduino). Son apenas dos llamadas:
```cpp
Madgwick filter;
filter.begin(100); // Se actualiza a 100 Hz, no a 1000 Hz

// En el loop:
filter.updateIMU(gx, gy, gz, ax, ay, az);
float pitch = filter.getPitch(); // o el ángulo sobre el eje normal
```

**Opción B: El "atajo" heurístico de MVP (Filtro complementario de 3 líneas)**
Si Madgwick les da problemas de ajuste de ganancia ($\beta$) durante la Clase 1 o 2:
- Antes del swing (cuando la paleta está casi quieta), calculan el ángulo base con el acelerómetro: $\theta_{\text{acc}} = \arctan2(a_z, a_x) \cdot \frac{180}{\pi}$.
- Durante los ~150 ms del golpe rápido, integran puramente el giroscopio: $\Delta\theta = \int g_y \, dt$.
- Ángulo al impacto = $\theta_{\text{base}} + \Delta\theta$.

#### 3. Implementación práctica: No calcular a 1000 Hz
No es necesario correr el filtro Madgwick a 1000 Hz durante toda la sesión:
- **Fase de preparación ($t < -150\text{ ms}$):** El jugador prepara el tiro. Ahí el movimiento es suave. Correr Madgwick o un filtro complementario liviano a 100 o 200 Hz mantiene orientado el cuaternión del sistema.
- **Fase de swing rápido / impacto:** Congelás la corrección del acelerómetro (ponés $\beta = 0$ para que el choque de la pelota no incline la estimación) e integrás puramente la rotación del giroscopio durante los 50 ms previos al impacto.

**Conclusión de Fase 1 (MVP actual):** Inferencia de los 4 golpes en el ESP32 + cálculo del ángulo `ang_deg` e impacto por IMU + envío por BLE al celular.

## 5. Fase 2: Video de Entrega y Tracking de Postura (Post 13/11)

- **Grabación final:** Una sola toma lateral a 3 metros (altura de cadera), 60 fps, con iluminación uniforme.
- **Superposición sincrónica:** Procesamiento en Python con YOLOv8-pose / YOLO11-pose para extraer esqueleto (17 keypoints), sincronizado con el impacto del sensor vía audio del golpe.
- **Comparación biomecánica:** Contrastar flexión de rodillas y codo del usuario vs. clips de entrenadores de referencia.

---

### 5.1 Modo Tutorial: Entrenador Biomecánico Interactivo (Feature Práctica)

Para que el proyecto tenga rigor técnico y no hagan promesas falsas ante los profesores, hay que tener claro el alcance del sensor.

#### 1. El límite físico: qué puede y qué NO puede decir la app
**Lo que el sensor SÍ sabe (en la paleta):**
- Ángulo de la cara en el momento exacto del impacto (`ang_deg`).
- Velocidad tangencial estimada del golpe (`vel_kmh`).
- Cuándo aceleró la muñeca respecto al impacto (`pico_ms`).
- Si el movimiento fue de cepillado (*brushing*) o de empuje plano/bloqueo (según los ratios $\omega / a_z$).

**Lo que el sensor NO sabe (y no deben inventar):**
- Posición de los pies, cadera o codo (eso requeriría cámara o sensores en el cuerpo).

**Regla de oro de los feedbacks:**
- La app **nunca** debe decir: *"Abrí más el codo"* o *"Flexioná las rodillas"*.
- La app **sí** debe decir: *"Entraste con la cara 15° demasiado abierta"* o *"Aceleraste después del impacto; el látigo de muñeca tiene que ser antes"*.

#### 2. Cómo se estructura el "Modo Tutorial"
En la web app de P3, en vez de limitarse a mostrar una tabla de métricas crudas, se armará una pestaña "Academia / Tutoriales" con objetivos por niveles.

**Módulo: "Aprender Topspin de Derecha (Comba)"**
El usuario entra a una pantalla con 3 pasos guiados:

- **Paso 1: Ángulo de ataque (Cerrar la cara)**
  - **Objetivo:** Lograr 5 golpes seguidos con la cara cerrada entre $-15^\circ$ y $-35^\circ$.
  - **Feedback visual:** La app muestra un gráfico o indicador de aguja.
  - **Regla:** Si `ang_deg > -5°`, disparar audio/texto: *"Paleta muy vertical. Vas a tirar la pelota afuera; cerrá la muñeca hacia la mesa"*.

- **Paso 2: El 'Brushing' (Velocidad de roce vs. Choque)**
  - **Objetivo:** Superar los $15\text{ km/h}$ o cierto umbral de aceleración angular ($\omega_y > 800^\circ/\text{s}$) asegurando que el tipo de golpe sea clasificado como Topspin por Edge Impulse.
  - **Regla:** Si el modelo clasifica como Empuje pero el jugador intentó hacer topspin, disparar audio/texto: *"Estás empujando la pelota plana. Hacé un arco ascendente de abajo hacia arriba"*.

- **Paso 3: Timing del látigo (El pico de giro)**
  - **Objetivo:** Con la métrica `pico_ms` del struct: si el pico máximo de rotación angular ocurrió después de tocar la pelota (`pico_ms > 0`), el golpe fue trabado.
  - **Feedback:** *"Llegaste tarde con la aceleración. El pico de velocidad tiene que alcanzarse justo antes del impacto"*.

#### 3. Esfuerzo de desarrollo vs. Impacto real
- **Complejidad de código (P3): Baja / Media.**
  Son condicionales puros (`if`/`else`) sobre el `BlePayload` que ya reciben en la web app vía Web Bluetooth. Solo implica armar una interfaz con tarjetas de desafíos (*"Desafío: 5 topspins con cara cerrada"*), un contador de progreso y un sintetizador de voz del navegador (`window.speechSynthesis`) para que el celular hable en tiempo real mientras el jugador tiene la paleta en la mano.
- **Impacto en la evaluación: Altísimo.**
  Pasan de presentar *"un hardware con acelerómetro que tira numeritos en pantalla"* a presentar *"un entrenador biomecánico interactivo de tenis de mesa"*.



## 6. Matriz de Riesgos y Planes de Contingencia

| Riesgo | Plan B |
| --- | --- |
| P1 trabado con interrupciones del ESP32 a 1000 Hz | Pasar temporalmente a *polling* (`delayMicroseconds(900)`) en el `loop()` para no bloquear la grabación de P2 |
| MPU-6500 saturado o con ruido en SPI | Bajar frecuencia SPI a 1 MHz; si el bus I2C ya viene armado en la breakout, forzar Fast Mode (400 kHz) |
| Falsos positivos en trigger de impacto por aceleración | Soldar disco piezoeléctrico en pin ADC como comparador analógico puro de vibración |
| Powerbank se apaga por bajo consumo en reposo | Colocar carga resistiva en paralelo o forzar loop de cálculo continuo sin entrar en deep sleep |
| Modelo pesado o latencia alta en ESP32-S3 | Cuantizar a `int8` en Edge Impulse o clasificar por árbol de decisión directo sobre picos de $\omega$ |
| Falla en enlace BLE durante la demo | Conexión cableada por puerto serie mostrando los mismos datos en consola/web |

---

## 7. Especificaciones Mecánicas y de Montaje (P2)

### 7.1 Qué modelar en Fusion 360
Diseñá dos piezas impresas en PETG o PLA (paredes de 1.6 mm a 2.0 mm):

**Pieza 1 — Cápsula del Sensor (MPU-6500 y Piezoeléctrico):**
- Caja diminuta (aprox. $22 \times 18 \times 7\text{ mm}$, peso $< 5\text{ g}$).
- Alojamiento interno que tape la plaqueta del MPU-6500 y deje un receptáculo contiguo para el disco piezoeléctrico (Plan B).
- Ranura de salida en el canto inferior pasante hacia el capuchón que admita hasta **7 hilos planos** (6 SPI + 1 señal piezoeléctrica, compartiendo masa GND), con traba interna de alivio de tensión (*strain relief*).
- Base inferior 100% plana y ligeramente texturada para maximizar la adhesión.

**Pieza 2 — Capuchón Prolongador del Mango (ESP32-S3):**
- Diseño tipo "vaina" o capuchón que prolonga el mango 3.5 a 4 cm hacia abajo en vertical, sin aletas laterales que sobresalgan del perfil de la mano.
- Zona superior (encastre): Cavidad que abraza los últimos 15 mm del mango de la paleta copiando su forma elíptica/cóncava, con apriete por fricción o ranura para una vuelta de cinta exterior.
- Zona inferior (electrónica): Aloja la placa ESP32-S3 orientada de forma vertical (en la misma dirección del eje del mango).
- Abertura en la base inferior centrada para conectar el cable USB-C de alimentación.
- Entrada superior para recibir los cables del bus SPI que bajan por el canto.
- Aristas redondeadas con filetes (*fillets*) de radio amplio para que el talón de la palma descanse sin molestias.

### 7.2 Dónde ubicar cada componente
- **MPU-6500:** En el cuello de la paleta (el triángulo de madera descubierta entre el mango y la goma), en la cara donde no apoye el dedo índice.
  *Por qué ahí:* Está pegado a la zona de juego (a 2–3 cm del contacto), capturando la vibración pura del impacto ($>150\text{ Hz}$) y el ángulo exacto de la madera sin la amortiguación de los tejidos de la mano.
- **ESP32-S3:** En el extremo inferior del mango (el pomo), alineado longitudinalmente dentro del capuchón.
  *Por qué ahí:* Al estar ubicado en el eje de rotación de la muñeca, los 10–12 gramos extra de la placa y la carcasa tienen un momento de inercia prácticamente despreciable; la punta de la paleta se siente igual de ágil.
- **Alimentación (Powerbank):** En el bolsillo del pantalón.

### 7.3 Cómo montarlo y cablearlo
- **Fijación del sensor a la madera:**
  1. Limpiá la zona del cuello con alcohol.
  2. Pegá primero un parche de cinta de enmascarar (cinta de papel de pintor) bien estirada sobre la madera (cinta de sacrificio).
  3. Encima de la cinta de papel, colocá cinta bifaz (3M VHB).
  4. Apoyá la cara metálica del **disco piezoeléctrico** y la base del **MPU-6500** presionando firmemente directo contra el VHB. *(El piezoeléctrico NUNCA va encastrado en las paredes de plástico porque el plástico actuaría como filtro pasabajos disipando la onda de la madera).* 
  5. La cápsula 3D se coloca por arriba actuando simplemente como un **domo protector** que los cubre, sin apretarlos ni dejarlos sueltos.
- **Puente del bus SPI (Cápsula 1 $\rightarrow$ Cápsula 2):**
  - **Ordenar los cables en cinta plana:** No armes una trenza ni un manojo cilíndrico grueso. Peiná los 6 hilos para que queden planos, uno al lado del otro en paralelo, formando una franja plana de menos de 1 mm de espesor.
  - **Primera fijación (Inmovilización puntual):** Apoyá la franja de cables recorriendo el canto lateral estrecho del mango (la madera del canto entre las dos cachas donde no cierran los dedos). Pegá dos tiritas finas de cinta de papel o cinta scotch transparente bien tensadas (una cerca del cuello y otra cerca de la base) para que los cables no se muevan de su carril mientras trabajás.
  - **Fijación mecánica definitiva y protección:** Cubrí todo el canto lateral del mango de arriba a abajo usando una vuelta de cinta de borde para paleta de ping pong (*edge tape*) o cinta aisladora de PVC de buena calidad. Aplicala estirándola con fuerza para que abrace la madera y copie el relieve. La cinta sella los cables contra el sudor de la mano, evita roces y deja el mango completamente liso al tacto.
- **Alimentación hacia el cuerpo:**
  - Enchufá un cable USB-C liviano y flexible a la base del capuchón.
  - Pasalo por dentro de la manga de la remera hacia el powerbank en el bolsillo, dejando una comba floja a la altura del codo para bracear libremente sin tirones.
