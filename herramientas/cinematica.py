"""Velocidad de la paleta y pico de giro en cada impacto (campos vel_kmh y pico_ms).

Uso:
    python cinematica.py ../datos/crudos/ARCHIVO.csv
    python cinematica.py ../datos/crudos/ARCHIVO.csv --L 0.45      # probar con otro L
    python cinematica.py ../datos/crudos/ARCHIVO.csv --estimar-L   # medir L con los swings del archivo

Muestra una fila por golpe con los tres números que la placa le manda a la app:
ángulo de la cara (orientacion.py), velocidad y pico de giro.

- Velocidad: v = ω · L. ω es el giro que mueve la paleta hacia adelante (ejes Y y Z;
  girar sobre el mango, eje X, no la hace avanzar) y L la distancia del eje de giro al
  centro de la paleta. El sensor mide ω; L hay que estimarlo (--estimar-L).
- Pico de giro: ms entre el momento de giro máximo y el impacto. Negativo = el pico fue
  antes del impacto (GOLPES.md: menos de −25 ms es frenar la mano antes de la pelota).
"""
import argparse

import numpy as np

from orientacion import angulo_en_impacto, madgwick
from senal import FS, cargar_sesion, detectar_impactos

L_M = 0.3                   # provisorio: es lo que implica el PLAN (800 °/s ≈ 15 km/h)
SENSOR_A_CENTRO_M = 0.09    # del sensor (en el cuello) al centro de la paleta, medido con regla el 9/10
SUAVIZAR_S = 0.005          # promedio móvil para que la vibración del golpe no cuente como pico
PICO_ANTES_S = 0.2          # dónde se busca el pico de giro: 200 ms antes del impacto...
PICO_DESPUES_S = 0.05       # ...hasta 50 ms después
VEL_VENTANA_S = 0.005       # la velocidad es el promedio de los 5 ms justo antes del impacto

# Para --estimar-L
SWING_MIN_DPS = 300         # solo muestras con giro fuerte (ahí la centrípeta domina)
SATURA_G = 15.5             # el acelerómetro mide hasta ±16 g: más que esto puede estar recortado
LEJOS_IMPACTO_S = 0.02      # no usar las muestras pegadas a un impacto (vibración)


def omega_swing(giro):
    """Giro que mueve la paleta hacia adelante, en °/s: la punta (+X) se mueve con ω × X = (0, ωz, −ωy)."""
    return np.hypot(giro[:, 1], giro[:, 2])


def suavizar(x, fs=FS):
    n = max(1, int(SUAVIZAR_S * fs))
    return np.convolve(x, np.ones(n) / n, mode="same")


def velocidad_kmh(omega_dps, i, L=L_M, fs=FS):
    """Velocidad del centro de la paleta justo antes del impacto i, en km/h."""
    n = max(1, int(VEL_VENTANA_S * fs))
    omega = np.radians(omega_dps[max(0, i - n):i].mean())
    return omega * L * 3.6


def pico_ms(omega_dps, i, fs=FS):
    """Milisegundos entre el giro máximo y el impacto i (negativo = el pico fue antes)."""
    desde = max(0, i - int(PICO_ANTES_S * fs))
    hasta = min(len(omega_dps), i + int(PICO_DESPUES_S * fs) + 1)
    k = desde + int(np.argmax(omega_dps[desde:hasta]))
    return (k - i) * 1000 / fs


def estimar_radio(acel, giro, q_sesion, impactos=(), fs=FS):
    """Distancia del eje de giro al sensor (m), a partir de la aceleración centrípeta.

    Al girar, el sensor siente un tirón hacia el eje: a_x = −ω² · r (ω en rad/s, solo Y y Z).
    Se le resta la gravedad (con la orientación del Madgwick) y se ajusta una recta entre
    ω² y el tirón con las muestras de giro fuerte que no saturan el acelerómetro: la pendiente es r.
    Devuelve (r, cantidad de muestras usadas, R² del ajuste) o None si no hay suficientes.
    """
    omega = np.radians(omega_swing(giro))
    # componente X de la gravedad en ejes de la paleta (misma fórmula que el Madgwick)
    gravedad_x = 2 * (q_sesion[:, 1] * q_sesion[:, 3] - q_sesion[:, 0] * q_sesion[:, 2])
    tiron = -(acel[:, 0] - gravedad_x) * 9.81  # m/s², positivo = hacia el eje

    usar = (np.degrees(omega) > SWING_MIN_DPS) & (np.abs(acel).max(axis=1) < SATURA_G)
    lejos = int(LEJOS_IMPACTO_S * fs)
    for i in impactos:
        usar[max(0, i - lejos):i + lejos] = False
    if usar.sum() < 50:
        return None

    x, y = omega[usar] ** 2, tiron[usar]
    r, ordenada = np.polyfit(x, y, 1)
    residuo = y - (r * x + ordenada)
    r2 = 1 - residuo.var() / y.var() if y.var() > 0 else 0.0
    return float(r), int(usar.sum()), float(r2)


def main():
    parser = argparse.ArgumentParser(description="Velocidad y pico de giro en cada impacto")
    parser.add_argument("archivo")
    parser.add_argument("--umbral", type=float, default=1.5, help="salto de aceleración en g (default 1.5)")
    parser.add_argument("--L", type=float, default=L_M, help=f"distancia eje de giro → centro de la paleta en m (default {L_M})")
    parser.add_argument("--estimar-L", action="store_true", help="medir L con la aceleración centrípeta de los swings del archivo")
    parser.add_argument("--sensor-centro", type=float, default=SENSOR_A_CENTRO_M,
                        help=f"distancia del sensor al centro de la paleta en m (default {SENSOR_A_CENTRO_M})")
    args = parser.parse_args()

    sesion = cargar_sesion(args.archivo)
    t, acel, giro = sesion["t"], sesion["acel"], sesion["giro"]
    q = madgwick(acel, giro)
    omega = suavizar(omega_swing(giro))

    impactos = np.flatnonzero(sesion["impacto"] == 1)
    origen = "marcados por la placa"
    if len(impactos) == 0:
        impactos, _ = detectar_impactos(acel, umbral_g=args.umbral)
        origen = f"detectados con umbral {args.umbral} g"

    if args.estimar_L:
        estimacion = estimar_radio(acel, giro, q, impactos)
        if estimacion is None:
            print(f"No alcanzan las muestras: hacen falta swings de más de {SWING_MIN_DPS} °/s sin saturar el acelerómetro.")
        else:
            r, n, r2 = estimacion
            print(f"Eje de giro → sensor: r = {r:.3f} m ({n} muestras, ajuste R² = {r2:.2f})")
            print(f"L = r + sensor→centro = {r:.3f} + {args.sensor_centro:.3f} = {r + args.sensor_centro:.3f} m")
            if r2 < 0.5:
                print("Ojo: el ajuste es flojo (R² < 0,5); el número no es confiable. Probar con más swings y más parecidos.")
        print()

    print(f"{len(impactos)} impactos ({origen}) · L = {args.L} m")
    if len(impactos):
        print("   n   tiempo   cara    ángulo    giro   velocidad    pico")
        for n, i in enumerate(impactos, 1):
            ang, cara = angulo_en_impacto(q, giro, i)
            w = omega[max(0, i - int(VEL_VENTANA_S * FS)):i].mean()
            print(f"{n:4d} {t[i]:7.2f} s  {cara:5s} {ang:+7.1f}° {w:5.0f} °/s"
                  f" {velocidad_kmh(omega, i, args.L):6.1f} km/h {pico_ms(omega, i):+6.0f} ms")


if __name__ == "__main__":
    main()
