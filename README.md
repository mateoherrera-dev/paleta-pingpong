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

Configuracion de la placa en el Arduino IDE (la camara no se usa):

- Placa: **ESP32S3 Dev Module**
- Flash Size: **16MB**
- PSRAM: **OPI PSRAM**
- Partition Scheme: **16M Flash (3MB APP/9.9MB FATFS)**
- Si se usa el USB nativo para el monitor serie: USB CDC On Boot → **Enabled**

Conexion del MPU-6500 por SPI (los nombres de la izquierda son los que trae impresos el modulo):

| MPU-6500 | ESP32-S3 | Para que |
| --- | --- | --- |
| VCC | 3V3 | Alimentacion |
| GND | GND | |
| SCL / SCLK | GPIO 14 | Reloj del bus |
| SDA / SDI | GPIO 21 | Datos placa → sensor (MOSI) |
| AD0 / SDO | GPIO 47 | Datos sensor → placa (MISO) |
| NCS | GPIO 41 | Elegir el sensor (CS) |
| INT | GPIO 42 | Aviso de muestra nueva |

Antes de cablear, revisar en el pinout de su placa que esos GPIO esten libres (que no los usen la camara, la PSRAM, la tarjeta SD ni el LED). Si no, cambiar los `PIN_...` al principio de `paleta.ino`. Sin el cable INT tambien anda: poner `USAR_INT = false` (lee cada 1 ms con el reloj de la placa).

Al arrancar, el monitor serie avisa si no encuentra el sensor (`WHO_AM_I = 0x00` o `0xFF`: revisar cables) o si no llega el aviso por INT.

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
