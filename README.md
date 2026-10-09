# Paleta de ping pong inteligente

Un sensor en el mango de la paleta reconoce cada golpe, mide el angulo de la paleta en el impacto y si el jugador frena antes de la pelota, y muestra un consejo en el celular.

- **Plan de trabajo, modulos y tareas por clase:** [`docs/PLAN.md`](docs/PLAN.md)
- **Formatos de datos entre modulos:** [`docs/CONTRATOS.md`](docs/CONTRATOS.md)

## Estructura

| Carpeta | Que va | Modulo |
| --- | --- | --- |
| `firmware/paleta/` | Codigo de la placa (Arduino IDE) | A |
| `herramientas/` | Python: grabar sesiones, graficarlas, procesar la señal | B y D |
| `app/` | App web que se conecta a la paleta por Bluetooth | C |
| `hardware/` | Capsula en OpenSCAD | E |
| `datos/` | Sesiones grabadas. **No se suben a git**: van al Drive del grupo | Todos |
| `docs/` | Plan, contratos, protocolo de grabacion, criterios | Todos |

## Como arrancar

### Firmware (modulo A)

Placa: **ESP32S3 Dev Module**, con la misma configuracion que en el proyecto de las gafas. La camara no se usa.

Conexion del MPU6050 (modulo GY-521):

| MPU6050 | ESP32-S3 |
| --- | --- |
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 41 |
| SCL | GPIO 42 |

Antes de conectar, revisar en el pinout de su placa que los GPIO 41 y 42 esten libres. Si no, cambiar `PIN_SDA` y `PIN_SCL` en `paleta.ino`.

Abrir `firmware/paleta/paleta.ino`, cargarlo y abrir el monitor serie a **921600 baudios**.

### Herramientas en Python (modulos B y D)

```bash
cd herramientas
pip install -r requirements.txt
python ejemplo.py
python ver.py ../datos/crudos/ejemplo_sintetico.csv
```

Con la placa conectada:

```bash
python grabar.py --listar
python grabar.py --puerto COM5 --jugador mateo --golpe topspin_derecha
```

### App (modulo C)

Desde la carpeta raiz del proyecto:

```bash
python -m http.server 8000
```

Abrir `http://localhost:8000/app/` en Chrome y tocar **Simulador**. Para usarla en el celular con la placa real hace falta https: publicarla con GitHub Pages.
