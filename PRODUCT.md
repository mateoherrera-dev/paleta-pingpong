# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Jugadores de tenis de mesa (intermedios a avanzados) que buscan corregir su técnica milimétrica sin detener el juego, entrenadores que monitorean el progreso biomecánico en cancha, y evaluadores técnicos que validan la precisión del modelo TinyML.

## Product Purpose

Transformar una paleta de ping-pong convencional en una herramienta inteligente de diagnóstico y entrenamiento en tiempo real mediante un IMU (MPU-6500) y un microcontrolador ESP32-S3. La aplicación web se conecta por Web Bluetooth (BLE), clasifica 4 golpes fundamentales (Topspin Derecha, Topspin Revés, Empuje Derecha, Empuje Revés) con TinyML (Edge Impulse), calcula métricas clave del impacto (ángulo de la cara, velocidad tangencial y timing de aceleración) y brinda retroalimentación instantánea visual y por voz.

## Positioning

**FIND YOUR EDGE**: El "entrenador de rincón" (Corner Coach) que te canta la justa sin vueltas al costado de la mesa. A diferencia de sistemas de laboratorio con cinemática abstracta o cámaras costosas, DOC procesa directamente en el edge físico (la paleta) y entrega consejos accionables inmediatos (*"Cerrá la cara 10°"*, *"Acelerá antes"*).

## Operating Context

Entorno de entrenamiento físico en mesa de tenis de mesa (club, gimnasio o sala de práctica). El dispositivo móvil o tablet se coloca apoyado al borde de la cancha o en una mesa lateral mientras el jugador golpea pelotas de práctica continuas. Transmisión BLE constante con latencia imperceptible tras cada impacto.

## Capabilities and Constraints

- **Conexión BLE:** Web Bluetooth API bajo servicio UART nórdico (UUID `6e400001-b5a3-f393-e0a9-e50e24dcca9e`).
- **Formato de datos (docs/CONTRATOS.md):** Struct binario little-endian de 14 o 20 bytes por evento de impacto.
- **Convención de ángulo:** 0° = cara perfectamente vertical; **negativo = cerrada** (mira hacia la mesa); **positivo = abierta** (mira hacia el techo).
- **Orientación espacial:** Eje X a lo largo del mango hacia la paleta, eje Z saliendo por la goma roja ($+Z$), eje Y perpendicular ($Z \times X$).
- **Ventana del modelo TinyML:** 196 muestras a 200 Hz (120 antes del impacto + 76 después).
- **Modos de uso:**
  1. *Modo Libre:* Telemetría instantánea de ángulo, velocidad, timing y score técnico (1-100 pts) con visor 3D interactivo (Three.js) y voz sintética.
  2. *Modo Tutorial:* Desafíos biomecánicos paso a paso (*Ángulo de contacto*, *Efecto brushing*, *Aceleración de látigo*).
  3. *Modo Benchmark:* Tanda de tiros configurables (10, 12, 20 o libre) para medir tasa de acierto y matriz de confusión contra el umbral del MVP (80%).

## Brand Commitments

- **Nombre:** DOC (Datos y Orientación en Cancha).
- **Lema:** FIND YOUR EDGE.
- **Sello industrial (Ball Stamp):** Sello oficial ITTF `DOC ★★★ 40+` estampado con tinta azul marino grafito mate.
- **Paleta de marca (docs/IDENTIDAD.md):**
  - Naranja Pelota Torneo: `#ff7700` (acento primario enérgico, score, estado activo).
  - Azul Torneo ITTF / Noche Cancha: `#070d18` / `#0c1527` (fondo inmersivo y superficies HUD).
  - Verde Acierto: `#10b981` (score $\ge 80$, ángulo óptimo, aciertos de clasificación).
  - Rojo Goma / Alerta: `#f43f5e` / `#dc2626` (falla crítica, goma de revés $+Z$).
- **Tono de voz:** Directo, exigente, cercano y sin jerga técnica frente al jugador.

## Evidence on Hand

- Código de frontend completo en [app/index.html](app/index.html) con visor 3D Three.js y síntesis de voz (Web Speech API).
- Modelo 3D de paleta reglamentaria [hardware/paleta.glb](hardware/paleta.glb).
- Filtro de orientación validado en [herramientas/orientacion.py](herramientas/orientacion.py) y [herramientas/prueba_orientacion.py](herramientas/prueba_orientacion.py) con error < 0.4° frente a tolerancia de 3.0°.
- Dataset sintético y evaluador en [herramientas/ejemplo.py](herramientas/ejemplo.py).
- Contratos de integración consolidados en [docs/CONTRATOS.md](docs/CONTRATOS.md) y rangos biomecánicos en [docs/GOLPES.md](docs/GOLPES.md).

## Product Principles

1. **Feedback en 1 segundo:** El jugador no puede leer gráficos densos entre pelota y pelota; el dato central (ángulo/score) y el consejo por voz deben llegar de forma instantánea.
2. **El deporte lidera sobre la matemática:** La interfaz habla de "cerrar la cara", "aceleración temprana" y "score técnico", ocultando cuaterniones o capas densas de red neuronal.
3. **Cero fricción en cancha:** Flujo continuo sin necesidad de tocar la pantalla con las manos transpiradas; reinicio ágil y visualización nítida a 2 metros de distancia.
4. **Fidelidad al contrato físico:** Signos de ángulo, ejes de coordenadas y tolerancias mecánicas se respetan estrictamente entre firmware, TinyML y frontend.

## Accessibility & Inclusion

- Contraste visual elevado para pantallas móviles en entornos con iluminación de club o gimnasio.
- Text-to-Speech (Web Speech API) configurable para que el usuario reciba correcciones auditivas sin mirar la pantalla.
- Compatibilidad con navegación por teclado y soporte de `prefers-reduced-motion` para usuarios sensibles al movimiento.
