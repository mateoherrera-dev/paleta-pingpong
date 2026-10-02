"""Grafica una sesión y marca los impactos, para ajustar el umbral de detección.

Uso:
    python ver.py ../datos/crudos/ARCHIVO.csv
    python ver.py ../datos/crudos/ARCHIVO.csv --umbral 2.0
    python ver.py ../datos/crudos/ARCHIVO.csv --png sesion.png
"""
import argparse

import matplotlib
import numpy as np

from senal import cargar_sesion, detectar_impactos, revisar_muestreo


def main():
    parser = argparse.ArgumentParser(description="Grafica una sesión de la paleta")
    parser.add_argument("archivo")
    parser.add_argument("--umbral", type=float, default=1.5, help="salto de aceleración en g (default 1.5)")
    parser.add_argument("--png", help="guardar el gráfico en un archivo en vez de mostrarlo")
    args = parser.parse_args()

    if args.png:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sesion = cargar_sesion(args.archivo)
    t, acel, giro = sesion["t"], sesion["acel"], sesion["giro"]
    fs, perdidas = revisar_muestreo(t)
    impactos, salto = detectar_impactos(acel, umbral_g=args.umbral)
    de_la_placa = np.flatnonzero(sesion["impacto"] == 1)

    print(f"Duración: {t[-1]:.1f} s · muestreo: {fs:.0f} Hz · muestras perdidas: {perdidas}")
    print(f"Impactos con umbral {args.umbral} g: {len(impactos)} · marcados por la placa: {len(de_la_placa)}")

    fig, ejes = plt.subplots(3, 1, sharex=True, figsize=(13, 8))
    for i, eje in enumerate("xyz"):
        ejes[0].plot(t, acel[:, i], lw=0.8, label=f"a{eje}")
        ejes[1].plot(t, giro[:, i], lw=0.8, label=f"g{eje}")
    ejes[2].plot(t[1:], salto, lw=0.8, color="0.35", label="salto entre muestras")
    ejes[2].axhline(args.umbral, color="tab:red", ls="--", lw=1, label=f"umbral {args.umbral} g")
    if len(de_la_placa):
        ejes[2].plot(t[de_la_placa], np.full(len(de_la_placa), args.umbral), "v", color="tab:orange", label="impacto según la placa")
    for eje in ejes:
        for i in impactos:
            eje.axvline(t[i], color="tab:red", alpha=0.25, lw=1)

    ejes[0].set_ylabel("aceleración (g)")
    ejes[1].set_ylabel("giro (°/s)")
    ejes[2].set_ylabel("salto (g)")
    ejes[2].set_xlabel("tiempo (s)")
    for eje in ejes:
        eje.legend(loc="upper right", fontsize=8)
        eje.grid(alpha=0.3)
    fig.suptitle(f"{args.archivo} · {len(impactos)} impactos")
    fig.tight_layout()

    if args.png:
        fig.savefig(args.png, dpi=110)
        print(f"Gráfico guardado en {args.png}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
