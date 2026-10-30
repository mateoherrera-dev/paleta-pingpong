// Paleta de ping pong inteligente — firmware de la clase 4
//
// Lee el MPU-6500 por SPI 1000 veces por segundo y manda cada muestra por el puerto serie:
//   t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
// Formato, unidades y ejes: docs/CONTRATOS.md
//
// Placa: ESP32S3 Dev Module. Configuración completa del Arduino IDE en el README.
// La cámara no se usa: se puede desconectar.
//
// En cada impacto, 76 ms después (cuando ya está completa la ventana del modelo), arma el struct
// BlePayload de 14 bytes y lo manda por BLE a la app (docs/CONTRATOS.md, sección 5).

#include <SPI.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>
#include "ml_inference.h"

// Pines SPI del MPU-6500 (pin del módulo → función). Revisar en el pinout de la placa que estén libres.
// SCL y SDA quedan en los GPIO que usaba el I2C: si hay que volver a I2C, esos dos cables no se mueven.
const int PIN_SCK = 42;   // SCL → reloj
const int PIN_MOSI = 41;  // SDA → datos de la placa al sensor
const int PIN_MISO = 14;  // AD0 → datos del sensor a la placa
const int PIN_CS = 21;    // NCS → chip select
const int PIN_INT = 1;    // INT → avisa que hay una muestra nueva

// true: se lee cada vez que el sensor avisa por INT que tiene una muestra nueva. Va al ritmo del
// reloj del sensor, así no se repiten ni se saltean muestras (idea tomada del PR #5 de Mateo).
// false: plan B, se lee cada 1000 µs con micros() y el cable INT no hace falta.
const bool USAR_INT = true;

// El MPU-6500 acepta hasta 1 MHz para escribir registros y hasta 20 MHz para leer datos.
// Con cables dupont largos conviene quedarse en 1 MHz: leer una muestra tarda ~120 µs.
const SPISettings AJUSTES_SPI(1000000, MSBFIRST, SPI_MODE3);

const uint32_t PERIODO_US = 1000;  // 1000 Hz

// Escalas para ±16 g y ±2000 °/s
const float LSB_POR_G = 2048.0f;
const float LSB_POR_DPS = 16.4f;

// Offset del acelerómetro de ESTE módulo, en g y en los ejes del módulo: se resta a cada lectura.
// Se mide con herramientas/calibrar.py y hay que volver a medirlo cada vez que se cambia el módulo.
// Módulo de repuesto soldado con chicotes (clase 3), calibrado el 23/10 con 6 posiciones
// (datos/pruebas/2026-10-23_094814_calibracion_libre.csv, error residual 0,021 g).
// Su eje Z también lee de más (+0,26 g; la hoja de datos admite ±0,08 g): el de la clase 1 tenía
// +0,46 g (0.033 / -0.012 / 0.460). Parece del lote de módulos: calibrar siempre cada uno.
const float OFFSET_AX_G = 0.028f;
const float OFFSET_AY_G = -0.002f;
const float OFFSET_AZ_G = 0.264f;

// Detección de impacto por Jerk: cuánto cambia el vector aceleración entre dos muestras seguidas,
// |a[k] - a[k-1]|, en g por muestra (g/ms a 1000 Hz). El swing cambia la aceleración en
// 30-100 ms; el choque con la pelota, en 1-2 ms (PLAN.md, 7.2).
// Es la resta de vectores y no la de módulos (|a[k]| - |a[k-1]|) porque si la vibración del
// choque es de costado respecto de la aceleración del swing, el módulo casi no cambia: con la
// resta de módulos se perdían los golpes sintéticos de las pruebas y 2 de 3 toques reales.
// Medido el 23/10 con el módulo firme en la Pieza A (datos/pruebas/2026-10-23_104715_umbral_libre.csv):
// pelota cayendo desde 30 cm → 1,28 a 18,5 g; swings al aire hasta 606 °/s → 0,06 a 0,17 g.
// 1,0 g agarra los golpes suaves (empujes) con mucho margen sobre los swings. Con el montaje
// provisorio del 16/10 (dupont colgando) los swings llegaban a 1,02 g y se usaba 1,5.
// Revisarlo con herramientas/ver.py --umbral si cambia el montaje.
const float UMBRAL_JERK_G = 1.0f;
const uint32_t REFRACTARIO_US = 300000;  // después de un impacto, ignorar 300 ms

