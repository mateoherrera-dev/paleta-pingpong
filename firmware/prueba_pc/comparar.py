"""Compara el ángulo de firmware/paleta/angulo.cpp con el de herramientas/orientacion.py.

Compila angulo.cpp para la PC (hace falta g++), lo corre sobre una sesión y calcula lo mismo
con el script de Python. Tienen que dar casi igual: el C++ usa float (como el ESP32) y el
Python double, así que se aceptan diferencias de hasta TOLERANCIA grados.

Uso (desde la raíz del repo):
    python herramientas/prueba_orientacion.py        # genera la sesión simulada
    python firmware/prueba_pc/comparar.py
    python firmware/prueba_pc/comparar.py datos/crudos/OTRA_SESION.csv
"""
import pathlib
import subprocess
import sys

import numpy as np

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))

from orientacion import angulo_en_impacto, angulo_roja, madgwick  # noqa: E402
from senal import cargar_sesion  # noqa: E402

TOLERANCIA = 0.1  # grados


def compilar():
    ejecutable = AQUI / ("prueba_angulo.exe" if sys.platform == "win32" else "prueba_angulo")
    # -static: el .exe no depende de las DLL del compilador para correr
    subprocess.run(["g++", "-O2", "-Wall", "-static", "-I", str(RAIZ / "firmware" / "paleta"),
                    str(AQUI / "prueba_angulo.cpp"), str(RAIZ / "firmware" / "paleta" / "angulo.cpp"),
                    "-o", str(ejecutable)], check=True)
    return ejecutable


def main():
    ruta = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "datos" / "crudos" / "prueba_orientacion.csv"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Generala con: python herramientas/prueba_orientacion.py")

    salida = subprocess.run([str(compilar()), str(ruta)], capture_output=True, text=True, check=True).stdout
    impactos_c, roja_c = [], []
    for linea in salida.splitlines():
        partes = linea.split(",")
        if partes[0] == "impacto":
            impactos_c.append((int(partes[1]), float(partes[2]), partes[3]))
        elif partes[0] == "roja":
            roja_c.append((int(partes[1]), float(partes[2])))

    sesion = cargar_sesion(ruta)
    q = madgwick(sesion["acel"], sesion["giro"])
    # el C++ imprime la orientación después de procesar la muestra i, o sea q[i + 1] del Python
    q_despues = np.vstack([q[1:], q[-1:]])
    roja_py = angulo_roja(q_despues)

    errores = [abs(c - roja_py[i]) for i, c in roja_c if i + 1 < len(q)]
    print(f"Ángulo de la cara roja en {len(errores)} puntos: diferencia máxima {max(errores):.3f}°")

    peor = max(errores)
    print("\nImpactos:  índice   C++        Python")
    for i, grados_c, cara_c in impactos_c:
        grados_py, cara_py = angulo_en_impacto(q, sesion["giro"], i)
        dif = abs(grados_c - grados_py) if cara_c == cara_py else float("inf")
        peor = max(peor, dif)
        print(f"  {i:8d} {grados_c:+8.2f}° {cara_c:5s} {grados_py:+8.2f}° {cara_py:5s}")

    if len(impactos_c) != int(sesion["impacto"].sum()):
        sys.exit("FALLA: el C++ no reportó todos los impactos del archivo")
    if peor > TOLERANCIA:
        sys.exit(f"FALLA: diferencia máxima {peor:.3f}° (tolerancia {TOLERANCIA}°)")
    print(f"\nOK: C++ y Python coinciden (diferencia máxima {peor:.3f}°, tolerancia {TOLERANCIA}°)")


if __name__ == "__main__":
    main()
