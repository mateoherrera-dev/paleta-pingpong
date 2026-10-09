// Paleta de ping pong inteligente — firmware de la clase 1
//
// Lee el MPU-6500 por SPI 1000 veces por segundo y manda cada muestra por el puerto serie:
//   t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
// Formato, unidades y ejes: docs/CONTRATOS.md
//
// Placa: ESP32S3 Dev Module. Configuración completa del Arduino IDE en el README.
// La cámara no se usa: se puede desconectar.

#include <SPI.h>

// Pines SPI del MPU-6500 (pin del módulo → función). Revisar en el pinout de la placa que estén libres.
// SCL y SDA quedan en los GPIO que usaba el I2C: si hay que volver a I2C, esos dos cables no se mueven.
const int PIN_SCK = 42;   // SCL → reloj
const int PIN_MOSI = 41;  // SDA → datos de la placa al sensor
const int PIN_MISO = 14;  // AD0 → datos del sensor a la placa
const int PIN_CS = 21;    // NCS → chip select

// El MPU-6500 acepta hasta 1 MHz para escribir registros y hasta 20 MHz para leer datos.
// Con cables dupont largos conviene quedarse en 1 MHz: leer una muestra tarda ~120 µs.
const SPISettings AJUSTES_SPI(1000000, MSBFIRST, SPI_MODE3);

const uint32_t PERIODO_US = 1000;  // 1000 Hz

// Escalas para ±16 g y ±2000 °/s
const float LSB_POR_G = 2048.0f;
const float LSB_POR_DPS = 16.4f;

// Detección de impacto: salto brusco de aceleración entre dos muestras seguidas.
// El swing cambia la aceleración de a poco; el golpe con la pelota, de golpe.
// Es un primer valor: ajustarlo con herramientas/ver.py sobre golpes reales.
const float UMBRAL_SALTO_G = 1.5f;
const uint32_t REFRACTARIO_US = 300000;  // después de un impacto, ignorar 300 ms

uint32_t proximaMuestra = 0;
uint32_t ultimoImpacto = 0;
float axAnterior = 0, ayAnterior = 0, azAnterior = 0;
bool hayAnterior = false;

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
// Si el módulo quedó montado girado, intercambiar o cambiar de signo acá.
void alinearEjes(float &x, float &y, float &z) {
  float mx = x, my = y, mz = z;
  x = mx;
  y = my;
  z = mz;
}

void setup() {
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
  Serial.println("# Paleta lista. Columnas: t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto");
  proximaMuestra = micros();
}

void loop() {
  uint32_t ahora = micros();
  if ((int32_t)(ahora - proximaMuestra) < 0) return;
  proximaMuestra += PERIODO_US;
  if ((int32_t)(ahora - proximaMuestra) > 0) proximaMuestra = ahora + PERIODO_US;  // atrasados: retomar desde ahora

  int16_t crudo[7];
  leerMPU(crudo);

  float ax = crudo[0] / LSB_POR_G, ay = crudo[1] / LSB_POR_G, az = crudo[2] / LSB_POR_G;
  float gx = crudo[4] / LSB_POR_DPS, gy = crudo[5] / LSB_POR_DPS, gz = crudo[6] / LSB_POR_DPS;  // crudo[3] es la temperatura
  alinearEjes(ax, ay, az);
  alinearEjes(gx, gy, gz);

  int impacto = 0;
  if (hayAnterior) {
    float dx = ax - axAnterior, dy = ay - ayAnterior, dz = az - azAnterior;
    float salto = sqrtf(dx * dx + dy * dy + dz * dz);
    if (salto > UMBRAL_SALTO_G && ahora - ultimoImpacto > REFRACTARIO_US) {
      impacto = 1;
      ultimoImpacto = ahora;
    }
  }
  axAnterior = ax;
  ayAnterior = ay;
  azAnterior = az;
  hayAnterior = true;

  Serial.printf("%lu,%.3f,%.3f,%.3f,%.1f,%.1f,%.1f,%d\n",
                (unsigned long)ahora, ax, ay, az, gx, gy, gz, impacto);
}
