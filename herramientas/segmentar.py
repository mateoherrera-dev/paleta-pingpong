"""Segmenta los archivos crudos en ventanas individuales para Edge Impulse.

Corta ventanas de 196 ms (120 ms antes del centro, 76 ms después) a 1000 Hz,
coincidiendo exactamente con ML_BUFFER_LONGITUD_ESPERADA en firmware/paleta/ml_inference.h.

Soporta:
  1. Golpes técnicos: segmentación por trigger de impacto (df['impacto'] == 1).
  2. Filtrado de descartes: detecta archivos NOTAS*.md y separa los tiros defectuosos
     (red, afuera, etc.) en datos/segmentados_descartados/.
  3. Ruido / not_a_swing:
     - Impactos físicos accidentales (toques, malabares, mesa).
     - Swings al aire sin choque: detección de picos de rotación (|ω| > 250 °/s).
     - Caminata y manipulación: ventanas periódicas con movimiento activo.

Uso:
    python herramientas/segmentar.py
    python herramientas/segmentar.py --crudos datos/crudos --salida datos/segmentados
"""
import argparse
import pathlib
import numpy as np
import pandas as pd

# Parámetros de la ventana (1000 Hz): 120 ms antes, 76 ms después = 196 ms total.
VENTANA_PRE = 120
VENTANA_POST = 76
LONGITUD_VENTANA = VENTANA_PRE + VENTANA_POST  # 196 muestras

GOLPES_VALIDOS = ["topspin_derecha", "topspin_reves", "empuje_derecha", "empuje_reves", "ruido"]


def exportar_ventana(df, idx_centro, ruta_salida):
    """Recorta 196 muestras alrededor de idx_centro y guarda el CSV para Edge Impulse."""
    inicio = idx_centro - VENTANA_PRE
    fin = idx_centro + VENTANA_POST
    if inicio < 0 or fin > len(df):
        return False

    ventana = df.iloc[inicio:fin].copy()
    ventana["timestamp"] = ((ventana["t_us"] - ventana["t_us"].iloc[0]) / 1000).astype(int)
    columnas_exportar = ["timestamp", "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps"]
    ventana[columnas_exportar].to_csv(ruta_salida, index=False)
    return True


def detectar_picos_giro(df, min_dps=250.0, distancia=400, indices_excluidos=None):
    """Detecta picos de rotación (swings al aire) donde la paleta gira rápido pero sin choque."""
    if indices_excluidos is None:
        indices_excluidos = []

    omega = np.sqrt(df["gx_dps"] ** 2 + df["gy_dps"] ** 2 + df["gz_dps"] ** 2).to_numpy()
    n = len(omega)
    picos = []
    mitad = distancia // 2

    for i in range(VENTANA_PRE, n - VENTANA_POST):
        val = omega[i]
        if val < min_dps:
            continue

        # Evitar solapamiento con impactos u otros picos ya tomados
        if any(abs(i - excl) < distancia for excl in (indices_excluidos + picos)):
            continue

        # Verificar si es el máximo local en su entorno
        vecindad = omega[max(0, i - mitad) : min(n, i + mitad + 1)]
        if val == np.max(vecindad):
            picos.append(i)

    return picos


def detectar_movimiento_continuo(df, paso=1000, indices_excluidos=None):
    """Extrae ventanas periódicas durante caminata, recogida de pelotas o reacomodo de grip."""
    if indices_excluidos is None:
        indices_excluidos = []

    omega = np.sqrt(df["gx_dps"] ** 2 + df["gy_dps"] ** 2 + df["gz_dps"] ** 2).to_numpy()
    ax = df["ax_g"].to_numpy()
    ay = df["ay_g"].to_numpy()
    az = df["az_g"].to_numpy()
    n = len(df)
    muestras_mov = []

    for i in range(VENTANA_PRE, n - VENTANA_POST, paso):
        if any(abs(i - excl) < 300 for excl in (indices_excluidos + muestras_mov)):
            continue

        inicio = i - VENTANA_PRE
        fin = i + VENTANA_POST
        sub_omega = omega[inicio:fin]
        sub_ax = ax[inicio:fin]
        sub_ay = ay[inicio:fin]
        sub_az = az[inicio:fin]

        std_a = (np.std(sub_ax) + np.std(sub_ay) + np.std(sub_az)) / 3.0
        mean_w = np.mean(sub_omega)

        # Movimiento activo perceptible (evita paleta quieta apoyada sobre la mesa)
        if std_a > 0.04 or mean_w > 20.0:
            muestras_mov.append(i)

    return muestras_mov


def inferir_etiqueta(nombre_archivo):
    """Deduce la clase a partir del nombre del archivo."""
    for golpe in GOLPES_VALIDOS:
        if golpe in nombre_archivo:
            return golpe
    return "desconocido"


def cargar_descartes(crudos_dir):
    """Lee archivos NOTAS*.md en la carpeta de crudos y devuelve { 'archivo.csv': {indices_impacto_a_descartar} }."""
    descartes = {}
    for ruta_md in crudos_dir.glob("*.md"):
        try:
            with open(ruta_md, "r", encoding="utf-8") as f:
                for linea in f:
                    partes = [p.strip().strip("`") for p in linea.split("|")]
                    if len(partes) >= 3:
                        archivo = partes[1]
                        impacto_str = partes[2]
                        if archivo.endswith(".csv") and impacto_str.isdigit():
                            if archivo not in descartes:
                                descartes[archivo] = set()
                            descartes[archivo].add(int(impacto_str))
        except Exception as e:
            print(f"Aviso al leer descartes de {ruta_md.name}: {e}")
    return descartes


