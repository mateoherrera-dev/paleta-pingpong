# Reglas del repo para los asistentes de IA

Somos tres y cada uno trabaja con su propio asistente (Claude, Gemini). Este archivo es lo que todos tienen que respetar: `CLAUDE.md` y `GEMINI.md` solo lo importan, asi las reglas estan escritas en un solo lugar. Si una regla cambia, se cambia aca en un PR y se avisa por el grupo.

## El proyecto

Paleta de ping pong con un IMU (MPU-6500) y una ESP32-S3 que reconoce 4 golpes con TinyML (Edge Impulse), mide angulo de la cara, velocidad y pico de giro, y le manda un struct por BLE a una app web que da consejos. Solo se trabaja los viernes; el MVP es el viernes 13/11.

- Plan por viernes y roles: [`docs/PLAN.md`](docs/PLAN.md)
- Formatos entre modulos (ejes, CSV, struct BLE, signo del angulo): [`docs/CONTRATOS.md`](docs/CONTRATOS.md)
- Rangos y consejos por golpe: [`docs/GOLPES.md`](docs/GOLPES.md)

## Quien toca que

| Carpeta | Dueño | Notas |
| --- | --- | --- |
| `firmware/` | P1 · Hardware | Arduino IDE, ESP32S3 Dev Module (configuracion en el README) |
| `herramientas/segmentar.py`, modelo, `hardware/` | P2 · Datos | Edge Impulse, capsula |
| `app/`, `herramientas/orientacion.py`, `docs/GOLPES.md` | P3 · Tecnica | App web, angulo, criterios |
| `docs/PLAN.md`, `docs/CONTRATOS.md`, `README.md` | Los tres | Avisar antes de un cambio grande |

Si una tarea necesita tocar la zona de otro, hacerlo igual pero decirlo en el PR y mencionar al dueño.

## Como trabajar con git

1. **Antes de empezar:** `git switch main` y `git pull`. Nunca arrancar sobre un `main` viejo.
2. **Una rama por tarea**, cortada desde `main` y con nombre corto de lo que hace: `app-struct-binario`, `firmware-spi`, `docs-ventana-196`. Nada de ramas largas por modulo.
3. **Commits chicos**, uno por cambio, con mensaje en español que diga que hace ("Agregar...", "Corregir...").
4. **Pushear la rama y abrir un PR a `main`.** `main` esta protegida: no acepta push directo ni force push. Se puede mergear sin aprobacion, pero si el PR toca la zona de otro, esperar a que lo mire.
5. **Merge con "Create a merge commit".** La rama se borra sola al mergear.
6. Si al hacer pull o merge aparece un conflicto, resolverlo mirando los dos lados; nunca descartar cambios de otro sin preguntar.
7. Antes de irse cada viernes, todo lo que sirve tiene que estar pusheado en una rama (aunque el PR quede abierto).

## Convenciones

- **Texto en UTF-8** (lo fija `.editorconfig`). Los `.md` van **sin tildes** (la ñ si); el codigo y los comentarios pueden tener tildes.
- **Ejes, formatos y signos:** los define `docs/CONTRATOS.md`. Lo mas facil de romper sin que de error:
  - Signo del angulo: 0° = cara vertical, **negativo = cerrada** (mira a la mesa), **positivo = abierta** (mira al techo).
  - Ejes: X a lo largo del mango hacia la paleta, Z saliendo por la goma roja, Y = Z × X.
  - Struct BLE de 14 bytes, little-endian.
  - Ventana del modelo: 196 muestras (120 antes del impacto + 76 despues).
- **Un cambio de contrato** (formato, signo, ventana, struct) se discute entre los tres y se actualiza `CONTRATOS.md` en el mismo PR que el codigo.
- Si dos documentos se contradicen, no elegir uno en silencio: marcarlo en el PR.

## Que no va a git

- **Datos de sesiones** (`datos/`): van a la carpeta de Drive del grupo.
- **Binarios pesados o generados** (zips de modelos, librerias armadas, exports): no se suben salvo que los tres lo acuerden.
- Credenciales, tokens o mails personales en el codigo.

## Herramientas en Python

Se corren desde `herramientas/` (`pip install -r requirements.txt`). Para probar sin la placa: `python ejemplo.py` genera una sesion sintetica y `python prueba_orientacion.py` valida el calculo del angulo.
