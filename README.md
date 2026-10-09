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

Conexion del MPU-6500 por SPI (con los nombres que trae impresos el modulo):

| Modulo MPU-6500 | Funcion | ESP32-S3 |
| --- | --- | --- |
| VCC | Alimentacion | 3V3 |
| GND | Masa | GND |
| SCL | SCK (reloj) | GPIO 42 |
| SDA | MOSI | GPIO 41 |
| AD0 | MISO | GPIO 14 |
| NCS | CS | GPIO 21 |
| INT | Dato listo (interrupcion) | GPIO 1 |
| FSYNC, EDA, ECL | - | Sin conectar |

Antes de conectar, revisar en el pinout de su placa que esos GPIO esten libres. Si no, cambiar los `PIN_...` al principio de `paleta.ino`. Al arrancar, el monitor serie tiene que mostrar `# MPU-6500 encontrado (WHO_AM_I = 0x70)`.

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
