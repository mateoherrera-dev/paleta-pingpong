import serial
import time
import csv
import argparse
import threading
from collections import deque
import sys

def capturar(puerto, baudrate, archivo_salida):
    try:
        ser = serial.Serial(puerto, baudrate)
    except serial.SerialException as e:
        print(f"Error abriendo el puerto {puerto}: {e}")
        sys.exit(1)

    print(f"Conectado a {puerto} a {baudrate} baudios.")
    print(f"Guardando captura en: {archivo_salida}")
    print("Presiona Ctrl+C para detener la captura...")

    buffer_datos = deque()
    corriendo = True

    # Hilo trabajador para escribir a disco
    def escritor_disco():
        with open(archivo_salida, mode='w', newline='') as f:
            writer = csv.writer(f)
            # Escribir cabecera
            writer.writerow(["timestamp_ms", "ax", "ay", "az", "gx", "gy", "gz"])
            
            while corriendo or len(buffer_datos) > 0:
                if len(buffer_datos) > 0:
                    linea_cruda = buffer_datos.popleft()
                    try:
                        # Asumimos que el paquete viene como CSV de texto (valores separados por coma)
                        linea_texto = linea_cruda.decode('utf-8').strip()
                        datos = linea_texto.split(',')
                        
                        # Guardar solo si tiene el largo correcto (1 tiempo + 6 señales)
                        if len(datos) == 7:
                            writer.writerow(datos)
                    except UnicodeDecodeError:
                        # Ignorar basura en el puerto serie (especialmente al inicio)
                        pass
                else:
                    time.sleep(0.01)

    # Iniciar hilo de escritura
    t_escritura = threading.Thread(target=escritor_disco, daemon=True)
    t_escritura.start()

    # Bucle principal de lectura no bloqueante
    try:
        while True:
            if ser.in_waiting > 0:
                linea = ser.readline()
                buffer_datos.append(linea)
    except KeyboardInterrupt:
        print("\nCaptura detenida por el usuario. Vaciando el buffer a disco...")
        corriendo = False
        t_escritura.join()
        ser.close()
        print("Guardado finalizado exitosamente.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Receptor serie para datos de captura MPU-6500")
    parser.add_argument("--puerto", "-p", required=True, help="Puerto serie (ej. COM3 o /dev/ttyUSB0)")
    parser.add_argument("--baudrate", "-b", type=int, default=921600, help="Velocidad del puerto serie (default: 921600)")
    parser.add_argument("--salida", "-o", required=True, help="Archivo CSV de salida (ej. tomas_TD_01.csv)")
    
    args = parser.parse_args()
    capturar(args.puerto, args.baudrate, args.salida)
