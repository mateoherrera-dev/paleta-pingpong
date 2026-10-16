"""Graba lo que manda la paleta por el puerto serie en un CSV.

Uso:
    python grabar.py --listar
    python grabar.py --puerto COM5 --jugador mateo --golpe topspin_derecha
    python grabar.py --puerto COM5 --jugador prueba --golpe libre --segundos 300

Cortar con Ctrl+C (o esperar --segundos). El archivo queda en datos/crudos/ con fecha, jugador y
golpe en el nombre. Si se pierden muestras en el camino (huecos en t_us), lo avisa en vivo y al final.
"""
import argparse
import datetime
import pathlib
import re
import time

import serial
from serial.tools import list_ports

from senal import COLUMNAS, GOLPES

CARPETA = pathlib.Path(__file__).resolve().parent.parent / "datos" / "crudos"
BUFFER_PUERTO = 1 << 20  # 1 MB: si Windows se traba un momento, que el buffer del puerto no se llene

# Una muestra tal como la imprime paleta.ino: t_us y 3 decimales en g, 1 decimal en °/s.
# Si se pierden bytes en el camino, dos líneas pueden quedar pegadas y tener igual 8 columnas
# (pasó el 16/10: "6505765060257,..."): el formato exacto y el tiempo las delatan.
MUESTRA = re.compile(r"\d{1,10}(,-?\d+\.\d{3}){3}(,-?\d+\.\d){3},[01]")


def lineas(puerto):
    """Lee el puerto de a bloques y devuelve las líneas completas.

    readline() de pyserial pide byte por byte: a 1000 líneas por segundo son ~50.000 llamadas
    por segundo, la compu se atrasa, el buffer del puerto se llena y se pierden líneas.
    """
    resto = b""
    while True:
        resto += puerto.read(puerto.in_waiting or 1)
        *completas, resto = resto.split(b"\n")
        for cruda in completas:
            yield cruda.decode("ascii", errors="ignore").strip()


def listar_puertos():
    for puerto in list_ports.comports():
        nota = {0x303A: "  ← USB nativo de la ESP32 (conector OTG): usar este",
                0x1A86: "  ← CH340 (conector TTL): con cable largo pierde datos"}.get(puerto.vid, "")
        print(f"{puerto.device}  {puerto.description}{nota}")


def main():
    parser = argparse.ArgumentParser(description="Graba una sesión de la paleta")
    parser.add_argument("--puerto", help="por ejemplo COM5 en Windows o /dev/ttyACM0 en Linux")
    parser.add_argument("--jugador", help="nombre de quien juega, sin espacios")
    parser.add_argument("--golpe", choices=GOLPES + ["libre"])
    parser.add_argument("--baudios", type=int, default=921600)
    parser.add_argument("--segundos", type=float, help="cortar solo después de estos segundos")
    parser.add_argument("--listar", action="store_true", help="muestra los puertos disponibles")
    args = parser.parse_args()

    if args.listar or not args.puerto:
        listar_puertos()
        return
    if not args.jugador or not args.golpe:
        parser.error("faltan --jugador y --golpe")

    try:
        puerto = serial.Serial(args.puerto, args.baudios, timeout=1)
    except serial.SerialException as error:
        ocupado = "denegado" in str(error) or "PermissionError" in str(error)
        print(f"No puedo abrir {args.puerto}: "
              + ("lo está usando otro programa (¿el Serial Monitor del IDE?)." if ocupado else "no existe."))
        print("Puertos disponibles:")
        listar_puertos()
        return

    CARPETA.mkdir(parents=True, exist_ok=True)
    marca = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    ruta = CARPETA / f"{marca}_{args.jugador}_{args.golpe}.csv"

    muestras = impactos = perdidas = rotas = 0
    t_anterior = t_rechazado = None
    with puerto, open(ruta, "w", newline="") as archivo:
        if hasattr(puerto, "set_buffer_size"):  # solo existe en Windows
            puerto.set_buffer_size(rx_size=BUFFER_PUERTO)
        archivo.write(",".join(COLUMNAS) + "\n")
        puerto.reset_input_buffer()
        print(f"Grabando {args.golpe} de {args.jugador}. Ctrl+C para terminar.")
        inicio = ultimo_aviso = time.monotonic()
        try:
            for linea in lineas(puerto):
                if linea.startswith("#"):
                    print(f"\n{linea}")
                    continue
                if not MUESTRA.fullmatch(linea):
                    # vacía, cortada o pegada; antes de la primera muestra es el arranque de la placa
                    rotas += linea != "" and t_anterior is not None
                    continue
                campos = linea.split(",")
                t = int(campos[0])
                if t_anterior is not None and not 0 < t - t_anterior < 1_000_000:
                    # Tiempo imposible: la línea quedó pegada con otra, o la placa se reinició.
                    # Si sigue a la que se rechazó recién, es un reinicio: se acepta y se sigue de ahí.
                    if t_rechazado is None or not 0 < t - t_rechazado < 2000:
                        t_rechazado = t
                        rotas += 1
                        continue
                elif t_anterior is not None and t - t_anterior > 1500:  # una muestra cada ~1000 µs
                    perdidas += round((t - t_anterior) / 1000) - 1
                t_anterior = t
                t_rechazado = None
                archivo.write(linea + "\n")
                muestras += 1
                impactos += campos[-1] == "1"
                ahora = time.monotonic()
                if ahora - ultimo_aviso >= 1:
                    print(f"\r{muestras} muestras · {impactos} impactos · {perdidas} perdidas", end="", flush=True)
                    ultimo_aviso = ahora
                if args.segundos and ahora - inicio >= args.segundos:
                    break
        except KeyboardInterrupt:
            pass

    print(f"\nGuardado en {ruta} ({muestras} muestras, {impactos} impactos)")
    if perdidas or rotas:
        print(f"Ojo: se perdieron {perdidas} muestras en el camino y llegaron {rotas} líneas rotas")


if __name__ == "__main__":
    main()
