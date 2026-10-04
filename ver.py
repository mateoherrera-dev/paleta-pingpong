import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys

def visualizar(archivo_csv):
    print(f"Cargando datos de {archivo_csv}...")
    try:
        df = pd.read_csv(archivo_csv)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)
        
    # Validar formato
    columnas_esperadas = ["timestamp_ms", "ax", "ay", "az", "gx", "gy", "gz"]
    if not all(col in df.columns for col in columnas_esperadas):
        print(f"Error: El archivo no contiene las columnas correctas.")
        print(f"Esperadas: {columnas_esperadas}")
        print(f"Encontradas: {list(df.columns)}")
        sys.exit(1)

    # Normalizar tiempo para que empiece en 0
    t = df['timestamp_ms'] - df['timestamp_ms'].iloc[0]

    # Crear gráfico con 2 subplots que comparten el eje X para mantener el zoom sincronizado
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
    
    # Gráfico Acelerómetro
    ax1.plot(t, df['ax'], label='ax', color='red', alpha=0.8)
    ax1.plot(t, df['ay'], label='ay', color='green', alpha=0.8)
    ax1.plot(t, df['az'], label='az', color='blue', alpha=0.8)
    ax1.set_ylabel("Aceleración (g)")
    ax1.set_title("Acelerómetro")
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Gráfico Giroscopio
    ax2.plot(t, df['gx'], label='gx', color='red', alpha=0.8)
    ax2.plot(t, df['gy'], label='gy', color='green', alpha=0.8)
    ax2.plot(t, df['gz'], label='gz', color='blue', alpha=0.8)
    ax2.set_xlabel("Tiempo (ms)")
    ax2.set_ylabel("Velocidad Angular (deg/s)")
    ax2.set_title("Giroscopio")
    ax2.legend(loc='upper right')
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.suptitle(f"Visualización de Señales: {archivo_csv}")
    plt.tight_layout()
    
    print("Mostrando gráfico interactivo...")
    print("TIP: Utiliza la herramienta de lupa (Zoom to rectangle) de la barra inferior para ver los picos.")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta de visualización de datos inerciales")
    parser.add_argument("archivo", help="Ruta del archivo CSV a visualizar")
    args = parser.parse_args()
    
    visualizar(args.archivo)
