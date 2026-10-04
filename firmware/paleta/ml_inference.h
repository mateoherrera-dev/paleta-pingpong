#ifndef ML_INFERENCE_H
#define ML_INFERENCE_H

// Cantidad exacta de floats que espera el modelo (196 muestras * 6 ejes IMU)
#define ML_BUFFER_LONGITUD_ESPERADA 1176

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
 * @param buffer_imu_196ms Array plano de floats [ax, ay, az, gx, gy, gz, ax, ay, ...].
 *                         Debe contener exactamente la cantidad de muestras 
 *                         que espera el modelo (196ms a 1000Hz = 1176 floats).
 * @param longitud_buffer  Tamaño del array para validación de seguridad (usar ML_BUFFER_LONGITUD_ESPERADA).
 * @return PrediccionGolpe Estructura con la clase ganadora y su certeza.
 */
PrediccionGolpe predecir_golpe(float* buffer_imu_196ms, int longitud_buffer);

#endif // ML_INFERENCE_H
