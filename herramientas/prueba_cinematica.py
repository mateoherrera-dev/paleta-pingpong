"""Prueba cinematica.py con la sesión simulada de prueba_orientacion.py, donde se saben las respuestas.

Uso:
    python prueba_cinematica.py

En la simulación el eje de giro está a BRAZO_M del sensor, cada golpe tiene el pico de giro
(800 °/s) 10 ms antes del impacto y la placa marca el impacto 1 ms después (la primera
muestra con vibración). Termina con error si algo se aleja de lo esperado.
"""
import sys

import numpy as np

from cinematica import L_M, estimar_radio, omega_swing, pico_ms, suavizar, velocidad_kmh
from orientacion import madgwick
from prueba_orientacion import BRAZO_M, simular
from senal import FS, detectar_impactos

PICO_ESPERADO_MS = -11       # pico 10 ms antes del contacto, detectado 1 ms después
GIRO_EN_IMPACTO_DPS = 800 * np.exp(-0.5 * (0.011 / 0.05) ** 2)  # la campana del swing, 11 ms después del pico


def main():
    sim = simular()
    acel, giro = np.array(sim.acel), np.array(sim.giro)
    impactos, _ = detectar_impactos(acel)
    q = madgwick(acel, giro)
    omega = suavizar(omega_swing(giro))
    fallas = []

    r, n, r2 = estimar_radio(acel, giro, q, impactos)
    print(f"Radio eje → sensor: real {BRAZO_M:.3f} m · estimado {r:.3f} m ({n} muestras, R² = {r2:.3f})")
    if abs(r - BRAZO_M) > 0.02:
        fallas.append("radio")

    v_esperada = np.radians(GIRO_EN_IMPACTO_DPS) * L_M * 3.6
    print(f"\nGolpes (L = {L_M} m):   velocidad (esperada {v_esperada:.1f} km/h)   pico (esperado {PICO_ESPERADO_MS} ms)")
    for i in impactos:
        v, p = velocidad_kmh(omega, i), pico_ms(omega, i)
        print(f"  {i / FS:6.2f} s {v:22.1f} km/h {p:+22.0f} ms")
        if abs(v - v_esperada) > 0.03 * v_esperada:
            fallas.append(f"velocidad en {i / FS:.2f} s")
        if abs(p - PICO_ESPERADO_MS) > 2:
            fallas.append(f"pico en {i / FS:.2f} s")

    if fallas:
        print(f"\nFALLA: {', '.join(fallas)}")
        sys.exit(1)
    print("\nOK: radio, velocidad y pico coinciden con la simulación")


if __name__ == "__main__":
    main()
