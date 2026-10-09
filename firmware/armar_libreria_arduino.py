"""Convierte un export "C++ library" de Edge Impulse en una libreria de Arduino.

El Arduino IDE no compila el export C++ tal cual (viene pensado para CMake).
Este script lo reempaqueta: mete edge-impulse-sdk/, model-parameters/ y tflite-model/
dentro de src/ y agrega library.properties y el header <proyecto>_inferencing.h.

Uso:
    python firmware/armar_libreria_arduino.py
    python firmware/armar_libreria_arduino.py firmware/otro_modelo.zip

Despues, en el Arduino IDE: Programa -> Incluir libreria -> Anadir biblioteca .ZIP
y elegir el zip que genera (queda al lado del original, termina en _arduino.zip).

Si el modelo se exporta directo como "Arduino library" desde Edge Impulse, este paso no hace falta.
"""
import pathlib
import re
import sys
import zipfile

CARPETAS_DEL_MODELO = ("edge-impulse-sdk/", "model-parameters/", "tflite-model/")
RAIZ = pathlib.Path(__file__).resolve().parent


def nombre_del_proyecto(export):
    metadata = export.read("model-parameters/model_metadata.h").decode("utf-8")
    proyecto = re.search(r'#define EI_CLASSIFIER_PROJECT_NAME\s+"([^"]+)"', metadata).group(1)
    return re.sub(r"\W", "_", proyecto) + "_inferencing"


def main():
    origen = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "modelo_dummy_sintetico.zip"
    destino = origen.with_name(origen.stem + "_arduino.zip")

    with zipfile.ZipFile(origen) as export, zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as libreria:
        nombre = nombre_del_proyecto(export)

        archivos = 0
        for item in export.infolist():
            if item.is_dir() or not item.filename.startswith(CARPETAS_DEL_MODELO):
                continue
            libreria.writestr(f"{nombre}/src/{item.filename}", export.read(item))
            archivos += 1

        libreria.writestr(f"{nombre}/library.properties", "\n".join([
            f"name={nombre}",
            "version=1.0.0",
            "author=Edge Impulse",
            "maintainer=Equipo paleta-pingpong",
            "sentence=Modelo de Edge Impulse de la paleta, empaquetado para el Arduino IDE.",
            "paragraph=Generado con firmware/armar_libreria_arduino.py a partir del export C++.",
            "category=Data Processing",
            "url=https://github.com/mateoherrera-dev/paleta-pingpong",
            "architectures=*",
            f"includes={nombre}.h",
            "",
        ]))

        guarda = nombre.upper()
        libreria.writestr(f"{nombre}/src/{nombre}.h", "\n".join([
            f"#ifndef {guarda}_H",
            f"#define {guarda}_H",
            "",
            "#include <Arduino.h>",
            '#include "edge-impulse-sdk/classifier/ei_run_classifier.h"',
            '#include "edge-impulse-sdk/dsp/numpy.hpp"',
            '#include "model-parameters/model_metadata.h"',
            "",
            f"#endif  // {guarda}_H",
            "",
        ]))

    print(f"Libreria {nombre} ({archivos} archivos) -> {destino}")


if __name__ == "__main__":
    main()
