"""Funciones compartidas para leer sesiones y procesar la señal de la paleta.

Formato de los archivos y ejes: docs/CONTRATOS.md
"""
import numpy as np

COLUMNAS = ["t_us", "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps", "impacto"]
GOLPES = ["topspin_derecha", "topspin_reves", "empuje_derecha", "empuje_reves"]
FS = 1000  # muestras por segundo


def cargar_sesion(ruta):
    """Lee un CSV de sesión y devuelve tiempo (s), aceleración (g), giro (°/s) e impactos de la placa."""
    datos = np.loadtxt(ruta, delimiter=",", skiprows=1)
    if datos.ndim == 1:
        datos = datos[np.newaxis, :]
    t = (datos[:, 0] - datos[0, 0]) / 1e6
    return {
        "t": t,
        "acel": datos[:, 1:4],
        "giro": datos[:, 4:7],
        "impacto": datos[:, 7].astype(int),
    }


def revisar_muestreo(t):
    """Devuelve la frecuencia real de muestreo y cuántas muestras se perdieron."""
    pasos = np.diff(t)
    periodo = np.median(pasos)
    perdidas = int(np.sum(np.round(pasos / periodo) - 1))
    return 1 / periodo, perdidas


def detectar_impactos(acel, umbral_g=1.5, refractario_s=0.3, fs=FS):
    """Busca saltos bruscos de aceleración entre muestras seguidas.

    Es el mismo algoritmo que corre en la placa (firmware/paleta/paleta.ino),
    así se puede ajustar el umbral acá y después copiarlo al firmware.
    Devuelve los índices de los impactos y la señal de salto (una muestra más corta).
    """
    salto = np.linalg.norm(np.diff(acel, axis=0), axis=1)
    impactos = []
    ultimo = -np.inf
    for i in np.flatnonzero(salto > umbral_g):
        if i - ultimo >= refractario_s * fs:
            impactos.append(i + 1)
            ultimo = i
    return np.array(impactos, dtype=int), salto


def cortar_ventanas(sesion, impactos, antes_s=0.5, despues_s=0.2, fs=FS):
    """Corta una ventana de los 6 ejes alrededor de cada impacto (para entrenar el modelo)."""
    antes, despues = int(antes_s * fs), int(despues_s * fs)
    senal = np.hstack([sesion["acel"], sesion["giro"]])
    return [senal[i - antes:i + despues] for i in impactos if i - antes >= 0 and i + despues <= len(senal)]
