"""Genera una sesión sintética para probar las herramientas sin tener la placa.

Uso:
    python ejemplo.py
    python ver.py ../datos/crudos/ejemplo_sintetico.csv

Los golpes son inventados: sirven para probar el código, no para entrenar.
"""
import pathlib

import numpy as np

from senal import COLUMNAS, FS, detectar_impactos

RUTA = pathlib.Path(__file__).resolve().parent.parent / "datos" / "crudos" / "ejemplo_sintetico.csv"


def main():
    rng = np.random.default_rng(7)
    duracion = 12
    t = np.arange(duracion * FS) / FS
    acel = rng.normal(0, 0.02, (len(t), 3)) + [0, 0, 1]
    giro = rng.normal(0, 1.0, (len(t), 3))

    for k, t0 in enumerate(np.arange(1.5, duracion - 1, 1.6)):
        signo = 1 if k % 2 == 0 else -1  # alterna derecha y revés
        swing = np.exp(-0.5 * ((t - t0) / 0.06) ** 2)
        giro[:, 2] += signo * 900 * swing
        giro[:, 0] += 300 * swing
        acel[:, 0] += 6 * np.exp(-0.5 * ((t - t0) / 0.07) ** 2)
        # el impacto: una vibración corta que se apaga en milisegundos
        dt = np.clip(t - (t0 + 0.01), 0, None)
        vibracion = 4 * np.exp(-dt / 0.005) * np.sin(2 * np.pi * 150 * dt)
        acel[:, 1] += vibracion
        acel[:, 2] += 0.6 * vibracion

    impactos, _ = detectar_impactos(acel)
    marca = np.zeros(len(t), dtype=int)
    marca[impactos] = 1
    t_us = (t * 1e6).astype(np.int64) + 5_000_000

    RUTA.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA, "w", newline="") as archivo:
        archivo.write(",".join(COLUMNAS) + "\n")
        for i in range(len(t)):
            a, g = acel[i], giro[i]
            archivo.write(f"{t_us[i]},{a[0]:.3f},{a[1]:.3f},{a[2]:.3f},{g[0]:.1f},{g[1]:.1f},{g[2]:.1f},{marca[i]}\n")
    print(f"Sesión sintética guardada en {RUTA} ({len(impactos)} golpes)")


if __name__ == "__main__":
    main()
