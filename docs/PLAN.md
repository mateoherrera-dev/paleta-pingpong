# Plan de trabajo

**Condiciones:** somos 3 y trabajamos solo los viernes, de 9 a 16 (a veces hasta las 18). Entre semana no hay trabajo de proyecto, salvo trámites cortos: compras e impresión 3D.

**Calendario:** hoy (viernes 2/10) es la clase 0. El MVP tiene que estar terminado el **viernes 13/11**. Después viene la fase 2, hasta la entrega final.

| Clase | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Viernes | 9/10 | 16/10 | 23/10 | 30/10 | 6/11 | **13/11 · MVP** |

No hay un viernes de colchón al final. El margen sale de dos lados: el horario de 16 a 18 de cada viernes, y el 13/11, que está pensado para cerrar y arreglar, no para agregar cosas.

**Objetivo del MVP:** alguien pega un golpe y el celular muestra **qué golpe fue, con qué ángulo pegó la paleta y si frenó antes de la pelota**, junto con un consejo.

**Definición de terminado del MVP:**
- Reconoce 4 golpes (topspin y empuje, de derecha y de revés) con **80 % de aciertos o más**, medido con gente que no se usó para entrenar.
- Muestra en el celular el ángulo en el impacto y si el pico de velocidad fue antes de pegar.
- Funciona sin cables a la compu: alcanza con un powerbank en el bolsillo.

YOLO y el análisis de postura van en la **fase 2**, después del 13/11.

---

## 1. Equipo y módulos

Los formatos de datos entre módulos están fijados en [`CONTRATOS.md`](CONTRATOS.md). Eso permite que cada uno avance por su lado durante la mañana y que a la tarde las partes encajen.

| Persona | Módulos | Qué hace | Suplente |
| --- | --- | --- | --- |
| **P1 · Hardware** | Firmware + cápsula | Sensor, detección de impactos, Bluetooth, modelo y métricas en la placa, cápsula en OpenSCAD | P2 |
| **P2 · Datos** | Datos + modelo | Grabación, protocolo, dataset, entrenamiento en Edge Impulse, medir precisión. En la fase 2, YOLO | P3 |
| **P3 · Técnica** | App + métricas + criterios | App, cálculo del ángulo y del pico de velocidad en Python, criterios de técnica, consejos, contacto con el jugador de referencia | P1 |

### Reglas

- **El suplente sabe cómo funciona el módulo** que cubre, por si el dueño falta un viernes.
- **Los tres graban datos.** La grabación es una actividad de grupo, no del módulo de datos solo.
- **Integrar todos los viernes.** Cada viernes a la tarde se prueba de punta a punta lo que haya, aunque sea con datos falsos.
- **Los contratos no se cambian solos:** se habla entre los tres y se actualiza `CONTRATOS.md`.
- **Git:** una rama por persona (`firmware`, `datos`, `app`), y se pasa a `main` cuando anda. Commit antes de irse cada viernes.

---

## 2. Cómo es un viernes

Las tareas que necesitan a los tres juntos (grabar, integrar) van a la tarde. A la mañana cada uno avanza en su módulo.

| Horario | Qué se hace |
| --- | --- |
| 9:00 – 9:20 | Arranque: qué quedó del viernes pasado, qué hito tenemos que mostrar hoy |
| 9:20 – 12:30 | **Trabajo por módulos**, cada uno en lo suyo |
| 12:30 – 13:30 | Almuerzo |
| 13:30 – 15:00 | **Bloque de grupo:** grabación, pruebas con gente o integración |
| 15:00 – 15:45 | Prueba de punta a punta y control del hito del día |
| 15:45 – 16:00 | Cierre: commit, tablero, compras y tareas del próximo viernes |
| 16:00 – 18:00 | **Colchón:** solo para lo atrasado, no para cosas nuevas |

**Para grabar se necesitan los tres:** uno juega, otro le tira pelotas (de a muchas seguidas, sin pelotear) y el tercero maneja la compu y el nombre de cada archivo. Después rotan.

---

## 3. Clase 0: hoy

### Organización (los tres, primera hora)

- [ ] Confirmar quién es P1, P2 y P3.
- [ ] **Comprar hoy por internet**, para que llegue antes del viernes 9/10: **2 MPU6050** (GY-521, uno de repuesto), cables dupont hembra-hembra y precintos.
- [ ] Crear el repo en GitHub, subir esta carpeta y dar acceso a los tres.
- [ ] Crear la carpeta de Drive para los datos.
- [ ] Pasar las tareas de este plan a un tablero (GitHub Projects o Trello).
- [ ] **Confirmar una mesa de ping pong disponible los viernes a la tarde**, o una red portátil para usar en cualquier mesa. Conseguir 2 paletas y una bolsa de pelotas: para grabar de a muchas seguidas hacen falta 20 o más.
- [ ] Averiguar dónde imprimir en 3D y cuánto tarda (la cápsula se imprime entre la clase 3 y la 4).
- [ ] Buscar un jugador de referencia que pueda venir **un viernes a la tarde** (clase 4).

