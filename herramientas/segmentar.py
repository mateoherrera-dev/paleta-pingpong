"""Segmenta los archivos crudos en ventanas individuales para Edge Impulse.

Uso:
    python herramientas/segmentar.py
"""
import pandas as pd
import pathlib

def main():
    crudos_dir = pathlib.Path("datos/crudos")
    salida_dir = pathlib.Path("datos/segmentados")
    
    if not crudos_dir.exists():
        print(f"No existe la carpeta {crudos_dir}. Asegurate de grabar datos primero.")
        return

    salida_dir.mkdir(parents=True, exist_ok=True)

    # Parámetros de la ventana (1000 Hz): 120 ms antes, 80 ms después = 200 ms total
    VENTANA_PRE = 120
    VENTANA_POST = 80

    archivos = list(crudos_dir.glob("*.csv"))
    if not archivos:
        print(f"No hay archivos CSV en {crudos_dir}")
        return

    total_ventanas = 0

    for ruta_csv in archivos:
        df = pd.read_csv(ruta_csv)
        
        # Validación rápida para asegurarse de que sea un archivo de la placa
        if 'impacto' not in df.columns or 't_us' not in df.columns:
            continue

        indices_impacto = df.index[df['impacto'] == 1].tolist()
        if not indices_impacto:
            continue
            
        print(f"Procesando {ruta_csv.name} ({len(indices_impacto)} impactos encontrados)...")

        # Inferir la etiqueta a partir del nombre original
        # GOLPES permitidos según senal.py
        etiqueta = "desconocido"
        for golpe in ["topspin_derecha", "topspin_reves", "empuje_derecha", "empuje_reves"]:
            if golpe in ruta_csv.name:
                etiqueta = golpe
                break

        for i, idx in enumerate(indices_impacto):
            inicio = idx - VENTANA_PRE
            fin = idx + VENTANA_POST
            
            # Si el impacto está muy cerca del borde del archivo, lo descartamos
            if inicio < 0 or fin > len(df):
                continue
                
            ventana = df.iloc[inicio:fin].copy()
            
            # Reindexar el timestamp para que arranque en 0 ms
            ventana['timestamp'] = ((ventana['t_us'] - ventana['t_us'].iloc[0]) / 1000).astype(int)
            
            # Renombrar columnas para estandarizarlas en Edge Impulse
            ventana = ventana.rename(columns={
                'ax_g': 'ax', 'ay_g': 'ay', 'az_g': 'az',
                'gx_dps': 'gx', 'gy_dps': 'gy', 'gz_dps': 'gz'
            })
            
            columnas_exportar = ['timestamp', 'ax', 'ay', 'az', 'gx', 'gy', 'gz']
            ventana_limpia = ventana[columnas_exportar]
            
            # Formato de nombre especial para Edge Impulse: "etiqueta.identificador.csv"
            # Esto permite que Edge Impulse infiera la etiqueta "topspin_derecha" automáticamente.
            nombre_archivo = salida_dir / f"{etiqueta}.{ruta_csv.stem}_impacto_{i+1}.csv"
            
            ventana_limpia.to_csv(nombre_archivo, index=False)
            total_ventanas += 1

    print(f"\n¡Listo! Se generaron {total_ventanas} ventanas en '{salida_dir}'.")
    print("Podés subir esta carpeta directamente a Edge Impulse.")

if __name__ == "__main__":
    main()
