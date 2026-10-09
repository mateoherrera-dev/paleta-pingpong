#include "angulo.h"
#include <math.h>

// Cada línea tiene su equivalente en herramientas/orientacion.py: si se cambia una, cambiar la otra
// y correr firmware/prueba_pc/comparar.py para ver que sigan dando lo mismo.

static const float DT = 1.0f / ANGULO_FS_HZ;
static const float GRADOS_A_RAD = 3.14159265f / 180.0f;

// Historia de las últimas muestras: la orientación ANTES de procesar cada una y su giro (rad/s).
// Alcanza para volver 150 muestras atrás desde la del impacto.
static const int HISTORIA = ANGULO_CONGELAR_MUESTRAS + 1;
typedef struct {
    float q[4];
    float g[3];
} Muestra;
static Muestra historia[HISTORIA];
static int siguiente = 0;  // posición donde se guarda la próxima muestra
static int guardadas = 0;  // cuántas posiciones tienen datos (hasta HISTORIA)

static float q[4] = {1, 0, 0, 0};  // orientación actual (q0 = parte real)

// Orientación inicial a partir de la gravedad que mide el acelerómetro (paleta quieta).
static void cuaternion_inicial(float ax, float ay, float az, float salida[4]) {
    float norma = sqrtf(ax * ax + ay * ay + az * az);
    ax /= norma;
    ay /= norma;
    az /= norma;
    float roll = atan2f(ay, az);
    float pitch = asinf(fmaxf(-1.0f, fminf(1.0f, -ax)));
    float cr = cosf(roll / 2), sr = sinf(roll / 2);
    float cp = cosf(pitch / 2), sp = sinf(pitch / 2);
    salida[0] = cr * cp;
    salida[1] = sr * cp;
    salida[2] = cr * sp;
    salida[3] = -sr * sp;
}

// Un paso del filtro: misma cuenta que updateIMU() de MadgwickAHRS (giro en rad/s).
// Con beta = 0 ignora el acelerómetro e integra solo el giroscopio.
static void paso_madgwick(float q[4], const float g[3], float ax, float ay, float az, float beta) {
    float q0 = q[0], q1 = q[1], q2 = q[2], q3 = q[3];
    float gx = g[0], gy = g[1], gz = g[2];
    float d0 = 0.5f * (-q1 * gx - q2 * gy - q3 * gz);
    float d1 = 0.5f * (q0 * gx + q2 * gz - q3 * gy);
    float d2 = 0.5f * (q0 * gy - q1 * gz + q3 * gx);
    float d3 = 0.5f * (q0 * gz + q1 * gy - q2 * gx);

    float norma = sqrtf(ax * ax + ay * ay + az * az);
    if (beta > 0 && norma > 0) {
        ax /= norma;
        ay /= norma;
        az /= norma;
        // gradiente del error entre la gravedad estimada y la medida
        float s0 = 4 * q0 * q2 * q2 + 2 * q2 * ax + 4 * q0 * q1 * q1 - 2 * q1 * ay;
        float s1 = 4 * q1 * q3 * q3 - 2 * q3 * ax + 4 * q0 * q0 * q1 - 2 * q0 * ay - 4 * q1
                   + 8 * q1 * q1 * q1 + 8 * q1 * q2 * q2 + 4 * q1 * az;
        float s2 = 4 * q0 * q0 * q2 + 2 * q0 * ax + 4 * q2 * q3 * q3 - 2 * q3 * ay - 4 * q2
                   + 8 * q2 * q1 * q1 + 8 * q2 * q2 * q2 + 4 * q2 * az;
        float s3 = 4 * q1 * q1 * q3 - 2 * q1 * ax + 4 * q2 * q2 * q3 - 2 * q2 * ay;
        float ns = sqrtf(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3);
        if (ns > 0) {
            d0 -= beta * s0 / ns;
            d1 -= beta * s1 / ns;
            d2 -= beta * s2 / ns;
            d3 -= beta * s3 / ns;
        }
    }

    q0 += d0 * DT;
    q1 += d1 * DT;
    q2 += d2 * DT;
    q3 += d3 * DT;
    float nq = sqrtf(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3);
    q[0] = q0 / nq;
    q[1] = q1 / nq;
    q[2] = q2 / nq;
    q[3] = q3 / nq;
}

// Ángulo de la cara roja (+Z) respecto de la vertical: cuánto apunta hacia arriba su normal.
static float angulo_roja(const float q[4]) {
    float vertical = q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3];
    return asinf(fmaxf(-1.0f, fminf(1.0f, vertical))) / GRADOS_A_RAD;
}

void angulo_inicializar() {
    siguiente = 0;
    guardadas = 0;
    q[0] = 1;
    q[1] = q[2] = q[3] = 0;
}

void angulo_actualizar(float ax, float ay, float az, float gx, float gy, float gz) {
    if (guardadas == 0) cuaternion_inicial(ax, ay, az, q);

    Muestra &m = historia[siguiente];
    for (int k = 0; k < 4; k++) m.q[k] = q[k];
    m.g[0] = gx * GRADOS_A_RAD;
    m.g[1] = gy * GRADOS_A_RAD;
    m.g[2] = gz * GRADOS_A_RAD;
    siguiente = (siguiente + 1) % HISTORIA;
    if (guardadas < HISTORIA) guardadas++;

    paso_madgwick(q, m.g, ax, ay, az, ANGULO_BETA);
}

ResultadoAngulo angulo_en_impacto() {
    ResultadoAngulo r = {0, true};
    if (guardadas == 0) return r;

    // La más nueva es la muestra del impacto: se parte de la más vieja y se integra
    // solo el giroscopio hasta la anterior al impacto.
    int pos = (siguiente - guardadas + HISTORIA) % HISTORIA;
    float qi[4];
    for (int k = 0; k < 4; k++) qi[k] = historia[pos].q[k];
    for (int n = 0; n < guardadas - 1; n++) {
        paso_madgwick(qi, historia[pos].g, 0, 0, 0, 0);
        pos = (pos + 1) % HISTORIA;
    }

    // Qué cara golpeó: la punta de la paleta está sobre +X, su velocidad es ω × X = (0, ωz, −ωy).
    // Si ωy < 0 la paleta avanza hacia +Z (roja); si ωy > 0, hacia −Z (negra).
    int n_cara = guardadas - 1 < ANGULO_CARA_MUESTRAS ? guardadas - 1 : ANGULO_CARA_MUESTRAS;
    float suma_gy = 0;
    for (int n = 1; n <= n_cara; n++) {
        suma_gy += historia[(siguiente - 1 - n + 2 * HISTORIA) % HISTORIA].g[1];
    }
    r.cara_roja = n_cara > 0 && suma_gy < 0;

    float roja = angulo_roja(qi);
    r.grados = r.cara_roja ? roja : -roja;
    return r;
}

float angulo_cara_roja() {
    return angulo_roja(q);
}