### Código (sin el sensor todavía)

| Quién | Tarea | Listo cuando… |
| --- | --- | --- |
| **P1** | Configurar el Arduino IDE y cargar `firmware/paleta/paleta.ino` en una placa | El monitor serie muestra `No encuentro el MPU6050`: compila, carga y corre |
| **P1** | Confirmar en el pinout de la placa que los GPIO 41 y 42 estén libres | Pines confirmados, o cambiados en el `.ino` |
| **P2** | Instalar las dependencias de Python, correr `ejemplo.py` y `ver.py` | Se ve el gráfico con 6 golpes marcados |
| **P2** | Escribir el protocolo de grabación (`docs/PROTOCOLO.md`): cuántos golpes, en qué orden, cómo se nombran los archivos | Protocolo escrito |
| **P3** | Abrir la app con el simulador y publicarla en GitHub Pages | Abre en el celular desde un link |
| **P3** | Mirar tutoriales de los 4 golpes y armar un borrador de criterios | Tabla borrador en `docs/` |

---

## 4. Fase 1: MVP, viernes por viernes

### Clase 1 · Viernes 9/10 · Señal real

| P1 | P2 | P3 |
| --- | --- | --- |
| Conectar el MPU6050, confirmar 1000 Hz sin pérdidas y alinear ejes. Atar el sensor a la paleta con precintos | Herramientas listas con datos reales. Ajustar el umbral de impacto con lo que se grabe a la tarde | Empezar el cálculo del ángulo en Python (filtro Madgwick) con las primeras grabaciones |

**Tarde:** 30–40 minutos de golpes sueltos grabados, de los tres.
**Hito:** en la compu se ven golpes reales con los impactos bien marcados.

### Clase 2 · Viernes 16/10 · Grabación grande

| P1 | P2 | P3 |
| --- | --- | --- |
| Bluetooth: al detectar un impacto, mandar un evento con el formato del contrato (valores falsos) | Script que corta las ventanas y las exporta para Edge Impulse | Conectar la app a la placa real |

**Tarde: la grabación grande, la tarea más importante del plan.** Los tres, cada uno **50 golpes de cada tipo**. Son unos 600 golpes. Con pelotas tiradas de a muchas, entra en 1:30–2 h.
**Hito:** dataset v1 en el Drive y un golpe real que aparece en el celular por Bluetooth.

### Clase 3 · Viernes 23/10 · Primer modelo

| P1 | P2 | P3 |
| --- | --- | --- |
| Integrar la librería de Edge Impulse en la placa con el primer modelo. Terminar el diseño de la cápsula | Entrenar el modelo y medir la precisión dejando a una persona afuera del entrenamiento | Ángulo y pico de velocidad calculados sobre todo el dataset |

**Tarde:** grabar a **3–5 compañeros de la facu**, unos 10 minutos cada uno. Sirven para medir el modelo con gente nueva y suman datos de los golpes que más se confunden.
**Hito:** precisión medida con gente nueva.
- **80 % o más:** seguimos.
- **Entre 60 y 80 %:** más datos de los golpes que se confunden.
- **Menos de 60 %:** bajamos a 3 golpes.

**Durante la semana:** mandar a imprimir la cápsula.

### Clase 4 · Viernes 30/10 · Integración

**Mañana, los tres juntos:** modelo corriendo en la placa (P1 + P2), ángulo y pico de velocidad pasados al firmware (P1 + P3), app mostrando datos reales (P3).
**Tarde:** sesión con el **jugador de referencia**.
**Hito:** golpe real → el celular muestra el tipo, el ángulo y si frenó. Es el MVP en versión cruda.

### Clase 5 · Viernes 6/11 · Técnica y usuarios

| P1 | P2 | P3 |
| --- | --- | --- |
| Cápsula montada, con powerbank | Reentrenar con todos los datos, incluidos los del jugador de referencia | Criterios ajustados con los datos del jugador de referencia y consejos finales |

**Tarde:** compañeros que no son del grupo usan la paleta: medimos aciertos y anotamos qué les resulta confuso.
**Al terminar el día se congelan las funciones del MVP.** Desde acá, solo arreglos.
**Hito:** alguien de afuera usa la paleta y recibe consejos.

### Clase 6 · Viernes 13/11 · MVP terminado

