"""Calcula el ángulo de la cara de la paleta en cada impacto (el campo ang_deg).

Uso:
    python orientacion.py ../datos/crudos/ARCHIVO.csv
    python orientacion.py ../datos/crudos/ARCHIVO.csv --png angulo.png
    python orientacion.py ../datos/crudos/ARCHIVO.csv --quieta     # prueba con la paleta quieta
    python orientacion.py ../datos/crudos/ARCHIVO.csv --cara roja  # forzar la cara que golpea
    python orientacion.py ../datos/crudos/ARCHIVO.csv --verificar  # swings que arrancan y terminan quietos

Cómo funciona (docs/PLAN.md, sección 4.7):
1. Un filtro Madgwick sigue la orientación de la paleta en toda la sesión: integra
   el giroscopio y usa el acelerómetro (la gravedad) para corregir la deriva de a poco.
2. En el swing el acelerómetro mide mucho más que la gravedad, así que en cada impacto
   se toma la orientación de CONGELAR_S antes y desde ahí se integra solo el giroscopio.
3. El ángulo es cuánto apunta hacia arriba la normal de la cara que golpea:
   ang = asin(componente vertical de la normal). La cara roja es +Z y la negra −Z.

Convención de signo (docs/CONTRATOS.md): 0° = cara vertical, negativo = cerrada
(mira a la mesa), positivo = abierta (mira al techo). Paleta acostada con la roja
para arriba: +90° para la roja.
"""
import argparse
import math

import matplotlib
import numpy as np

from senal import FS, cargar_sesion, detectar_impactos

BETA = 0.1          # ganancia del Madgwick (la misma que trae MadgwickAHRS de Arduino)
CONGELAR_S = 0.15   # cuánto antes del impacto se deja de usar el acelerómetro
CARA_S = 0.02       # ventana antes del impacto para decidir qué cara golpeó

# Para --verificar (swings que arrancan y terminan con la paleta quieta)
QUIETO_GIRO_DPS = 15   # girando menos que esto, la paleta está quieta
QUIETO_ACEL_G = 0.1    # y el acelerómetro mide 1 g ± esto (solo la gravedad)
QUIETO_MIN_S = 0.3     # cuánto tiene que durar quieta para usarla de referencia
SWING_MIN_DPS = 200    # giro mínimo para que el movimiento entre dos quietos cuente como swing
SATURA_DPS = 1990      # el MPU-6500 mide hasta ±2000 °/s


def cuaternion_inicial(a):
    """Orientación inicial a partir de la gravedad que mide el acelerómetro (paleta quieta)."""
    a = a / np.linalg.norm(a)
    roll = math.atan2(a[1], a[2])
    pitch = math.asin(max(-1.0, min(1.0, -a[0])))
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    return [cr * cp, sr * cp, cr * sp, -sr * sp]


def paso_madgwick(q, g, a, dt, beta):
    """Un paso del filtro: misma cuenta que updateIMU() de MadgwickAHRS (giro en rad/s).

    Con beta = 0 ignora el acelerómetro e integra solo el giroscopio.
    """
    q0, q1, q2, q3 = q
    gx, gy, gz = g
    d0 = 0.5 * (-q1 * gx - q2 * gy - q3 * gz)
    d1 = 0.5 * (q0 * gx + q2 * gz - q3 * gy)
    d2 = 0.5 * (q0 * gy - q1 * gz + q3 * gx)
    d3 = 0.5 * (q0 * gz + q1 * gy - q2 * gx)

    norma = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    if beta > 0 and norma > 0:
        ax, ay, az = a[0] / norma, a[1] / norma, a[2] / norma
        # gradiente del error entre la gravedad estimada y la medida
        s0 = 4 * q0 * q2 * q2 + 2 * q2 * ax + 4 * q0 * q1 * q1 - 2 * q1 * ay
        s1 = (4 * q1 * q3 * q3 - 2 * q3 * ax + 4 * q0 * q0 * q1 - 2 * q0 * ay - 4 * q1
              + 8 * q1 * q1 * q1 + 8 * q1 * q2 * q2 + 4 * q1 * az)
        s2 = (4 * q0 * q0 * q2 + 2 * q0 * ax + 4 * q2 * q3 * q3 - 2 * q3 * ay - 4 * q2
              + 8 * q2 * q1 * q1 + 8 * q2 * q2 * q2 + 4 * q2 * az)
        s3 = 4 * q1 * q1 * q3 - 2 * q1 * ax + 4 * q2 * q2 * q3 - 2 * q2 * ay
        ns = math.sqrt(s0 * s0 + s1 * s1 + s2 * s2 + s3 * s3)
        if ns > 0:
            d0 -= beta * s0 / ns
            d1 -= beta * s1 / ns
            d2 -= beta * s2 / ns
            d3 -= beta * s3 / ns

    q0, q1, q2, q3 = q0 + d0 * dt, q1 + d1 * dt, q2 + d2 * dt, q3 + d3 * dt
    nq = math.sqrt(q0 * q0 + q1 * q1 + q2 * q2 + q3 * q3)
    return [q0 / nq, q1 / nq, q2 / nq, q3 / nq]


