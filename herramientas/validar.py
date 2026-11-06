"""Mide cuánto acierta el modelo de la placa en las tandas de validación ciega.

Cada tanda se graba con grabar.py (un golpe por tanda, como siempre). grabar.py deja al lado del CSV
un _placa.txt con lo que dijo el modelo en cada impacto ("# Golpe N: TD 87 % ..."). Acá se cruza
eso con el golpe del nombre del archivo, se sacan los descartes anotados en NOTAS*.md (misma tabla
que crudos/NOTAS.md: archivo e impacto) y se arma la precisión y la matriz de confusión.

Uso (desde herramientas/; por defecto lee datos/validacion/):
    python validar.py
    python validar.py --confianza-min 60
"""
import argparse
import csv
import pathlib
import re
from collections import Counter, defaultdict

from senal import GOLPES

CARPETA = pathlib.Path(__file__).resolve().parent.parent / "datos" / "validacion"
META = 80  # % de aciertos con externos (hito de la clase 5 en PLAN.md)

# Lo que imprime paleta.ino en mandarGolpe() y su golpe en el nombre de archivo
ABREVIATURAS = {"TD": "topspin_derecha", "TR": "topspin_reves", "ED": "empuje_derecha",
                "ER": "empuje_reves", "ruido": "ruido"}
CLASES = ["TD", "TR", "ED", "ER", "ruido"]
SIN_RECONOCER = "dudoso"  # predicción por debajo de --confianza-min
LENTO = "lento"  # el firmware lo descartó por giro máximo bajo (no le llega a la app)
# "# Golpe N: TD 87 % ..." lo manda a la app; "# Descartado: TD 80 % ..., giro máx 250 °/s (swing
# muy lento)" es el filtro del PR #29: no le llega a la app, así que cuenta como ruido o como lento.
GOLPE_PLACA = re.compile(r"# (?:Golpe \d+|Descartado): (TD|TR|ED|ER|ruido) (\d+) %(.*)")
NOMBRE = re.compile(r"\d{4}-\d{2}-\d{2}_\d{6}_(.+)_(" + "|".join(GOLPES) + r")$")
DESCARTE = re.compile(r"^\|\s*`([^`]+\.csv)`\s*\|\s*(\d+)\s*\|")


def leer_descartes(carpeta):
    """{archivo.csv: {impactos a descartar}} de todos los NOTAS*.md de la carpeta."""
    descartes = defaultdict(set)
    for notas in carpeta.glob("NOTAS*.md"):
        for linea in notas.read_text(encoding="utf-8").splitlines():
            m = DESCARTE.match(linea.strip())
            if m:
                descartes[m.group(1)].add(int(m.group(2)))
    return descartes


def contar_impactos(ruta_csv):
    with open(ruta_csv, newline="") as archivo:
        return sum(fila[-1] == "1" for fila in csv.reader(archivo) if fila)


def leer_predicciones(ruta_placa):
    """{impacto del CSV: (clase, confianza)} y los avisos de lo que no cierra."""
    predicciones, avisos = {}, []
    with open(ruta_placa, encoding="utf-8") as archivo:
        next(archivo, None)  # encabezado
        for fila in archivo:
            impacto, _, linea = fila.rstrip("\n").split("\t", 2)
            m = GOLPE_PLACA.match(linea)
            if not m:
                continue
            impacto = int(impacto)
            if impacto == 0:
                avisos.append("un golpe de la placa llegó antes del primer impacto del CSV (se ignora)")
            elif impacto in predicciones:
                avisos.append(f"dos golpes de la placa para el impacto {impacto} (queda el primero)")
            else:
                lento = linea.startswith("# Descartado") and "muy lento" in m.group(3) and m.group(1) != "ruido"
                predicciones[impacto] = (LENTO if lento else m.group(1), int(m.group(2)))
    return predicciones, avisos


def matriz(tiros, columnas):
    filas = [c for c in CLASES[:4] if any(real == c for real, _ in tiros)]
    cuenta = Counter(tiros)
    ancho = max(len(c) for c in columnas) + 2
    lineas = ["real \\ modelo".ljust(16) + "".join(c.rjust(ancho) for c in columnas) + "   aciertos"]
    for real in filas:
        total = sum(cuenta[(real, p)] for p in columnas)
        bien = cuenta[(real, real)]
        celdas = "".join(str(cuenta[(real, p)]).rjust(ancho) for p in columnas)
        lineas.append(f"{real.ljust(16)}{celdas}   {bien}/{total} ({100 * bien / total:.0f} %)")
    return "\n".join(lineas)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--carpeta", type=pathlib.Path, default=CARPETA)
    parser.add_argument("--confianza-min", type=int, default=0,
                        help="por debajo de esta certeza (%%) el golpe cuenta como dudoso (mal)")
    args = parser.parse_args()

    descartes = leer_descartes(args.carpeta)
    por_jugador = defaultdict(list)
    for ruta_csv in sorted(args.carpeta.glob("*.csv")):
        nombre = NOMBRE.match(ruta_csv.stem)
        if not nombre or nombre.group(2) == "ruido":
            continue
        jugador, golpe = nombre.groups()
        real = next(a for a, g in ABREVIATURAS.items() if g == golpe)
        ruta_placa = ruta_csv.with_name(ruta_csv.stem + "_placa.txt")
        if not ruta_placa.exists():
            print(f"{ruta_csv.name}: no tiene _placa.txt (¿grabado con un grabar.py viejo?), se saltea")
            continue

        predicciones, avisos = leer_predicciones(ruta_placa)
        impactos = contar_impactos(ruta_csv)
        afuera = descartes.get(ruta_csv.name, set())
        validos = [i for i in range(1, impactos + 1) if i not in afuera]
        sin_prediccion = [i for i in validos if i not in predicciones]
        for i in validos:
            if i in predicciones:
                clase, confianza = predicciones[i]
                por_jugador[jugador].append((real, clase if confianza >= args.confianza_min else SIN_RECONOCER))

        bien = sum(predicciones[i][0] == real for i in validos if i in predicciones)
        evaluados = len(validos) - len(sin_prediccion)
        resumen = f"{ruta_csv.name}: {impactos} impactos, {len(afuera)} descartados, {bien}/{evaluados} bien"
        print(resumen)
        if sin_prediccion:
            avisos.append(f"impactos sin golpe de la placa (no cuentan): {sin_prediccion}")
        for aviso in avisos:
            print(f"    ojo: {aviso}")

    if not por_jugador:
        print(f"No hay tandas con _placa.txt en {args.carpeta}")
        return

    todos = [tiro for tiros in por_jugador.values() for tiro in tiros]
    columnas = CLASES + [c for c in (LENTO, SIN_RECONOCER) if any(p == c for _, p in todos)]
    for jugador, tiros in por_jugador.items():
        bien = sum(r == p for r, p in tiros)
        print(f"\n== {jugador}: {bien}/{len(tiros)} ({100 * bien / len(tiros):.0f} %)")
        print(matriz(tiros, columnas))

    bien = sum(r == p for r, p in todos)
    precision = 100 * bien / len(todos)
    print(f"\n== Total ({len(por_jugador)} jugadores): {bien}/{len(todos)} ({precision:.1f} %)")
    print(matriz(todos, columnas))
    print(f"\nMeta de la clase 5: {META} % -> {'cumple' if precision >= META else 'NO cumple'}")


if __name__ == "__main__":
    main()
