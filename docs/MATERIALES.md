# Lista de materiales

Como solo trabajamos los viernes, **lo que no llega a tiempo nos hace perder una semana entera**. Por eso conviene comprar hoy todo lo urgente y tambien los repuestos baratos.

## Como comprar en Mercado Libre

- Filtrar por **envio Full** o "llega mañana": suele llegar en 1–2 dias. Los envios normales pueden tardar una semana.
- Juntar todo lo posible en **un mismo vendedor** para pagar un solo envio.
- Mandarlo a una direccion donde haya alguien durante la semana.
- **Revisar si el MPU6050 viene con los pines soldados.** Si vienen sueltos, hay que soldarlos.

## 1. Urgente: tiene que llegar antes del viernes 9/10

| ✓ | Material | Cant. | Buscar en ML | Para que / ojo con |
| --- | --- | --- | --- | --- |
| [ ] | Modulo MPU6050 | 2 | `MPU6050 GY-521` | Uno de repuesto. Preferir con pines soldados |
| [ ] | Cables dupont hembra-hembra, 20 cm | 1 pack de 40 | `cables dupont hembra hembra 20cm` | Conectar el sensor a la placa |
| [ ] | Cables dupont macho-hembra, 20 cm | 1 pack de 40 | `cables dupont macho hembra 20cm` | Por si hace falta usar protoboard |
| [ ] | **Cable USB de datos largo, 2–3 m** | 1 | `cable usb c datos 3 metros` | Para grabar mientras se juega: la placa manda los datos a la compu por este cable. **Tiene que ser de datos, no solo de carga**, y con la ficha que tenga su placa |
| [ ] | Precintos chicos | 1 pack | `precintos 100mm` | Atar el sensor a la paleta en las primeras pruebas |
| [ ] | Cinta de tela o aisladora | 1 | `cinta de tela` | Fijar cables al mango |
| [ ] | Pelotas de ping pong 40+ | 50 | `pelotas ping pong 40+ x 50` | Para grabar tirando de a muchas seguidas. Sirven las de entrenamiento |
| [ ] | Paleta de ping pong economica | 1 o 2 | `paleta ping pong` | Una para ponerle el sensor (se va a pegar y atar cosas). Si ya tienen, no hace falta |
| [ ] | Red retractil | 1 | `red ping pong retractil` | **Solo si la mesa de la facu no tiene red** |

## 2. Repuestos y plan B: baratos, conviene comprarlos ya

| ✓ | Material | Cant. | Buscar en ML | Para que |
| --- | --- | --- | --- | --- |
| [ ] | Disco piezoelectrico 27 mm | 3 | `piezo electrico 27mm` | Plan B si la deteccion de impactos con el acelerometro falla |
| [ ] | Resistencias de 1 MΩ | 5 | `resistencia 1M 1/4w` | Van con el piezo |

## 3. Para la capsula y la paleta sin cables (antes del 30/10)

| ✓ | Material | Cant. | Buscar en ML | Para que / ojo con |
| --- | --- | --- | --- | --- |
| [ ] | Powerbank chico | 1 | — | Alimentar la placa en el MVP. Seguro alguno tiene. **Ojo:** muchos se apagan solos cuando el consumo es bajo. Probarlo antes con la placa encendida 10 minutos |
| [ ] | Cable USB corto, 30–50 cm | 1 | `cable usb c corto 30cm` | Del powerbank a la placa |
| [ ] | Abrojo (velcro) con adhesivo | 1 m | `abrojo adhesivo` | Sujetar el cable al brazo o armar una pulsera |
| [ ] | Goma EVA | 1 plancha | `goma eva` | Amortiguar la placa dentro de la capsula |
| [ ] | Tornillos M2 × 8 mm | 1 bolsita | `tornillos m2 x 8` | Cerrar la capsula |
| [ ] | Impresion 3D de la capsula | — | Servicio de impresion o impresora de alguien | Pedir **PETG**: aguanta mejor los golpes que el PLA |

### Opcional: bateria en la paleta en vez de powerbank

Solo si quieren la paleta sin ningun cable. Agrega peso y armado.

| ✓ | Material | Cant. | Buscar en ML | Ojo con |
| --- | --- | --- | --- | --- |
| [ ] | Bateria LiPo 3,7 V, 500 mAh, con conector JST | 1 | `bateria lipo 3.7v 500mah` | — |
| [ ] | Cargador TP4056 con proteccion, USB-C | 1 | `tp4056 usb c proteccion` | Que diga "con proteccion" (tiene 6 pines de conexion, no 4) |
| [ ] | Elevador de tension MT3608 | 1 | `mt3608 step up` | La placa necesita 5 V en el pin de 5V y la bateria da 3,7 V. **Hay que regular la salida a 5 V con un multimetro antes de conectar la placa** |
| [ ] | Interruptor deslizante chico | 2 | `switch deslizante mini` | Encender y apagar |

## 4. Fase 2: video final

| ✓ | Material | Cant. | Buscar en ML | Para que |
| --- | --- | --- | --- | --- |
| [ ] | Tripode para celular | 1 | `tripode celular` | Filmar el video final de costado, a la altura de la cadera. Si alguien tiene, no hace falta |

## Herramientas (probablemente esten en el laboratorio de la facu)

Soldador y estaño, multimetro, pinza de corte, termocontraible. Si los pines del MPU6050 vienen sueltos, el soldador hace falta **el viernes 9/10**.

## Ya tenemos

- Placas ESP32-S3 N16R8 (sin usar la camara)
- Celular
- Compu
- Mesa de ping pong (a confirmar)

## Mas adelante, solo si hace falta

- **Sensor con mas rango de giro** (por ejemplo LSM6DSV16X, hasta 4000 °/s), si el MPU6050 se satura en los topspins rapidos. Puede ser dificil de conseguir en Argentina: lo vemos en la clase 1 con los primeros datos.
- **Seeed XIAO ESP32-S3**, si la placa en el mango molesta demasiado para jugar.
