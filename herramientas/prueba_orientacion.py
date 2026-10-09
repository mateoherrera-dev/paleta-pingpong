"""Prueba orientacion.py con una sesión simulada donde se sabe el ángulo verdadero.

Uso:
    python prueba_orientacion.py
    python orientacion.py ../datos/crudos/prueba_orientacion.csv --quieta

La sesión tiene la paleta quieta a 0°, +30° y −30° (como la prueba de la tarde)
y después golpes de derecha (cara roja) y de revés (cara negra). Como la orientación
se simula, se conoce el ángulo real en cada impacto y se compara con el calculado.
Termina con error si alguno se aleja más de TOLERANCIA grados.
"""
import pathlib
import sys

import numpy as np

from orientacion import angulo_en_impacto, angulo_roja, madgwick
from senal import COLUMNAS, FS, detectar_impactos

RUTA = pathlib.Path(__file__).resolve().parent.parent / "datos" / "crudos" / "prueba_orientacion.csv"
TOLERANCIA = 3.0   # grados
BRAZO_M = 0.4      # distancia del eje de giro al sensor, para la aceleración centrípeta


def rotacion(w, dt):
    """Matriz de rotación de girar a velocidad w (rad/s, ejes de la paleta) durante dt (Rodrigues)."""
    angulo = np.linalg.norm(w) * dt
    if angulo == 0:
        return np.eye(3)
    x, y, z = w / np.linalg.norm(w)
    k = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + np.sin(angulo) * k + (1 - np.cos(angulo)) * k @ k