// Distancia del plano inferior del pomo (donde apoya el sensor) al centro de la cabeza de la paleta,
// medida con regla el 16/10 (docs/CONTRATOS.md). Para la velocidad tangencial v = ω · L (vel_kmh).
const float L_PALETA_M = 0.18f;

// Velocidad y pico de giro: la misma cuenta que herramientas/cinematica.py (P3).
// ω del swing = hypot(gy, gz) (girar sobre el mango, eje X, no hace avanzar la paleta),
// suavizado con un promedio de 5 muestras centrado para que la vibración del golpe no cuente.
// L es la distancia del eje de giro (muñeca/codo, no el sensor) al centro de la paleta:
// 0,30 m es el provisorio de cinematica.py hasta medirlo con --estimar-L.
const float L_GIRO_M = 0.30f;
const int VEL_ANTES = 5;       // la velocidad es el promedio de ω en los 5 ms antes del impacto
const int PICO_ANTES = 200;    // el pico de giro se busca desde 200 ms antes del impacto...
const int PICO_DESPUES = 50;   // ...hasta 50 ms después
const int MUESTRAS_DESPUES = 76;  // se espera hasta completar la ventana del modelo (120 + 76)

// Últimas muestras de ω del swing, en °/s. 512 alcanzan para 200 antes + 76 después del impacto.
const int OMEGA_N = 512;
float omega[OMEGA_N];
uint32_t muestras = 0;         // muestras leídas desde que arrancó: la k va en omega[k % OMEGA_N]
uint32_t muestraImpacto = 0;   // número de muestra del último impacto
bool golpePendiente = false;   // hubo un impacto y todavía no se mandó por BLE

// BLE: mismo servicio y característica que espera la app (app/index.html, filtro por nombre "Paleta")
const char *NOMBRE_BLE = "Paleta";
const char *UUID_SERVICIO = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
const char *UUID_NOTIFY = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";

// Evento de golpe (docs/CONTRATOS.md, sección 5): 14 bytes, little-endian (el ESP32 ya lo es)
#pragma pack(push, 1)
struct BlePayload {
  uint32_t timestamp;     // ms desde el arranque, en el impacto
  uint16_t numero_golpe;  // contador de impactos de la sesión
  uint8_t tipo_golpe;     // 0=TD, 1=TR, 2=ED, 3=ER, 4=desconocido o ruido
  uint8_t confianza;      // 0 a 100
  int16_t vel_kmh;
  int16_t ang_deg;        // − cerrada, + abierta
  int16_t pico_ms;        // − el pico de giro fue antes del impacto
};
#pragma pack(pop)
static_assert(sizeof(BlePayload) == 14, "BlePayload tiene que medir 14 bytes (CONTRATOS.md)");

BLECharacteristic *caracteristica = nullptr;
volatile bool celularConectado = false;
uint16_t golpes = 0;

class AlConectar : public BLEServerCallbacks {
  void onConnect(BLEServer *servidor) override {
    celularConectado = true;
  }
  void onDisconnect(BLEServer *servidor) override {
    celularConectado = false;
    BLEDevice::startAdvertising();  // para que el celular se pueda volver a conectar
  }
};

uint32_t proximaMuestra = 0;
uint32_t ultimaLectura = 0;   // micros() de la última muestra leída
uint32_t ultimoMensaje = 0;   // para no mandar avisos por serie más de una vez por segundo
uint32_t ultimoImpacto = 0;
float axAnterior = 0, ayAnterior = 0, azAnterior = 0;
bool hayAnterior = false;

volatile uint32_t avisos = 0;  // pulsos de INT desde que arrancó: los cuenta la interrupción
uint32_t avisosLeidos = 0;     // hasta qué aviso ya se leyó
uint32_t perdidas = 0;         // muestras que el sensor tuvo listas y no se llegaron a leer

// La interrupción solo cuenta el aviso. El SPI se lee en loop(), nunca acá adentro.
void IRAM_ATTR alAvisarElSensor() {
  avisos++;
}

void escribirRegistro(uint8_t registro, uint8_t valor) {
  SPI.beginTransaction(AJUSTES_SPI);
  digitalWrite(PIN_CS, LOW);
  SPI.transfer(registro & 0x7F);  // bit 7 en 0: escritura
  SPI.transfer(valor);
  digitalWrite(PIN_CS, HIGH);
  SPI.endTransaction();
}

