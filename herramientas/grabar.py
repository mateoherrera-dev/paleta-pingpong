"""Graba lo que manda la paleta por el puerto serie en un CSV.

Uso:
    python grabar.py --listar
    python grabar.py --puerto COM5 --jugador mateo --golpe topspin_derecha

Cortar con Ctrl+C. El archivo queda en datos/crudos/ con fecha, jugador y golpe en el nombre.
"""
import argparse
import datetime
import pathlib
import time

import serial
from serial.tools import list_ports

from senal import COLUMNAS, GOLPES

CARPETA = pathlib.Path(__file__).resolve().parent.parent / "datos" / "crudos"


def main():
    parser = argparse.ArgumentParser(description="Graba una sesión de la paleta")
    parser.add_argument("--puerto", help="por ejemplo COM5 en Windows o /dev/ttyACM0 en Linux")
    parser.add_argument("--jugador", help="nombre de quien juega, sin espacios")
    parser.add_argument("--golpe", choices=GOLPES + ["libre"])
    parser.add_argument("--baudios", type=int, default=921600)
    parser.add_argument("--listar", action="store_true", help="muestra los puertos disponibles")
    args = parser.parse_args()

    if args.listar or not args.puerto:
        for puerto in list_ports.comports():
            print(f"{puerto.device}  {puerto.description}")
        return
    if not args.jugador or not args.golpe:
        parser.error("faltan --jugador y --golpe")

    CARPETA.mkdir(parents=True, exist_ok=True)
    marca = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    ruta = CARPETA / f"{marca}_{args.jugador}_{args.golpe}.csv"

    muestras = impactos = 0
    with serial.Serial(args.puerto, args.baudios, timeout=1) as puerto, open(ruta, "w", newline="") as archivo:
        archivo.write(",".join(COLUMNAS) + "\n")
        puerto.reset_input_buffer()
        print(f"Grabando {args.golpe} de {args.jugador}. Ctrl+C para terminar.")
        ultimo_aviso = time.monotonic()
        try:
            while True:
                linea = puerto.readline().decode("ascii", errors="ignore").strip()
                if linea.startswith("#"):
                    print(f"\n{linea}")
                    continue
                campos = linea.split(",")
                if len(campos) != len(COLUMNAS):
                    continue  # línea vacía o cortada
                archivo.write(linea + "\n")
                muestras += 1
                impactos += campos[-1] == "1"
                if time.monotonic() - ultimo_aviso >= 1:
                    print(f"\r{muestras} muestras · {impactos} impactos", end="", flush=True)
                    ultimo_aviso = time.monotonic()
        except KeyboardInterrupt:
            pass

    print(f"\nGuardado en {ruta} ({muestras} muestras, {impactos} impactos)")


if __name__ == "__main__":
    main()
