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
| **P1 · Hardware** | Firmware + cápsula | Sensor MPU-6500 por SPI a 1000 Hz, detección de impactos por jerk/piezo, BLE por eventos, inferencia Edge Impulse en placa, cápsula en OpenSCAD | P2 |
| **P2 · Datos** | Datos + modelo | Grabación por UART (cable USB a 921600 baudios), protocolo, dataset, entrenamiento en Edge Impulse, evaluación de precisión. En fase 2, YOLO-pose | P3 |
| **P3 · Técnica** | App + métricas + criterios | App web BLE, cálculo cinemático ($v = \omega \cdot L$), ángulo de cara previa al choque (Madgwick), criterios de técnica y consejos | P1 |

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
| Conectar MPU-6500 por SPI a $\ge 1\text{ MHz}$. Leer registro `WHO_AM_I` (`0x70`). Configurar muestreo a 1000 Hz por FIFO/interrupción y atar sensor a la paleta | Script de guardado masivo en CSV. Validar que la derivada de aceleración ($\Delta a / \Delta t$) aísle el impacto real de los swings al aire | Algoritmo de orientación (Madgwick/Mahony) en Python procesando las ráfagas capturadas |

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
| Exportar modelo C++ de Edge Impulse, integrarlo en el firmware y pasar a alimentación por Powerbank (verificar que no corte por bajo consumo) | Entrenar modelo en Edge Impulse, optimizar cuantización INT8 y medir matriz de confusión | Conectar app web con el BLE real: parsear paquete de 20 bytes al recibir impacto |

**Tarde:** Capturar a 3–5 compañeros de la facultad con la paleta inalámbrica para validar precisión fuera del dataset de entrenamiento.
**Hito:** Precisión medida en hardware real.
- $\ge 80\%$: se avanza a integración final.
- $60\% - 80\%$: reentrenamiento con golpes ambiguos.
- $< 60\%$: reducir alcance a 3 golpes.

**Durante la semana:** Enviar cápsula a imprimir en 3D.

### Clase 4 · Viernes 30/10 · Integración Total y Jugador de Referencia

**Mañana (los tres):** Sensor en paleta alimentado por powerbank → Inferencia local en ESP32-S3 → Disparo BLE de métricas ($v$, ángulo, tipo) → App celular mostrando métricas y feedback.
**Tarde:** Sesión de pruebas y validación con el **jugador de referencia**.
**Hito:** Golpes reales recibidos en el celular sin cables ni compu intermediaria.

### Clase 5 · Viernes 6/11 · Ensamble y Ajuste Fino

| P1 | P2 | P3 |
| --- | --- | --- |
| Montar electrónica final en la cápsula impresa y verificar alivio de tensión del cable USB al bolsillo | Calibrar pesos y reentrenar modelo agregando las muestras del jugador experto | Pulir reglas heurísticas de consejos en base al perfil del jugador de referencia |

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
