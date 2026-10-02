// Paleta de ping pong inteligente — firmware de la clase 0
//
// Lee el MPU6050 1000 veces por segundo y manda cada muestra por el puerto serie:
//   t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
// Formato, unidades y ejes: docs/CONTRATOS.md
//
// Placa: ESP32S3 Dev Module (misma configuración que en el proyecto de las gafas).
// La cámara no se usa: se puede desconectar.

#include <Wire.h>

// Pines I2C del MPU6050. Revisar en el pinout de la placa que estén libres y en los headers.
const int PIN_SDA = 41;
const int PIN_SCL = 42;

const uint8_t MPU_ADDR = 0x68;     // 0x69 si el pin AD0 del módulo está conectado a 3,3 V
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
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(registro);
  Wire.write(valor);
  Wire.endTransmission();
}

bool iniciarMPU() {
  Wire.beginTransmission(MPU_ADDR);
  if (Wire.endTransmission() != 0) return false;
  escribirRegistro(0x6B, 0x01);  // PWR_MGMT_1: despertar, reloj del giroscopio
  delay(50);
  escribirRegistro(0x1A, 0x01);  // CONFIG: filtro de 184 Hz, muestreo interno a 1 kHz
  escribirRegistro(0x19, 0x00);  // SMPLRT_DIV: 1 kHz / (1 + 0)
  escribirRegistro(0x1B, 0x18);  // GYRO_CONFIG: ±2000 °/s
  escribirRegistro(0x1C, 0x18);  // ACCEL_CONFIG: ±16 g
  return true;
}

// Lee aceleración, temperatura y giro en una sola lectura de 14 bytes
bool leerMPU(int16_t crudo[7]) {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // ACCEL_XOUT_H
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MPU_ADDR, 14) != 14) return false;
  for (int i = 0; i < 7; i++) {
    uint8_t alto = Wire.read();
    uint8_t bajo = Wire.read();
    crudo[i] = (int16_t)((alto << 8) | bajo);
  }
  return true;
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
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000);
  while (!iniciarMPU()) {
    Serial.println("# No encuentro el MPU6050: revisar cables, pines y direccion I2C");
    delay(1000);
  }
  Serial.println("# Paleta lista. Columnas: t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto");
  proximaMuestra = micros();
}

void loop() {
  uint32_t ahora = micros();
  if ((int32_t)(ahora - proximaMuestra) < 0) return;
  proximaMuestra += PERIODO_US;
  if ((int32_t)(ahora - proximaMuestra) > 0) proximaMuestra = ahora + PERIODO_US;  // atrasados: retomar desde ahora

  int16_t crudo[7];
  if (!leerMPU(crudo)) return;

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
