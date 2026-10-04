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
- [ ] **Comprar por internet** para recibir antes del 9/10: **2 módulos MPU-6500** (uno de repuesto), cables dupont hembra-hembra, cable USB-C flexible largo (2–3 m) y precintos. Alternativa de respaldo: 2 discos piezoeléctricos chicos por si el trigger por acelerómetro mete ruido.
- [ ] Crear el repo en GitHub, subir estructura base y dar permisos al equipo.
- [ ] Crear la carpeta de Drive para los CSV crudos.
- [ ] **Confirmar mesa de ping pong disponible los viernes a la tarde**, red portátil, 2 paletas y mínimo 20 pelotas para tiros en ráfaga.
- [ ] Averiguar proveedor de impresión 3D y tiempos de entrega (impresión entre Clase 3 y 4).
- [ ] Contactar al jugador de referencia para coordinar su asistencia el viernes 30/10 (Clase 4).

### Código y Banco (sin sensor físico aún)

| Quién | Tarea | Listo cuando… |
| --- | --- | --- |
| **P1** | Configurar ESP-IDF / Arduino IDE para ESP32-S3-WROOM-1 (N16R8) y probar SPI base | La placa compila y el monitor serie corre a 921600 baudios |
| **P2** | Escribir módulo wrapper C++ (`ml_inference.h/cpp`) integrando el modelo Edge Impulse sintético (`firmware/modelo_dummy_sintetico.zip`) | Módulo encapsulado listo con función `predecir_golpe()` |
| **P1** | Linkear `ml_inference.h` en el `.ino` y correr inferencia de prueba con array dummy | La placa compila el modelo y devuelve la predicción |
| **P1** | Mapear pines SPI libres (`SCK`, `MISO`, `MOSI`, `CS`) y pin `INT` para el MPU-6500 | Pines fijados en el código y libres de strapping pins |
| **P2** | Script receptor en Python por puerto serie (lectura a 921600 baudios) y visualizador `ver.py` | Recibe paquetes simulados a 1000 Hz sin dropping de buffers |
| **P2** | Escribir protocolo de captura (`docs/PROTOCOLO.md`): orden de tiros, estructura y metadatos de CSV | Protocolo cerrado |
| **P3** | App web base (Web Bluetooth API) desplegada en GitHub Pages | Conecta y parsea el string de prueba del contrato |
| **P3** | Definir rangos biomecánicos preliminares (ángulos de impacto y velocidad tangencial) | Tabla base en `docs/` |

---

## 4. Fase 1: MVP, viernes por viernes

### Clase 1 · Viernes 9/10 · Señal real y adquisición a 1000 Hz (Alimentación: Cable USB-C a PC)

| P1 | P2 | P3 |
| --- | --- | --- |
| Conectar MPU-6500 por SPI a $\ge 1\text{ MHz}$. Leer registro `WHO_AM_I` (`0x70`). Configurar muestreo a 1000 Hz por FIFO/interrupción y atar sensor a la paleta | Modelar cápsula de la placa en Fusion 360 midiendo componentes. Validar aislación del impacto real vs swings al aire | Algoritmo de orientación (Madgwick/Mahony) en Python procesando las ráfagas. Definir contrato de payload BLE (struct C) |

**Tarde:** 30–40 min de capturas con cable USB largo (swings al aire vs. golpes reales contra pelota).
**Hito:** Señal limpia a 1000 Hz en PC y trigger de impacto validado sin falsos positivos.

### Clase 2 · Viernes 16/10 · Grabación masiva del Dataset (Alimentación: Cable USB-C a PC)

| P1 | P2 | P3 |
| --- | --- | --- |
| Implementar buffer circular en ESP32-S3 (congelar ventana de 200 ms alrededor del impacto) y testear BLE en dummy | Script de segmentación automática de impactos y formateo directo para Edge Impulse | Pruebas de estimación de velocidad tangencial ($v = \omega_{\text{swing}} \cdot L$) y visualización en tiempo real |