uint8_t leerRegistro(uint8_t registro) {
  SPI.beginTransaction(AJUSTES_SPI);
  digitalWrite(PIN_CS, LOW);
  SPI.transfer(registro | 0x80);  // bit 7 en 1: lectura
  uint8_t valor = SPI.transfer(0x00);
  digitalWrite(PIN_CS, HIGH);
  SPI.endTransaction();
  return valor;
}

// Devuelve en `id` el WHO_AM_I leído, para diagnosticar el cableado si algo falla
bool iniciarMPU(uint8_t &id) {
  escribirRegistro(0x6B, 0x80);  // PWR_MGMT_1: reset completo
  delay(100);
  escribirRegistro(0x68, 0x07);  // SIGNAL_PATH_RESET: reset de giro, acelerómetro y temperatura (recomendado en SPI)
  delay(100);
  escribirRegistro(0x6B, 0x01);  // PWR_MGMT_1: despertar, reloj del giroscopio
  delay(50);
  escribirRegistro(0x6A, 0x10);  // USER_CTRL: apagar la interfaz I2C, solo SPI

  // 0x70 = MPU-6500. 0x71 y 0x73 = MPU-9250 / MPU-9255 (el mismo sensor con magnetómetro): también sirven.
  // 0x00 o 0xFF = el sensor no contesta: revisar MISO (AD0), CS (NCS) y la alimentación.
  id = leerRegistro(0x75);  // WHO_AM_I
  if (id != 0x70 && id != 0x71 && id != 0x73) return false;

  escribirRegistro(0x1A, 0x01);  // CONFIG: filtro del giro de 184 Hz, muestreo interno a 1 kHz
  escribirRegistro(0x19, 0x00);  // SMPLRT_DIV: 1 kHz / (1 + 0)
  escribirRegistro(0x1B, 0x18);  // GYRO_CONFIG: ±2000 °/s
  escribirRegistro(0x1C, 0x18);  // ACCEL_CONFIG: ±16 g
  escribirRegistro(0x1D, 0x00);  // ACCEL_CONFIG2: filtro del acelerómetro de 218 Hz (registro nuevo del 6500)
  escribirRegistro(0x6C, 0x00);  // PWR_MGMT_2: los 6 ejes encendidos
  escribirRegistro(0x37, 0x00);  // INT_PIN_CFG: INT activo en alto, pulso de 50 µs
  escribirRegistro(0x38, 0x01);  // INT_ENABLE: avisar por INT con cada muestra nueva
  return true;
}

// Lee aceleración, temperatura y giro en una sola lectura de 14 bytes
void leerMPU(int16_t crudo[7]) {
  SPI.beginTransaction(AJUSTES_SPI);
  digitalWrite(PIN_CS, LOW);
  SPI.transfer(0x3B | 0x80);  // ACCEL_XOUT_H, lectura
  for (int i = 0; i < 7; i++) {
    uint8_t alto = SPI.transfer(0x00);
    uint8_t bajo = SPI.transfer(0x00);
    crudo[i] = (int16_t)((alto << 8) | bajo);
  }
  digitalWrite(PIN_CS, HIGH);
  SPI.endTransaction();
}

// Pasa de los ejes del módulo a los ejes de la paleta (docs/CONTRATOS.md).
// En la base del pomo la plaqueta queda perpendicular al mango, así que hay que intercambiar ejes:
// el cuerpo de esta función lo escribe herramientas/ejes.py a partir de 3 posiciones grabadas.
// Módulo de repuesto pegado en la base del pomo dentro de la Pieza A, con el chip hacia afuera
// (23/10, datos/pruebas/2026-10-23_101954_ejes_libre.csv): la punta de la paleta es -Z del módulo
// y la goma roja es +X del módulo. Quedó igual que el módulo de la clase 1 en el mismo lugar.
void alinearEjes(float &x, float &y, float &z) {
  float mx = x, my = y, mz = z;
  x = -mz;
  y = my;
  z = mx;
}

