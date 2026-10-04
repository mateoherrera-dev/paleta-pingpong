#ifndef ML_INFERENCE_H
#define ML_INFERENCE_H

#ifdef __cplusplus
extern "C" {
#endif

// Estructura limpia y desacoplada del SDK de Edge Impulse
// para que P1 la consuma sin importar los tipos de datos internos de la red.
typedef struct {
    const char* etiqueta;
    float probabilidad;
    float tiempo_inferencia_ms;
} PrediccionGolpe;

/**
 * @brief Inicializa configuraciones de Edge Impulse (si fueran necesarias).
 */
void ml_inicializar();

/**
 * @brief Ejecuta el modelo de TinyML sobre la ventana capturada.
 * 
 * @param buffer_imu_200ms Array plano de floats [ax, ay, az, gx, gy, gz, ax, ay, ...].
 *                         Debe contener exactamente la cantidad de muestras 
 *                         que espera el modelo (ej. 200ms a 1000Hz = 1200 floats).
 * @param longitud_buffer  Tamaño del array para validación de seguridad.
 * @return PrediccionGolpe Estructura con la clase ganadora y su certeza.
 */
PrediccionGolpe predecir_golpe(float* buffer_imu_200ms, int longitud_buffer);

#ifdef __cplusplus
}
#endif

#endif // ML_INFERENCE_H