**Tarde: Grabación masiva.** Los tres: 50 golpes por tipo (Topspin Der/Rev, Empuje Der/Rev) $\approx$ 600 tiros.
**Hito:** Dataset v1 subido a Drive y segmentado para entrenamiento.

### Clase 3 · Viernes 23/10 · Despliegue TinyML y Pase a Inalámbrico (Alimentación: Powerbank en bolsillo)

| P1 | P2 | P3 |
| --- | --- | --- |
| Pasar a alimentación por Powerbank (verificar que no corte) y emitir struct de predicción por NimBLE al detectar impacto | Entrenar modelo en Edge Impulse, optimizar cuantización INT8, exportar C++ y actualizar `ml_inference.h` | Conectar app web con el BLE real: parsear struct (payload C cerrado) y actualizar UI al impacto |

**Tarde:** Capturar a 3–5 compañeros de la facultad con la paleta inalámbrica para validar precisión fuera del dataset de entrenamiento.
**Hito:** Precisión medida en hardware real.
- $\ge 80\%$: se avanza a integración final.
- $60\% - 80\%$: reentrenamiento con golpes ambiguos.
- $< 60\%$: reducir alcance a 3 golpes.

**Durante la semana:** P2 envía la cápsula a imprimir en 3D.

### Clase 4 · Viernes 30/10 · Integración Total y Jugador de Referencia

**Mañana (los tres):** Sensor en paleta alimentado por powerbank → Inferencia local en ESP32-S3 → Disparo BLE de métricas ($v$, ángulo, tipo) → App celular mostrando métricas y feedback.
**Tarde:** Sesión de pruebas y validación con el **jugador de referencia**.
**Hito:** Golpes reales recibidos en el celular sin cables ni compu intermediaria.

### Clase 5 · Viernes 6/11 · Ensamble y Ajuste Fino

| P1 | P2 | P3 |
| --- | --- | --- |
| Montar electrónica final en la cápsula impresa y verificar alivio de tensión del cable USB al bolsillo | Calibrar pesos mecánicos de la paleta y reentrenar modelo agregando las muestras del jugador experto | Pulir reglas heurísticas de consejos en base al perfil del jugador de referencia |

**Tarde:** Pruebas de usabilidad ciega con compañeros ajenos a la carrera.
**Congelamiento de código al finalizar la jornada.**
**Hito:** Sistema cerrado y robusto mecánicamente.

### Clase 6 · Viernes 13/11 · MVP Terminado

- **Mañana:** Calibraciones menores y pruebas de estrés de batería/enlace BLE.
- **Tarde:** Medición de métricas finales (latencia, acierto, batería), ensayo general y **filmación de la demo de respaldo**.

**Hito: MVP 100 % completado.**

---

## 5. Fase 2: Video de Entrega y Tracking de Postura (Post 13/11)

- **Grabación final:** Una sola toma lateral a 3 metros (altura de cadera), 60 fps, con iluminación uniforme.
- **Superposición sincrónica:** Procesamiento en Python con YOLOv8-pose / YOLO11-pose para extraer esqueleto (17 keypoints), sincronizado con el impacto del sensor vía audio del golpe.
- **Comparación biomecánica:** Contrastar flexión de rodillas y codo del usuario vs. clips de entrenadores de referencia.

---

## 6. Matriz de Riesgos y Planes de Contingencia

| Riesgo | Plan B |
| --- | --- |
| MPU-6500 saturado o con ruido en SPI | Bajar frecuencia SPI a 1 MHz; si el bus I2C ya viene armado en la breakout, forzar Fast Mode (400 kHz) |
| Falsos positivos en trigger de impacto por aceleración | Soldar disco piezoeléctrico en pin ADC como comparador analógico puro de vibración |
| Powerbank se apaga por bajo consumo en reposo | Colocar carga resistiva en paralelo o forzar loop de cálculo continuo sin entrar en deep sleep |
| Modelo pesado o latencia alta en ESP32-S3 | Cuantizar a `int8` en Edge Impulse o clasificar por árbol de decisión directo sobre picos de $\omega$ |
| Falla en enlace BLE durante la demo | Conexión cableada por puerto serie mostrando los mismos datos en consola/web |