def madgwick(acel, giro, fs=FS, beta=BETA):
    """Corre el filtro sobre toda la sesión. Devuelve un cuaternión (q0..q3) por muestra.

    q[k] es la orientación antes de procesar la muestra k.
    """
    giro_rad = np.radians(giro).tolist()
    acel_l = acel.tolist()
    dt = 1 / fs
    q = cuaternion_inicial(acel[0])
    salida = np.empty((len(acel), 4))
    for k in range(len(acel)):
        salida[k] = q
        q = paso_madgwick(q, giro_rad[k], acel_l[k], dt, beta)
    return salida


def angulo_roja(q):
    """Ángulo de la cara roja (+Z) respecto de la vertical, en grados. Acepta uno o varios cuaterniones."""
    q = np.asarray(q)
    # componente vertical de la normal Z = Z de la gravedad estimada (misma fórmula que el Madgwick)
    vertical = q[..., 0] ** 2 - q[..., 1] ** 2 - q[..., 2] ** 2 + q[..., 3] ** 2
    return np.degrees(np.arcsin(np.clip(vertical, -1, 1)))


def cara_que_golpea(giro, i, fs=FS):
    """Decide qué cara le pegó a la pelota según hacia dónde se movía la paleta.

    La punta de la paleta está sobre +X, así que su velocidad es ω × X = (0, ωz, −ωy):
    si ωy < 0 la paleta avanza hacia +Z y golpea la roja; si ωy > 0, la negra.
    """
    gy = giro[max(0, i - int(CARA_S * fs)):i, 1].mean()
    return "roja" if gy < 0 else "negra"


def integrar_giro(q, giro, fs=FS):
    """Parte de la orientación q y suma solo el giroscopio (giro en °/s), sin el acelerómetro."""
    q = list(q)
    for g in np.radians(giro).tolist():
        q = paso_madgwick(q, g, (0.0, 0.0, 0.0), 1 / fs, beta=0)
    return q


def angulo_en_impacto(q_sesion, giro, i, fs=FS, congelar_s=CONGELAR_S, cara="auto"):
    """Ángulo de la cara que golpea en el impacto i (en grados) y qué cara fue.

    Parte de la orientación del Madgwick congelar_s antes del impacto e integra
    solo el giroscopio hasta el impacto, para que el swing no falsee la vertical.
    """
    j = max(0, i - int(round(congelar_s * fs)))
    q = integrar_giro(q_sesion[j], giro[j:i], fs)
    if cara == "auto":
        cara = cara_que_golpea(giro, i, fs)
    ang = float(angulo_roja(q))
    return (ang if cara == "roja" else -ang), cara


def tramos_quietos(acel, giro, fs=FS):
    """Tramos (inicio, fin) donde la paleta está quieta: casi no gira y el acelerómetro mide solo la gravedad."""
    quieta = ((np.linalg.norm(giro, axis=1) < QUIETO_GIRO_DPS)
              & (np.abs(np.linalg.norm(acel, axis=1) - 1) < QUIETO_ACEL_G))
    cambios = np.diff(np.concatenate([[0], quieta.astype(int), [0]]))
    inicios, fines = np.flatnonzero(cambios == 1), np.flatnonzero(cambios == -1)
    return [(a, b) for a, b in zip(inicios, fines) if b - a >= QUIETO_MIN_S * fs]


def verificar_swings(acel, giro, fs=FS):
    """Mide cuánto error acumula el giroscopio en swings que arrancan y terminan con la paleta quieta.

    Con la paleta quieta el acelerómetro da el ángulo bien. Se parte del ángulo que mide quieta
    antes del swing, se suma solo el giroscopio durante el swing (como en el impacto) y se compara
    con lo que mide el acelerómetro cuando vuelve a quedar quieta. El swing dura más que los
    CONGELAR_S del impacto, así que el error en el impacto es menor que este.
    Devuelve una lista de (inicio, fin, giro máximo °/s, saturó, ángulo por giroscopio, ángulo por acelerómetro).
    """
    tramos = tramos_quietos(acel, giro, fs)
    resultados = []
    for (a0, a1), (b0, b1) in zip(tramos, tramos[1:]):
        giro_max = np.linalg.norm(giro[a1:b0], axis=1).max()
        if giro_max < SWING_MIN_DPS:
            continue  # se movió poco: no es un swing
        q = integrar_giro(cuaternion_inicial(acel[a0:a1].mean(axis=0)), giro[a1:b0], fs)
        a = acel[b0:b1].mean(axis=0)
        por_acel = np.degrees(np.arcsin(np.clip(a[2] / np.linalg.norm(a), -1, 1)))
        satura = bool(np.abs(giro[a1:b0]).max() >= SATURA_DPS)
        resultados.append((a1, b0, giro_max, satura, float(angulo_roja(q)), float(por_acel)))
    return resultados