// Corre el modelo una vez al arrancar, para ver que está cargado y cuánto tarda.
// La ventana es la paleta quieta (az = 1 g): con el modelo dummy no importa qué etiqueta dé.
void probarModelo() {
  static float ventana[ML_BUFFER_LONGITUD_ESPERADA];  // static: son 4,7 kB, mejor fuera de la pila
  for (int i = 0; i < ML_BUFFER_LONGITUD_ESPERADA; i++) ventana[i] = (i % 6 == 2) ? 1.0f : 0.0f;
  ml_inicializar();
  uint32_t inicio = micros();
  PrediccionGolpe p = predecir_golpe(ventana, ML_BUFFER_LONGITUD_ESPERADA);
  float ms = (micros() - inicio) / 1000.0f;
  Serial.printf("# Modelo: %s con %.0f %% de certeza, en %.2f ms\n", p.etiqueta, p.probabilidad * 100, ms);
}

void iniciarBLE() {
  BLEDevice::init(NOMBRE_BLE);
  BLEServer *servidor = BLEDevice::createServer();
  servidor->setCallbacks(new AlConectar());
  BLEService *servicio = servidor->createService(UUID_SERVICIO);
  caracteristica = servicio->createCharacteristic(UUID_NOTIFY, BLECharacteristic::PROPERTY_NOTIFY);
  caracteristica->addDescriptor(new BLE2902());  // lo que escribe el celular para suscribirse
  servicio->start();
  BLEAdvertising *anuncio = BLEDevice::getAdvertising();
  anuncio->addServiceUUID(UUID_SERVICIO);
  anuncio->setScanResponse(true);  // el nombre va en la respuesta al escaneo: no entra junto al UUID
  BLEDevice::startAdvertising();
  Serial.printf("# BLE: anunciando como \"%s\"\n", NOMBRE_BLE);
}

// ω del swing en la muestra k, promediado con las 2 de cada lado (como suavizar() de cinematica.py)
float omegaSuave(uint32_t k) {
  float suma = 0;
  for (int j = -2; j <= 2; j++) suma += omega[(k + j) % OMEGA_N];
  return suma / 5;
}

// Arma el evento del último impacto y lo manda. Se llama MUESTRAS_DESPUES muestras después del impacto.
void mandarGolpe() {
  uint32_t i = muestraImpacto;
  float w = 0;
  for (uint32_t k = i - VEL_ANTES; k < i; k++) w += omegaSuave(k);
  w /= VEL_ANTES;
  uint32_t kPico = i - PICO_ANTES;
  for (uint32_t k = kPico; k <= i + PICO_DESPUES; k++) {
    if (omegaSuave(k) > omegaSuave(kPico)) kPico = k;
  }

  BlePayload p;
  p.timestamp = ultimoImpacto / 1000;
  p.numero_golpe = ++golpes;
  p.tipo_golpe = 4;  // todavía sin el modelo real: "desconocido"
  p.confianza = 0;
  p.vel_kmh = (int16_t)lroundf(w * DEG_TO_RAD * L_GIRO_M * 3.6f);
  p.ang_deg = 0;     // falta angulo.cpp (rama firmware-angulo de Mateo)
  p.pico_ms = (int16_t)((int32_t)kPico - (int32_t)i);  // 1 muestra = 1 ms

  bool enviado = celularConectado;
  if (enviado) {
    caracteristica->setValue((uint8_t *)&p, sizeof(p));
    caracteristica->notify();
  }
  Serial.printf("# Golpe %u: %d km/h (%.0f °/s), pico %+d ms%s\n", p.numero_golpe, p.vel_kmh, w, p.pico_ms,
                enviado ? ", enviado por BLE" : ", sin celular conectado");
}

