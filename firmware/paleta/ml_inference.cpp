#include "ml_inference.h"
#include <Arduino.h>

// Cabecera de la librería de Arduino del modelo (incluye ei_run_classifier.h).
// Se genera con firmware/armar_libreria_arduino.py. Si el modelo se exporta como
// "Arduino library" desde Edge Impulse, cambiar por el <..._inferencing.h> de ese zip.
#include <ping_pong_classifier_inferencing.h>

void ml_inicializar() {
    // Edge Impulse no requiere inicialización global obligatoria,
    // pero acá se pueden pre-asignar tensores o configurar pines de debug.
    Serial.println("ML_INFERENCE: Módulo de inferencia inicializado.");
}

PrediccionGolpe predecir_golpe(float* buffer_imu_196ms, int longitud_buffer) {
    PrediccionGolpe resultado = {"Desconocido", 0.0f, 0.0f};

    // 1. Validar que P1 nos pasó el tamaño de buffer correcto.
    // EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE viene de model_metadata.h
    if (longitud_buffer != EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE) {
        Serial.printf("ML_ERROR: Buffer de tamaño incorrecto. Se esperaban %d floats, llegaron %d\n", 
                      EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, longitud_buffer);
        return resultado;
    }

    // 2. Envolver el array puro de C en la estructura signal_t que usa Edge Impulse
    signal_t signal;
    int err = numpy::signal_from_buffer(buffer_imu_196ms, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
    
    if (err != 0) {
        Serial.printf("ML_ERROR: Falló signal_from_buffer (código %d)\n", err);
        return resultado;
    }

    // 3. Invocar al clasificador de TensorFlow Lite Micro / Edge Impulse
    ei_impulse_result_t result = { 0 };
    bool debug_nn = false;
    
    err = run_classifier(&signal, &result, debug_nn);
    if (err != EI_IMPULSE_OK) {
        Serial.printf("ML_ERROR: Falló run_classifier (código %d)\n", err);
        return resultado;
    }

    // 4. Buscar la clase con la probabilidad más alta (ArgMax)
    int mejor_indice = 0;
    float mejor_probabilidad = 0.0f;
    
    for (uint16_t i = 0; i < EI_CLASSIFIER_LABEL_COUNT; i++) {
        if (result.classification[i].value > mejor_probabilidad) {
            mejor_probabilidad = result.classification[i].value;
            mejor_indice = i;
        }
    }

    // 5. Empaquetar el resultado en el struct limpio
    resultado.etiqueta = result.classification[mejor_indice].label;
    resultado.probabilidad = mejor_probabilidad;
    resultado.tiempo_inferencia_ms = result.timing.classification;

    return resultado;
}