---

## 7. Especificaciones Mecánicas y de Montaje (P2)

### 7.1 Qué modelar en Fusion 360
Diseñar dos carcasas separadas con espesor de pared de 1.5 mm a 2.0 mm, para ser impresas en PETG o PLA:

**Cápsula A (Sensor MPU-6500):**
- Cajita ultracompacta (aprox. $22 \times 18 \times 8\text{ mm}$, peso $< 6\text{ g}$).
- Alojamiento interno justo para la plaqueta del breakout MPU-6500, con soporte para dos tornillos autorroscantes M2 (o trabas por encastre snap-fit).
- Salida lateral o inferior para el mazo de 6 cables SPI con un canal estrangulador (*strain relief*) que evite tirones directos sobre las soldaduras de la placa.
- Cara inferior completamente plana y rugosa para facilitar la adhesión química.

**Cápsula B (Procesador ESP32-S3):**
- Caja ergonómica para alojar el módulo ESP32-S3-WROOM-1 (N16R8).
- Abertura para el conector USB-C (alimentación hacia el powerbank en el bolsillo).
- Salida para la bornera/conector del cable SPI que viene de la mano.
- Base ligeramente curvada para copiar la anatomía del brazo, equipada con dos ranuras laterales pasantes de $25 \times 3\text{ mm}$ para enhebrar una correa elástica deportiva con velcro.

### 7.2 Dónde ubicar cada componente
- **MPU-6500:** En el cuello de la paleta (el triángulo de madera descubierta entre el final de la empuñadura y el borde inferior de la goma). Se monta sobre la cara de revés o en el lateral donde no apoyen las yemas ni el talón de los dedos.
  *Por qué ahí:* Está a solo 2–3 cm del punto de impacto, capturando la onda elástica de alta frecuencia ($> 150\text{ Hz}$) sin la amortiguación viscoelástica que introduce la mano en el mango, y con mayor brazo de palanca angular que en el pomo inferior.
- **ESP32-S3:** En el tercio medio o superior del antebrazo (lado dorsal, unos 8–12 cm por debajo del codo).
  *Por qué ahí:* Despeja la articulación de la muñeca para movimientos explosivos de flexión y rotación (brushing), y no agrega peso a la mano.
- **Batería (Powerbank):** En el bolsillo del pantalón, unida al antebrazo por un cable USB estándar pasado por debajo de la remera.

### 7.3 Cómo montarlo y fijarlo (Mecánica y Cableado)
- **Fijación del sensor a la madera (segura y desmontable):**
  1. Limpiar la zona del cuello con alcohol isopropílico.
  2. Pegar una primera capa de cinta de enmascarar de papel (cinta de pintor) bien tensionada sobre la madera.
  3. Sobre esa cinta de papel, colocar cinta bifaz de espuma acrílica (3M VHB).
  4. Presionar la base plana de la Cápsula A contra la 3M VHB durante 30 segundos. Esta combinación transmite la rigidez requerida para los 1000 Hz pero permite despegar todo tirando del papel sin astillar el enchapado de la paleta.
- **Puente de cable SPI (Paleta $\rightarrow$ Antebrazo):**
  - Usar cable extraflexible de silicona multifilar (AWG 28 o AWG 30) o cinta plana para los 6 hilos (VCC, GND, SCK, MOSI, MISO, CS).
  - **Comba de seguridad obligatoria:** Dejar un lazo o bucle flojo de 4 a 6 cm de margen sobre el dorso de la muñeca.
  - Fijar el cable con una vuelta de cinta aisladora en la base del mango y otra en la muñeca antes de subir al antebrazo. Al quebrar la muñeca 90° hacia adelante y hacia atrás, el cable nunca debe tensarse ni hacer tope mecánico.
- **Sujeción del ESP32:**
  - Ajustar la Cápsula B con la banda elástica de velcro en el antebrazo, asegurando que quede firme para no desplazarse con la inercia del braceo pero sin cortar la circulación.
