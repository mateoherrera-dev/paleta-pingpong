#ifndef ANGULO_H
#define ANGULO_H

// Ángulo de la cara de la paleta en el impacto (campo ang_deg del struct BLE).
// Es la misma cuenta que herramientas/orientacion.py, pasada a C++:
// un filtro Madgwick sigue la orientación todo el tiempo y, en el impacto, se parte
// de la orientación de 150 ms antes integrando solo el giroscopio (el swing falsea
// el acelerómetro). Signo: docs/CONTRATOS.md (0° vertical, − cerrada, + abierta).
//
// Uso desde paleta.ino:
//   setup():  angulo_inicializar();
//   loop():   angulo_actualizar(ax, ay, az, gx, gy, gz);   // en CADA muestra, a 1000 Hz
//             if (impacto) { ResultadoAngulo r = angulo_en_impacto(); ... }
//
// No depende de Arduino.h, así también compila en la PC para probarlo
// (firmware/prueba_pc/).

#define ANGULO_FS_HZ 1000            // muestras por segundo que llegan a angulo_actualizar()
#define ANGULO_BETA 0.1f             // ganancia del Madgwick (la de MadgwickAHRS de Arduino)
#define ANGULO_CONGELAR_MUESTRAS 150 // 150 ms antes del impacto se deja de usar el acelerómetro
#define ANGULO_CARA_MUESTRAS 20      // 20 ms antes del impacto, para decidir qué cara golpeó

typedef struct {
    float grados;    // ángulo de la cara que golpeó: − cerrada, + abierta
    bool cara_roja;  // true = golpeó la cara roja (+Z), false = la negra (−Z)
    float q[4];      // orientación en el impacto (q0 = parte real): lleva los vectores de la
                     // paleta al mundo (Z del mundo para arriba). Va al struct BLE (CONTRATOS.md)
} ResultadoAngulo;

/**
 * @brief Arranca el filtro de cero. Llamar en setup() (o para empezar una sesión nueva).
 */
void angulo_inicializar();

/**
 * @brief Procesa una muestra del sensor. Llamar en cada muestra, antes de angulo_en_impacto().
 *
 * Aceleración en g y giro en °/s, ya con los ejes de CONTRATOS.md (después de alinearEjes()).
 * La primera muestra tiene que ser con la paleta más o menos quieta: de ahí sale la vertical inicial.
 */
void angulo_actualizar(float ax, float ay, float az, float gx, float gy, float gz);

/**
 * @brief Ángulo en el impacto. Llamar justo después de angulo_actualizar() de la muestra
 *        donde se detectó el impacto (esa muestra ya trae la vibración y no se usa).
 *
 * Para el struct BLE: payload.ang_deg = (int16_t)lroundf(r.grados);
 */
ResultadoAngulo angulo_en_impacto();

/**
 * @brief Ángulo actual de la cara roja según el filtro, en grados. Sirve para probar con la
 *        paleta quieta en ángulos conocidos (acostada con la roja para arriba = +90°).
 */
float angulo_cara_roja();

#endif // ANGULO_H