void setup() {
  // Si nadie lee el USB (la app por BLE sin grabar.py, o con el powerbank) cada Serial.printf
  // esperaba hasta 2 s a que la compu leyera: el loop iba a 1 muestra cada 2 s y los golpes no
  // salían nunca por BLE (30/10). Con timeout 0 lo que no entra se tira, y el buffer de 16 kB
  // (~350 ms de muestras) aguanta los tirones de Windows cuando grabar.py sí está leyendo.
  Serial.setTxBufferSize(16384);
  Serial.setTxTimeoutMs(0);
  Serial.begin(921600);
  delay(1500);  // tiempo para abrir el monitor serie
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);  // CS en alto antes de arrancar el bus: el sensor no escucha
  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI, PIN_CS);
  uint8_t id = 0;
  while (!iniciarMPU(id)) {
    Serial.printf("# No encuentro el MPU-6500 (WHO_AM_I = 0x%02X): revisar cables, CS y pines SPI\n", id);
    delay(1000);
  }
  Serial.printf("# MPU-6500 encontrado (WHO_AM_I = 0x%02X)\n", id);
  if (USAR_INT) {
    pinMode(PIN_INT, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_INT), alAvisarElSensor, RISING);
    Serial.printf("# Muestreo por INT (GPIO %d)\n", PIN_INT);
  } else {
    Serial.println("# Muestreo cada 1 ms con micros() (USAR_INT = false)");
  }
  probarModelo();
  iniciarBLE();
  Serial.println("# Paleta lista. Columnas: t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto");
  avisosLeidos = avisos;  // los avisos que llegaron mientras se imprimía no cuentan como perdidos
  proximaMuestra = ultimaLectura = micros();
}

// Decide si toca leer una muestra: con INT, cuando el sensor avisó; en el plan B, cada 1 ms.
bool tocaLeer() {
  uint32_t ahora = micros();
  if (USAR_INT) {
    uint32_t hasta = avisos;  // copia: la interrupción lo puede cambiar en cualquier momento
    if (hasta == avisosLeidos) {
      // si el sensor no avisa nunca, el cable INT está suelto o en otro pin
      if (ahora - ultimaLectura > 1000000 && ahora - ultimoMensaje > 1000000) {
        Serial.printf("# No llega el aviso por INT (GPIO %d): revisar el cable o poner USAR_INT = false\n", PIN_INT);
        ultimoMensaje = ahora;
      }
      return false;
    }
    perdidas += hasta - avisosLeidos - 1;  // si avisó más de una vez desde la última lectura, esas muestras se perdieron
    avisosLeidos = hasta;
    return true;
  }
  if ((int32_t)(ahora - proximaMuestra) < 0) return false;
  proximaMuestra += PERIODO_US;
  if ((int32_t)(ahora - proximaMuestra) > 0) proximaMuestra = ahora + PERIODO_US;  // atrasados: retomar desde ahora
  return true;
}

void loop() {
  if (!tocaLeer()) return;
  uint32_t ahora = micros();
  ultimaLectura = ahora;

  // Las líneas con # las muestra grabar.py pero no las guarda en el CSV
  if (perdidas > 0 && ahora - ultimoMensaje > 1000000) {
    Serial.printf("# Se perdieron %lu muestras\n", (unsigned long)perdidas);
    perdidas = 0;
    ultimoMensaje = ahora;
  }

  int16_t crudo[7];
  leerMPU(crudo);

  float ax = crudo[0] / LSB_POR_G - OFFSET_AX_G;
  float ay = crudo[1] / LSB_POR_G - OFFSET_AY_G;
  float az = crudo[2] / LSB_POR_G - OFFSET_AZ_G;
  float gx = crudo[4] / LSB_POR_DPS, gy = crudo[5] / LSB_POR_DPS, gz = crudo[6] / LSB_POR_DPS;  // crudo[3] es la temperatura
  alinearEjes(ax, ay, az);
  alinearEjes(gx, gy, gz);
  omega[muestras % OMEGA_N] = hypotf(gy, gz);

  int impacto = 0;
  if (hayAnterior) {
    float dx = ax - axAnterior, dy = ay - ayAnterior, dz = az - azAnterior;
    float jerk = sqrtf(dx * dx + dy * dy + dz * dz);
    // un impacto en los primeros 200 ms no tiene de dónde sacar el pico de giro: se ignora
    if (jerk > UMBRAL_JERK_G && ahora - ultimoImpacto > REFRACTARIO_US && muestras > PICO_ANTES + 2) {
      impacto = 1;
      ultimoImpacto = ahora;
      muestraImpacto = muestras;
      golpePendiente = true;
    }
  }
  axAnterior = ax;
  ayAnterior = ay;
  azAnterior = az;
  hayAnterior = true;

  Serial.printf("%lu,%.3f,%.3f,%.3f,%.1f,%.1f,%.1f,%d\n",
                (unsigned long)ahora, ax, ay, az, gx, gy, gz, impacto);

  if (golpePendiente && muestras == muestraImpacto + MUESTRAS_DESPUES) {
    golpePendiente = false;
    mandarGolpe();
  }
  muestras++;
}