class Simulador:
    """Mueve una paleta virtual y guarda lo que mediría el sensor y el ángulo real."""

    def __init__(self, rng):
        self.rng = rng
        # columnas = ejes X, Y, Z de la paleta vistos desde el mundo (Z del mundo = arriba)
        # arranca con el mango horizontal y la cara roja vertical, mirando a la red
        self.R = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=float)
        self.giro, self.acel, self.real = [], [], []
        self.impactos = []  # (índice, cara que golpea)

    def _avanzar(self, w, extra=(0, 0, 0)):
        """Guarda una muestra con velocidad de giro w (rad/s) y avanza 1 ms."""
        arriba = self.R[2]  # la vertical del mundo en ejes de la paleta
        centripeta = -np.array([1, 0, 0]) * (w[1] ** 2 + w[2] ** 2) * BRAZO_M / 9.81
        a = arriba + centripeta + np.asarray(extra) + self.rng.normal(0, 0.02, 3)
        g = np.degrees(w) + self.rng.normal(0, 0.5, 3) + [0.8, -0.5, 0.3]  # ruido y sesgo del giróscopo
        self.acel.append(np.clip(a, -16, 16))
        self.giro.append(g)
        self.real.append(np.degrees(np.arcsin(np.clip(self.R[2, 2], -1, 1))))
        self.R = self.R @ rotacion(w, 1 / FS)

    def quieto(self, segundos):
        for _ in range(int(segundos * FS)):
            self._avanzar(np.zeros(3))

    def inclinar(self, grados, segundos=0.4):
        """Gira la muñeca (eje X, el mango): con la cara vertical, +grados la cierra."""
        n = int(segundos * FS)
        perfil = np.sin(np.pi * np.arange(n) / n) ** 2  # arranca y frena suave
        perfil *= np.radians(grados) / (perfil.sum() / FS)
        for w in perfil:
            self._avanzar(np.array([w, 0, 0]))

    def golpe(self, cara, muneca_grados, pico_dps=800):
        """Swing alrededor de Y (de derecha con la roja, de revés con la negra) más un giro de muñeca."""
        n = int(0.5 * FS)
        t = (np.arange(n) - n // 2) / FS
        campana = np.exp(-0.5 * (t / 0.05) ** 2)
        wy = (-1 if cara == "roja" else 1) * np.radians(pico_dps) * campana
        wx = campana * np.radians(muneca_grados) / (campana.sum() / FS)
        impacto = n // 2 + 10
        for k in range(n):
            vibracion = 0.0
            if k >= impacto:
                dt = (k - impacto) / FS
                vibracion = 4 * np.exp(-dt / 0.005) * np.sin(2 * np.pi * 150 * dt)
            if k == impacto:
                self.impactos.append((len(self.acel), cara))
            self._avanzar(np.array([wx[k], wy[k], 0]), extra=(0, vibracion, 0.6 * vibracion))


def simular():
    sim = Simulador(np.random.default_rng(3))
    # prueba quieta: 0°, +30° (abierta), −30° (cerrada), vuelta a 0°
    sim.quieto(2)
    sim.inclinar(-30)
    sim.quieto(2)
    sim.inclinar(60)
    sim.quieto(2)
    sim.inclinar(-30)
    sim.quieto(1.5)
    # golpes: (cara, inclinación previa, giro de muñeca durante el swing)
    golpes = [("roja", 10, 15), ("negra", -20, 10), ("roja", -35, -5), ("negra", 25, -10),
              ("roja", 15, 10), ("negra", -40, 5)]
    for cara, previa, muneca in golpes:
        sim.inclinar(previa, 0.3)
        sim.quieto(0.4)
        sim.golpe(cara, muneca)
        sim.quieto(0.6)
    return sim


def main():
    sim = simular()
    acel, giro, real = np.array(sim.acel), np.array(sim.giro), np.array(sim.real)
    detectados, _ = detectar_impactos(acel)

    q = madgwick(acel, giro)
    errores = []

    print("Paleta quieta (cara roja):   real   calculado")
    for desde, hasta in [(0.5, 1.9), (2.6, 4.3), (4.9, 6.6), (7.2, 8.5)]:
        tramo = slice(int(desde * FS), int(hasta * FS))
        calc = angulo_roja(q[tramo]).mean()
        errores.append(abs(calc - real[tramo].mean()))
        print(f"  {desde:4.1f}–{hasta:4.1f} s {real[tramo].mean():+20.1f}° {calc:+10.1f}°")

    print("\nGolpes:   cara   real   calculado   solo acelerómetro   cara detectada")
    for i_real, cara in sim.impactos:
        cerca = detectados[np.abs(detectados - i_real) <= 3]
        if len(cerca) == 0:
            print(f"  impacto en {i_real / FS:.2f} s no detectado")
            errores.append(np.inf)
            continue
        i = int(cerca[0])
        verdad = real[i] if cara == "roja" else -real[i]
        ang, cara_calc = angulo_en_impacto(q, giro, i)
        a = acel[i - 1]
        ingenuo = np.degrees(np.arcsin(np.clip(a[2] / np.linalg.norm(a), -1, 1)))
        ingenuo = ingenuo if cara == "roja" else -ingenuo
        errores.append(abs(ang - verdad) if cara_calc == cara else np.inf)
        print(f"  {i / FS:6.2f} s {cara:6s} {verdad:+6.1f}° {ang:+9.1f}° {ingenuo:+15.1f}° {cara_calc:>16s}")

    RUTA.parent.mkdir(parents=True, exist_ok=True)
    marca = np.zeros(len(acel), dtype=int)
    marca[detectados] = 1
    with open(RUTA, "w", newline="") as archivo:
        archivo.write(",".join(COLUMNAS) + "\n")
        for k in range(len(acel)):
            a, g = acel[k], giro[k]
            archivo.write(f"{5_000_000 + k * 1000},{a[0]:.3f},{a[1]:.3f},{a[2]:.3f},"
                          f"{g[0]:.1f},{g[1]:.1f},{g[2]:.1f},{marca[k]}\n")
    print(f"\nSesión guardada en {RUTA}")

    peor = max(errores)
    if peor > TOLERANCIA:
        print(f"FALLA: error máximo {peor:.1f}° (tolerancia {TOLERANCIA}°)")
        sys.exit(1)
    print(f"OK: error máximo {peor:.1f}° (tolerancia {TOLERANCIA}°)")


if __name__ == "__main__":
    main()
