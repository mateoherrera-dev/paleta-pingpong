"""Calcula alinearEjes() para que la placa mande los datos en los ejes de la paleta.

Los ejes de la paleta están en docs/CONTRATOS.md: X a lo largo del mango hacia la punta,
Z saliendo por la goma roja, Y = Z × X. El módulo casi nunca queda montado así (en la base
del pomo la plaqueta queda perpendicular al mango), y alinearEjes() en paleta.ino lo corrige.

Uso (con alinearEjes() SIN cambios en paleta.ino: x = mx, y = my, z = mz):
    python grabar.py --puerto COM5 --jugador ejes --golpe libre
        1. paleta acostada, goma roja para arriba           ~4 s quieta
        2. paleta parada, pomo en la mesa y punta arriba    ~4 s quieta
        3. paleta de canto, sobre cualquiera de los dos     ~4 s quieta (para verificar)
        entre posición y posición moverla sin frenar; Ctrl+C al final
    python ejes.py ../datos/crudos/ARCHIVO.csv

Imprime el cuerpo de alinearEjes() para pegar en firmware/paleta/paleta.ino. La misma función
gira el giroscopio: como es una rotación (Y = Z × X), los signos del giro quedan bien solos.
"""
import argparse

import numpy as np

from calibrar import tramos_quietos
from senal import cargar_sesion

TORCIDO_GRADOS = 20  # más que esto: el módulo quedó girado o la paleta no estaba derecha


def eje_dominante(v):
    """Eje del módulo (0, 1, 2) que más se alinea con v, su signo y cuántos grados se aparta."""
    u = v / np.linalg.norm(v)
    i = int(np.argmax(np.abs(u)))
    return i, np.sign(u[i]), np.degrees(np.arccos(min(1.0, abs(u[i]))))


def main():
    parser = argparse.ArgumentParser(description="Calcula alinearEjes() a partir de 3 posiciones")
    parser.add_argument("archivo")
    args = parser.parse_args()

    sesion = cargar_sesion(args.archivo)
    t, acel = sesion["t"], sesion["acel"]
    tramos = tramos_quietos(sesion["giro"])
    medias = [acel[i:f].mean(axis=0) for i, f in tramos]
    nombres = ["acostada, roja arriba", "parada, punta arriba", "de canto"]

    print(f"{len(tramos)} posiciones quietas (en ejes del módulo):")
    for k, ((i, f), m) in enumerate(zip(tramos, medias)):
        nombre = nombres[k] if k < len(nombres) else "sobra"
        print(f"  {k + 1}. {t[i]:5.1f}–{t[f - 1]:5.1f} s  {nombre:22}  mx {m[0]:+.2f}  my {m[1]:+.2f}  mz {m[2]:+.2f} g")
    if len(tramos) < 2:
        print("Hacen falta por lo menos las posiciones 1 y 2. Grabar de nuevo.")
        return
    if len(tramos) > 3:
        print("Hay más de 3 tramos quietos: se usan los 3 primeros. Si no es lo que se grabó, grabar de nuevo.")

    # Lo que apunta para arriba es lo que mide +1 g
    iz, sz, desvio_z = eje_dominante(medias[0])  # posición 1: Z de la paleta para arriba
    ix, sx, desvio_x = eje_dominante(medias[1])  # posición 2: X de la paleta para arriba
    if iz == ix:
        print("\nLas posiciones 1 y 2 dieron el mismo eje del módulo: ¿se grabaron en otro orden? Grabar de nuevo.")
        return
    for nombre, desvio in [("1", desvio_z), ("2", desvio_x)]:
        if desvio > TORCIDO_GRADOS:
            print(f"Ojo: en la posición {nombre} el eje está {desvio:.0f}° torcido (el módulo quedó girado o la paleta no estaba derecha).")

    # Filas de la rotación: cada eje de la paleta escrito en ejes del módulo
    x_paleta = sx * np.eye(3)[ix]
    z_paleta = sz * np.eye(3)[iz]
    y_paleta = np.cross(z_paleta, x_paleta)
    rotacion = np.array([x_paleta, y_paleta, z_paleta])

    print("\nEn ejes de la paleta:")
    for k, m in enumerate(medias[:3]):
        p = rotacion @ m
        print(f"  {k + 1}. {nombres[k]:22}  ax {p[0]:+.2f}  ay {p[1]:+.2f}  az {p[2]:+.2f} g")
    if len(medias) >= 3 and abs((rotacion @ medias[2])[1]) < 0.8:
        print("Ojo: la posición 3 debería dar ay ≈ ±1 g y no da. Revisar que haya sido de canto.")

    print("\nPara alinearEjes() en firmware/paleta/paleta.ino:")
    print("  float mx = x, my = y, mz = z;")
    for eje, fila in zip("xyz", rotacion):
        j = int(np.argmax(np.abs(fila)))
        signo = "-" if fila[j] < 0 else ""
        print(f"  {eje} = {signo}m{'xyz'[j]};")


if __name__ == "__main__":
    main()