- **Mañana:** arreglar lo pendiente de la semana anterior.
- **Tarde:** medir los números finales (precisión con gente nueva, pruebas con usuarios), ensayar la demo y **grabar un video de la demo funcionando**, por si en vivo algo falla.

**Hito: MVP terminado.**

### Si nos atrasamos, recortamos en este orden

1. Cápsula impresa: se presenta con el sensor atado con precintos.
2. Consejos por voz: quedan solo en pantalla.
3. Pico de velocidad: queda solo el ángulo.
4. Cuarto golpe: bajamos a 3.

---

## 5. Fase 2: video y postura (después del 13/11)

Hasta la entrega final. Fecha a confirmar.

### El video de la entrega

**No hace falta filmar las sesiones de grabación de datos.** YOLO-pose ya viene entrenado y no necesita esos videos para aprender. Para la entrega alcanza con **un video bien filmado**:

- **Con la paleta con sensor puesta.** Así el video muestra las dos cosas juntas: el esqueleto de YOLO-pose y, en cada golpe, el tipo, el ángulo y la velocidad que midió la paleta. El video y el sensor se sincronizan con el sonido del impacto.
- **De costado, con el celular a la altura de la cadera, a unos 3 m.** Es la toma donde mejor se ven rodillas, codo y tronco, y tiene que coincidir con el ángulo de los clips de profesionales.
- **Con buena luz y el jugador entero en cuadro.**
- **Con varios golpes de cada tipo:** de un jugador del grupo y, si se puede, del jugador de referencia, para comparar.

### Comparación de postura con profesionales

1. **Juntar clips.** De 5 a 10 videos de entrenadores o profesionales mostrando cada golpe **de costado**, idealmente en cámara lenta. Los tutoriales de técnica suelen tener exactamente esa toma.
2. **Correr YOLO-pose** sobre cada clip. Devuelve 17 puntos del cuerpo por cuadro: hombros, codos, muñecas, caderas, rodillas y tobillos.
3. **Calcular ángulos:** rodilla (cadera–rodilla–tobillo), codo (hombro–codo–muñeca) e inclinación del tronco.
4. **Marcar el momento del impacto** en cada clip. En los de profesionales, a mano o con el sonido. En el nuestro, con el sensor.
5. **Armar rangos de referencia.** Por ejemplo, la rodilla de un profesional en el impacto del topspin de derecha está entre X° y Y°, sacado del promedio de los clips.
6. **Comparar** al usuario con esos rangos: "flexionás 20° menos las rodillas que la referencia".

```python
from ultralytics import YOLO
import numpy as np

modelo = YOLO("yolo11n-pose.pt")

def angulo(a, b, c):
    """Ángulo en el punto b, en grados."""
    ba, bc = a - b, c - b
    coseno = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(coseno, -1, 1)))

for cuadro in modelo("topspin_profesional.mp4", stream=True):
    if cuadro.keypoints is None or len(cuadro.keypoints.xy) == 0:
        continue
    k = cuadro.keypoints.xy[0].numpy()  # 17 puntos (x, y) de la primera persona detectada
    rodilla = angulo(k[12], k[14], k[16])  # cadera, rodilla y tobillo derechos
    codo = angulo(k[6], k[8], k[10])       # hombro, codo y muñeca derechos
```

**Límites:**
- Con una sola cámara los ángulos son aproximados, porque dependen del punto de vista. Por eso todos los videos tienen que filmarse desde el mismo lado.
- Si en el cuadro aparecen dos personas, hay que quedarse con la del jugador (la más grande o la más cercana).
- Para zurdos, espejar el video o usar los puntos del lado izquierdo.

---

## 6. Riesgos y plan B

| Riesgo | Plan B |
| --- | --- |
| El MPU6050 no llega para el 9/10 | Comprarlo en una casa de electrónica en la semana. Mientras tanto, P1 avanza con el Bluetooth y P2 con datos de prueba |
| No hay mesa disponible un viernes | Red portátil en cualquier mesa. Para grabar golpes alcanza con una mesa y alguien que tire pelotas |
| Falta uno de los tres un viernes | El suplente cubre su módulo. Si es un viernes de grabación, se graba con dos y se completa la semana siguiente |
| La detección de impactos falla | Pegar un disco piezoeléctrico en la paleta: detecta el golpe con la pelota sin ambigüedad |
| El modelo acierta poco | Bajar a 3 golpes, o separarlo en dos decisiones: derecha/revés (muy fácil) y topspin/empuje |
| Bluetooth da problemas | Para la demo, mandar los eventos por WiFi o por cable a la compu |
| La placa en el mango molesta para jugar | Placa en una pulsera y solo el sensor en el mango, con un cable fino |
| El jugador de referencia no puede venir | Criterios sacados de tutoriales y de los ángulos de los clips de profesionales |