def main():
    parser = argparse.ArgumentParser(description="Ángulo de la cara de la paleta en cada impacto")
    parser.add_argument("archivo")
    parser.add_argument("--umbral", type=float, default=1.5, help="salto de aceleración en g (default 1.5)")
    parser.add_argument("--beta", type=float, default=BETA, help=f"ganancia del Madgwick (default {BETA})")
    parser.add_argument("--congelar", type=float, default=CONGELAR_S * 1000,
                        help=f"ms antes del impacto en que se deja de usar el acelerómetro (default {CONGELAR_S * 1000:.0f})")
    parser.add_argument("--cara", choices=["auto", "roja", "negra"], default="auto",
                        help="cara que golpea (default: auto, según el sentido del swing)")
    parser.add_argument("--quieta", action="store_true",
                        help="prueba con la paleta quieta: muestra el ángulo de la roja cada medio segundo")
    parser.add_argument("--verificar", action="store_true",
                        help="swings que arrancan y terminan quietos: error que acumula el giroscopio en cada uno")
    parser.add_argument("--png", help="guardar el gráfico en un archivo en vez de mostrarlo")
    args = parser.parse_args()

    if args.png:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sesion = cargar_sesion(args.archivo)
    t, acel, giro = sesion["t"], sesion["acel"], sesion["giro"]
    q = madgwick(acel, giro, beta=args.beta)
    roja = angulo_roja(q)

    impactos = np.flatnonzero(sesion["impacto"] == 1)
    origen = "marcados por la placa"
    if len(impactos) == 0:
        impactos, _ = detectar_impactos(acel, umbral_g=args.umbral)
        origen = f"detectados con umbral {args.umbral} g"

    if args.quieta:
        print("Ángulo de la cara roja (paleta quieta, Madgwick):")
        print("   desde    hasta   promedio   variación")
        bloque = FS // 2
        for k in range(0, len(t) - bloque + 1, bloque):
            tramo = roja[k:k + bloque]
            print(f"{t[k]:7.1f} s {t[k + bloque - 1]:6.1f} s {tramo.mean():8.1f}° {np.ptp(tramo):9.1f}°")

    if args.verificar:
        swings = verificar_swings(acel, giro)
        print(f"Swings que arrancan y terminan quietos: {len(swings)}")
        if swings:
            print("   n   desde   duración   giro máx   solo giroscopio   acelerómetro   error")
            errores = []
            for n, (a, b, giro_max, satura, por_giro, por_acel) in enumerate(swings, 1):
                error = por_giro - por_acel
                errores.append(abs(error))
                aviso = "  ¡saturó!" if satura else ""
                print(f"{n:4d} {t[a]:6.1f} s {(b - a) / FS:7.2f} s {giro_max:7.0f} °/s"
                      f" {por_giro:+12.1f}° {por_acel:+13.1f}° {error:+7.1f}°{aviso}")
            print(f"Error típico: {np.median(errores):.1f}° · peor: {max(errores):.1f}°")
        else:
            print("No encontré ninguno: cada swing tiene que tener al menos "
                  f"{QUIETO_MIN_S:.1f} s quieta antes y después.")

    resultados = []
    for i in impactos:
        ang, cara = angulo_en_impacto(q, giro, i, congelar_s=args.congelar / 1000, cara=args.cara)
        resultados.append((i, ang, cara))

    print(f"\n{len(impactos)} impactos ({origen})")
    if resultados:
        print("   n   tiempo   cara    ángulo")
        for n, (i, ang, cara) in enumerate(resultados, 1):
            print(f"{n:4d} {t[i]:7.2f} s  {cara:5s} {ang:+7.1f}°")

    fig, ejes = plt.subplots(2, 1, sharex=True, figsize=(13, 7))
    ejes[0].plot(t, roja, lw=0.9, color="tab:red", label="cara roja (Madgwick)")
    ejes[0].axhline(0, color="0.5", lw=0.8)
    for i, ang, cara in resultados:
        color = "tab:red" if cara == "roja" else "k"
        ejes[0].plot(t[i], ang, "o", color=color, ms=5)
        ejes[0].annotate(f"{ang:+.0f}°", (t[i], ang), textcoords="offset points", xytext=(0, 7),
                         ha="center", fontsize=8, color=color)
    ejes[0].plot([], [], "o", color="k", ms=5, label="impacto (color = cara que golpea)")
    ejes[0].set_ylabel("ángulo (°)  − cerrada / + abierta")
    ejes[0].set_ylim(-95, 95)
    for k, eje in enumerate("xyz"):
        ejes[1].plot(t, giro[:, k], lw=0.8, label=f"g{eje}")
    ejes[1].set_ylabel("giro (°/s)")
    ejes[1].set_xlabel("tiempo (s)")
    for eje in ejes:
        for i, _, _ in resultados:
            eje.axvline(t[i], color="tab:red", alpha=0.2, lw=1)
        eje.legend(loc="upper right", fontsize=8)
        eje.grid(alpha=0.3)
    fig.suptitle(f"{args.archivo} · ángulo de la cara")
    fig.tight_layout()

    if args.png:
        fig.savefig(args.png, dpi=110)
        print(f"Gráfico guardado en {args.png}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