def main():
    parser = argparse.ArgumentParser(description="Segmenta CSVs crudos de IMU en ventanas para Edge Impulse.")
    parser.add_argument("--crudos", type=str, default="datos/crudos", help="Carpeta con archivos CSV crudos")
    parser.add_argument("--salida", type=str, default="datos/segmentados", help="Carpeta de salida para ventanas válidas")
    parser.add_argument("--descartados", type=str, default="datos/segmentados_descartados", help="Carpeta para ventanas descartadas según NOTAS*.md")
    args = parser.parse_args()

    crudos_dir = pathlib.Path(args.crudos)
    salida_dir = pathlib.Path(args.salida)
    descartados_dir = pathlib.Path(args.descartados)

    if not crudos_dir.exists():
        print(f"No existe la carpeta '{crudos_dir}'. Asegurate de colocar los archivos crudos allí.")
        return

    salida_dir.mkdir(parents=True, exist_ok=True)
    descartados_dir.mkdir(parents=True, exist_ok=True)

    descartes_por_archivo = cargar_descartes(crudos_dir)
    if descartes_por_archivo:
        total_descartes_anotados = sum(len(v) for v in descartes_por_archivo.values())
        print(f"Descartes detectados en notas: {total_descartes_anotados} impactos en {len(descartes_por_archivo)} archivo(s).")

    archivos = sorted(list(crudos_dir.glob("*.csv")))
    if not archivos:
        print(f"No hay archivos CSV en '{crudos_dir}'.")
        return

    total_validas = 0
    total_descartadas = 0

    for ruta_csv in archivos:
        try:
            df = pd.read_csv(ruta_csv)
        except Exception as e:
            print(f"Error al leer {ruta_csv.name}: {e}")
            continue

        # Validación mínima de columnas requeridas
        columnas_requeridas = {"t_us", "ax_g", "ay_g", "az_g", "gx_dps", "gy_dps", "gz_dps"}
        if not columnas_requeridas.issubset(df.columns):
            continue

        etiqueta = inferir_etiqueta(ruta_csv.name)
        indices_impacto = df.index[df["impacto"] == 1].tolist() if "impacto" in df.columns else []
        descartes_este_archivo = descartes_por_archivo.get(ruta_csv.name, set())

        validas_archivo = 0
        descartadas_archivo = 0

        # 1. Ventanas por impacto físico (golpes técnicos o choques de ruido)
        for i, idx in enumerate(indices_impacto):
            numero_impacto = i + 1
            es_descarte = numero_impacto in descartes_este_archivo
            destino = descartados_dir if es_descarte else salida_dir

            nombre_salida = destino / f"{etiqueta}.{ruta_csv.stem}_impacto_{numero_impacto}.csv"
            if exportar_ventana(df, idx, nombre_salida):
                if es_descarte:
                    descartadas_archivo += 1
                else:
                    validas_archivo += 1

        # 2. Si es archivo de ruido, extraer también swings al aire y movimientos sin choque
        if etiqueta == "ruido":
            # Swings al aire (|ω| > 250 °/s sin impacto)
            picos_swing = detectar_picos_giro(df, min_dps=250.0, distancia=400, indices_excluidos=indices_impacto)
            for j, idx in enumerate(picos_swing):
                nombre_salida = salida_dir / f"{etiqueta}.{ruta_csv.stem}_swing_{j+1}.csv"
                if exportar_ventana(df, idx, nombre_salida):
                    validas_archivo += 1

            # Movimiento continuo (caminata, manipulación de paleta)
            excluidos_totales = indices_impacto + picos_swing
            muestras_mov = detectar_movimiento_continuo(df, paso=1000, indices_excluidos=excluidos_totales)
            for k, idx in enumerate(muestras_mov):
                nombre_salida = salida_dir / f"{etiqueta}.{ruta_csv.stem}_movimiento_{k+1}.csv"
                if exportar_ventana(df, idx, nombre_salida):
                    validas_archivo += 1

            detalles_ruido = f"({len(indices_impacto)} impactos, {len(picos_swing)} swings al aire, {len(muestras_mov)} caminata/mov)"
            print(f"Procesando {ruta_csv.name} [{etiqueta}]: {validas_archivo} válidas {detalles_ruido}")
        else:
            if descartadas_archivo > 0:
                print(f"Procesando {ruta_csv.name} [{etiqueta}]: {validas_archivo} válidas, {descartadas_archivo} descartadas en notas")
            else:
                print(f"Procesando {ruta_csv.name} [{etiqueta}]: {validas_archivo} impactos")

        total_validas += validas_archivo
        total_descartadas += descartadas_archivo

    print(f"\n¡Listo! Ventanas válidas generadas: {total_validas} en '{salida_dir}'.")
    if total_descartadas > 0:
        print(f"Ventanas descartadas: {total_descartadas} en '{descartados_dir}'.")
    print("Podés subir la carpeta de segmentados directamente a Edge Impulse.")


if __name__ == "__main__":
    main()
