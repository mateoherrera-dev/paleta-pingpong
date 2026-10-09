// Paleta de ping pong inteligente — firmware de la clase 1
//
// Lee el MPU-6500 por SPI 1000 veces por segundo y manda cada muestra por el puerto serie:
//   t_us,ax_g,ay_g,az_g,gx_dps,gy_dps,gz_dps,impacto
// Formato, unidades y ejes: docs/CONTRATOS.md
//
// Placa: ESP32S3 Dev Module. Configuración completa del Arduino IDE en el README.
// La cámara no se usa: se puede desconectar.

#include <SPI.h>
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
// El eje Z de este chip lee ≈ +0,46 g de más (la hoja de datos admite hasta ±0,08 g).
// Medido el 9/10 con herramientas/calibrar.py. Si se cambia el módulo, hay que volver a medirlo.
const float OFFSET_AX_G = 0.033f;
const float OFFSET_AY_G = -0.012f;
const float OFFSET_AZ_G = 0.460f;

// Detección de impacto: salto brusco de aceleración entre dos muestras seguidas.
// El swing cambia la aceleración de a poco; el golpe con la pelota, de golpe.
// Es un primer valor: ajustarlo con herramientas/ver.py sobre golpes reales.
const float UMBRAL_SALTO_G = 1.5f;
const uint32_t REFRACTARIO_US = 300000;  // después de un impacto, ignorar 300 ms

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
// Si el módulo quedó montado girado, intercambiar o cambiar de signo acá.
void alinearEjes(float &x, float &y, float &z) {
  float mx = x, my = y, mz = z;
  x = mx;
  y = my;
  z = mz;
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
  if (USAR_INT) {
    pinMode(PIN_INT, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_INT), alAvisarElSensor, RISING);
    Serial.printf("# Muestreo por INT (GPIO %d)\n", PIN_INT);
  } else {
    Serial.println("# Muestreo cada 1 ms con micros() (USAR_INT = false)");
  }
  probarModelo();
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
