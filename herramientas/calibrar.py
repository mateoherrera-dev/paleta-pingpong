"""Calcula el offset del acelerómetro con el módulo quieto en varias posiciones.

Uso:
    python grabar.py --puerto COM5 --jugador calibracion --golpe libre
        (unos 4 s quieto en cada posición: chip arriba, chip abajo y los 4 cantos; Ctrl+C al final)
    python calibrar.py ../datos/crudos/ARCHIVO.csv

Busca los tramos en que el módulo no gira y elige el offset que hace que en todos la
aceleración total dé 1 g. Las posiciones no tienen que ser exactas, solo distintas entre sí.
Si paleta.ino ya resta un offset, lo que da este script se SUMA al que ya tiene.
"""
import argparse

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from senal import FS, cargar_sesion

GIRO_QUIETO_DPS = 25  # si no pasa de esto, el módulo no está cambiando de orientación
VENTANA_S = 0.3
TRAMO_MINIMO_S = 1.0


def tramos_quietos(giro):
    """Devuelve (inicio, fin) de cada tramo en que el módulo no gira."""
    w = int(VENTANA_S * FS)
    pico = np.abs(giro).max(axis=1)
    pico = sliding_window_view(np.pad(pico, (w // 2, w - w // 2 - 1), mode="edge"), w).max(axis=1)
    quieto = np.concatenate([[False], pico < GIRO_QUIETO_DPS, [False]])
    bordes = np.flatnonzero(np.diff(quieto.astype(int)))
    return [(i, f) for i, f in zip(bordes[::2], bordes[1::2]) if f - i >= TRAMO_MINIMO_S * FS]


def ajustar_offset(medias):
    """Offset que deja |media - offset| lo más cerca posible de 1 g en todas las posiciones."""
    offset = np.zeros(3)
    for _ in range(50):
        d = medias - offset
        norma = np.linalg.norm(d, axis=1)
        paso = np.linalg.lstsq(-d / norma[:, None], norma - 1, rcond=None)[0]
        offset -= paso
        if np.abs(paso).max() < 1e-6:
            break
    return offset


def main():
    parser = argparse.ArgumentParser(description="Calcula el offset del acelerómetro")
    parser.add_argument("archivo")
    args = parser.parse_args()

    sesion = cargar_sesion(args.archivo)
    t, acel = sesion["t"], sesion["acel"]
    tramos = tramos_quietos(sesion["giro"])
    medias = np.array([acel[i:f].mean(axis=0) for i, f in tramos])

    print(f"{len(tramos)} posiciones quietas:")
    for (i, f), m in zip(tramos, medias):
        print(f"  {t[i]:5.1f}–{t[f - 1]:5.1f} s   ax {m[0]:+.3f}  ay {m[1]:+.3f}  az {m[2]:+.3f}   |a| {np.linalg.norm(m):.3f} g")
    if len(tramos) < 4:
        print("Hacen falta al menos 4 posiciones distintas (mejor 6). Grabar de nuevo.")
        return

    offset = ajustar_offset(medias)
    error = np.abs(np.linalg.norm(medias - offset, axis=1) - 1).max()
    print(f"\nOffset: ax {offset[0]:+.3f}  ay {offset[1]:+.3f}  az {offset[2]:+.3f} g")
    print(f"Con el offset restado, |a| se aleja de 1 g como mucho {error:.3f} g", end="")
    print(" (bien)" if error < 0.03 else " (alto: posiciones poco quietas o falta variedad)")
    print("\nPara firmware/paleta/paleta.ino:")
    for eje, valor in zip("XYZ", offset):
        print(f"const float OFFSET_A{eje}_G = {valor:.3f}f;")


if __name__ == "__main__":
    main()
