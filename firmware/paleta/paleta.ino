// Paleta de ping pong inteligente — firmware de la clase 1
//
// Lee el MPU-6500 por SPI 1000 veces por segundo y manda cada muestra por el puerto serie:
//   t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
// Formato, unidades y ejes: docs/CONTRATOS.md
//
// Placa: ESP32S3 Dev Module. Configuración completa del Arduino IDE en el README.
// La cámara no se usa: se puede desconectar.

#include <SPI.h>

// Pines del bus SPI. Revisar en el pinout de la placa que estén libres (no los use la
// cámara, la PSRAM, la tarjeta SD ni el LED) antes de cablear.
const int PIN_SCK = 14;   // MPU-6500: SCL / SCLK
const int PIN_MOSI = 21;  // MPU-6500: SDA / SDI
const int PIN_MISO = 47;  // MPU-6500: AD0 / SDO
const int PIN_CS = 41;    // MPU-6500: NCS
const int PIN_INT = 42;   // MPU-6500: INT (avisa cuando hay una muestra nueva)

// true: se lee cada vez que el sensor avisa por INT que tiene una muestra nueva (va al ritmo
// del reloj del sensor, sin repetir ni saltear muestras).
// false: plan B del PLAN, se lee cada 1000 µs con micros() y el cable INT no hace falta.
const bool USAR_INT = true;

// El MPU-6500 acepta hasta 1 MHz para escribir registros y hasta 20 MHz para leer los datos.
// 1 MHz para todo alcanza: leer una muestra (15 bytes) tarda ~0,15 ms de los 1 ms disponibles.
SPISettings ajustesSPI(1000000, MSBFIRST, SPI_MODE3);

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
uint32_t ultimaMuestra = 0;
uint32_t ultimoAviso = 0;
uint32_t ultimoImpacto = 0;
float axAnterior = 0, ayAnterior = 0, azAnterior = 0;
bool hayAnterior = false;
volatile bool hayMuestraNueva = false;

void IRAM_ATTR alAvisarElSensor() {
  hayMuestraNueva = true;
}

void escribirRegistro(uint8_t registro, uint8_t valor) {
  SPI.beginTransaction(ajustesSPI);
  digitalWrite(PIN_CS, LOW);
  SPI.transfer(registro & 0x7F);  // bit 7 en 0: escribir
  SPI.transfer(valor);
  digitalWrite(PIN_CS, HIGH);
  SPI.endTransaction();
}

void leerRegistros(uint8_t registro, uint8_t *destino, int cantidad) {
  SPI.beginTransaction(ajustesSPI);
  digitalWrite(PIN_CS, LOW);
  SPI.transfer(registro | 0x80);  // bit 7 en 1: leer
  for (int i = 0; i < cantidad; i++) destino[i] = SPI.transfer(0x00);
  digitalWrite(PIN_CS, HIGH);
  SPI.endTransaction();
}

// Devuelve el WHO_AM_I leído: el MPU-6500 responde 0x70. 0x00 o 0xFF = no hay nada conectado.
uint8_t iniciarMPU() {
  escribirRegistro(0x6B, 0x80);  // PWR_MGMT_1: reiniciar
  delay(100);
  escribirRegistro(0x68, 0x07);  // SIGNAL_PATH_RESET: reiniciar giróscopo, acelerómetro y temperatura
  delay(100);
  escribirRegistro(0x6A, 0x10);  // USER_CTRL: apagar la interfaz I2C, solo SPI

  uint8_t quienSoy;
  leerRegistros(0x75, &quienSoy, 1);  // WHO_AM_I
  if (quienSoy == 0x00 || quienSoy == 0xFF) return quienSoy;

  escribirRegistro(0x6B, 0x01);  // PWR_MGMT_1: despertar, reloj del giroscopio
  delay(50);
  escribirRegistro(0x1A, 0x01);  // CONFIG: filtro de 184 Hz, muestreo interno a 1 kHz
  escribirRegistro(0x19, 0x00);  // SMPLRT_DIV: 1 kHz / (1 + 0)
  escribirRegistro(0x1B, 0x18);  // GYRO_CONFIG: ±2000 °/s
  escribirRegistro(0x1C, 0x18);  // ACCEL_CONFIG: ±16 g
  escribirRegistro(0x37, 0x00);  // INT_PIN_CFG: INT activo en alto, pulso de 50 µs
  escribirRegistro(0x38, 0x01);  // INT_ENABLE: avisar por INT cuando hay muestra nueva
  return quienSoy;
}

// Lee aceleración, temperatura y giro en una sola lectura de 14 bytes
void leerMPU(int16_t crudo[7]) {
  uint8_t datos[14];
  leerRegistros(0x3B, datos, 14);  // desde ACCEL_XOUT_H
  for (int i = 0; i < 7; i++) crudo[i] = (int16_t)((datos[2 * i] << 8) | datos[2 * i + 1]);
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
  digitalWrite(PIN_CS, HIGH);
  SPI.begin(PIN_SCK, PIN_MISO, PIN_MOSI);

  uint8_t quienSoy;
  while ((quienSoy = iniciarMPU()) == 0x00 || quienSoy == 0xFF) {
    Serial.printf("# No encuentro el MPU-6500 (WHO_AM_I = 0x%02X): revisar cables y pines SPI\n", quienSoy);
    delay(1000);
  }
  if (quienSoy != 0x70) {
    Serial.printf("# Ojo: WHO_AM_I = 0x%02X, el MPU-6500 responde 0x70. Puede ser otro chip parecido.\n", quienSoy);
  }

  if (USAR_INT) {
    pinMode(PIN_INT, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_INT), alAvisarElSensor, RISING);
  }
  Serial.println("# Paleta lista. Columnas: t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto");
  proximaMuestra = micros();
  ultimaMuestra = proximaMuestra;
}

// Espera a que toque leer: aviso del sensor por INT o, en el plan B, que pase 1 ms.
bool tocaLeer() {
  if (USAR_INT) {
    if (!hayMuestraNueva) {
      // si el sensor no avisa nunca, probablemente el cable INT está suelto o en otro pin
      uint32_t ahora = micros();
      if (ahora - ultimaMuestra > 1000000 && ahora - ultimoAviso > 1000000) {
        Serial.println("# No llega el aviso por INT: revisar el cable o poner USAR_INT = false");
        ultimoAviso = ahora;
      }
      return false;
    }
    hayMuestraNueva = false;
    return true;
  }
  uint32_t ahora = micros();
  if ((int32_t)(ahora - proximaMuestra) < 0) return false;
  proximaMuestra += PERIODO_US;
  if ((int32_t)(ahora - proximaMuestra) > 0) proximaMuestra = ahora + PERIODO_US;  // atrasados: retomar desde ahora
  return true;
}

void loop() {
  if (!tocaLeer()) return;
  uint32_t ahora = micros();
  ultimaMuestra = ahora;

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
