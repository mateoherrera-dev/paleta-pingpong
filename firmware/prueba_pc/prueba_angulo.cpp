// Corre angulo.cpp en la PC sobre un CSV de sesión, como si las muestras llegaran de la placa.
// Lo usa comparar.py; a mano:
//   g++ -O2 -static -I../paleta prueba_angulo.cpp ../paleta/angulo.cpp -o prueba_angulo
//   prueba_angulo ../../datos/crudos/prueba_orientacion.csv
//
// Imprime una línea por impacto ("impacto,índice,grados,cara") y el ángulo de la cara roja
// cada 100 muestras ("roja,índice,grados").
#include <cstdio>

#include "angulo.h"

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Uso: prueba_angulo ARCHIVO.csv\n");
        return 1;
    }
    FILE *archivo = fopen(argv[1], "r");
    if (!archivo) {
        fprintf(stderr, "No puedo abrir %s\n", argv[1]);
        return 1;
    }

    char linea[256];
    fgets(linea, sizeof linea, archivo);  // encabezado
    angulo_inicializar();
    long i = 0;
    unsigned long long t_us;
    float ax, ay, az, gx, gy, gz;
    int impacto;
    while (fgets(linea, sizeof linea, archivo)) {
        if (sscanf(linea, "%llu,%f,%f,%f,%f,%f,%f,%d", &t_us, &ax, &ay, &az, &gx, &gy, &gz, &impacto) != 8) continue;
        angulo_actualizar(ax, ay, az, gx, gy, gz);
        if (impacto) {
            ResultadoAngulo r = angulo_en_impacto();
            printf("impacto,%ld,%.3f,%s\n", i, r.grados, r.cara_roja ? "roja" : "negra");
        }
        if (i % 100 == 0) printf("roja,%ld,%.3f\n", i, angulo_cara_roja());
        i++;
    }
    fclose(archivo);
    return 0;
}
