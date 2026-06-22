#!/usr/bin/env python3
"""
Verifica y completa el RBD de los liceos emblemáticos cruzando la lista de
referencia (nombres tomados de Wikipedia, confirmados manualmente) contra el
Directorio Oficial de Establecimientos del MINEDUC.

Filosofía: el RBD no se escribe a mano. Se obtiene haciendo *match* del nombre
y la comuna contra la fuente de verdad (el Directorio), de modo que la
asignación sea reproducible y auditable.

Uso:
    python scripts/referencias/verificar_rbd_emblematicos.py \
        --directorio raw/directorio_establecimientos.csv

Entrada:
    - scripts/referencias/liceos_emblematicos.csv  (lista curada de nombres)
    - Directorio del MINEDUC (CSV), descargado en raw/. Disponible en
      datosabiertos.mineduc.cl -> "Directorio de establecimientos educacionales".

Salida:
    - Sobrescribe liceos_emblematicos.csv con la columna `rbd` completada y
      `rbd_verificado` = si/revisar/no segun la calidad del match.
    - Imprime un reporte con el puntaje de cada match para revision humana.

Sin dependencias externas: usa solo la biblioteca estandar.
"""

from __future__ import annotations

import argparse
import csv
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

# Rutas por defecto (relativas a la raiz del repo).
AQUI = Path(__file__).resolve().parent
REF_CSV = AQUI / "liceos_emblematicos.csv"

# Umbral de similitud para aceptar un match automaticamente.
UMBRAL_AUTO = 0.92      # >= esto -> rbd_verificado = "si"
UMBRAL_REVISAR = 0.75   # entre revisar y auto -> "revisar" (mirar a mano)


def normalizar(texto: str) -> str:
    """Minusculas, sin tildes, sin puntuacion y sin palabras de relleno."""
    if texto is None:
        return ""
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.lower()
    # quitar puntuacion basica
    for ch in ".,;:()[]\"'/\\-":
        t = t.replace(ch, " ")
    # palabras de relleno que no aportan a la identificacion
    relleno = {
        "liceo", "instituto", "nacional", "colegio", "de", "del", "la", "el",
        "los", "las", "y", "n", "nro", "no", "experimental", "general",
        "internado", "comercial",
    }
    palabras = [p for p in t.split() if p and p not in relleno]
    return " ".join(palabras)


def similitud(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def detectar_columnas(encabezados: list[str]) -> tuple[str, str, str]:
    """Encuentra las columnas de RBD, nombre y comuna en el Directorio.

    Los nombres exactos varian entre anios del MINEDUC; buscamos por prefijo.
    """
    h_low = {h.lower().strip(): h for h in encabezados}

    def buscar(candidatos: list[str], contiene: str | None = None) -> str | None:
        for c in candidatos:
            if c in h_low:
                return h_low[c]
        if contiene:
            for low, orig in h_low.items():
                if contiene in low:
                    return orig
        return None

    col_rbd = buscar(["rbd"], "rbd")
    col_nombre = buscar(["nom_rbd", "nombre", "nombre_establecimiento"], "nom")
    col_comuna = buscar(["nom_com_rbd", "comuna", "nombre_comuna"], "com")
    faltan = [n for n, c in [("RBD", col_rbd), ("nombre", col_nombre),
                             ("comuna", col_comuna)] if c is None]
    if faltan:
        raise SystemExit(
            f"No pude detectar columnas {faltan} en el Directorio. "
            f"Encabezados disponibles: {encabezados}"
        )
    return col_rbd, col_nombre, col_comuna


def leer_directorio(ruta: Path) -> list[dict]:
    # El MINEDUC suele entregar CSV separado por ';' y en latin-1.
    for sep, enc in [(";", "latin-1"), (",", "utf-8"), (";", "utf-8"),
                     (",", "latin-1")]:
        try:
            with ruta.open(encoding=enc, newline="") as f:
                muestra = f.read(4096)
                if sep not in muestra:
                    continue
                f.seek(0)
                filas = list(csv.DictReader(f, delimiter=sep))
                if filas and len(filas[0]) > 1:
                    print(f"[ok] Directorio leido con sep='{sep}' enc='{enc}' "
                          f"({len(filas)} filas).")
                    return filas
        except (UnicodeDecodeError, csv.Error):
            continue
    raise SystemExit(f"No pude leer el Directorio: {ruta}")


def resolver_archivo(ruta: Path) -> Path:
    """Si `ruta` es una carpeta, busca dentro el archivo del Directorio."""
    if ruta.is_file():
        return ruta
    if ruta.is_dir():
        # Preferimos CSV; buscamos de forma recursiva.
        candidatos = sorted(ruta.rglob("*.csv"))
        if not candidatos:
            otros = sorted(ruta.rglob("*.xlsx")) + sorted(ruta.rglob("*.xls"))
            if otros:
                raise SystemExit(
                    f"El Directorio vino como Excel ({otros[0].name}). "
                    "Avisa para adaptar el lector a .xlsx, o exportalo a CSV."
                )
            raise SystemExit(f"No encontre ningun .csv dentro de {ruta}")
        if len(candidatos) > 1:
            print(f"[aviso] varios CSV en la carpeta; uso el primero: "
                  f"{candidatos[0].name}")
        return candidatos[0]
    raise SystemExit(f"No existe la ruta: {ruta}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--directorio", required=True, type=Path,
                    help="Ruta al CSV del Directorio, o a la CARPETA que lo "
                         "contiene (se autodetecta el archivo).")
    ap.add_argument("--ref", type=Path, default=REF_CSV,
                    help="CSV de referencia de emblematicos.")
    args = ap.parse_args()

    if not args.directorio.exists():
        raise SystemExit(
            f"No existe el Directorio en {args.directorio}.\n"
            "Descargalo desde datosabiertos.mineduc.cl "
            "('Directorio de establecimientos') y dejalo en raw/."
        )
    archivo_dir = resolver_archivo(args.directorio)
    print(f"[ok] Usando archivo: {archivo_dir}")

    # Leer referencia.
    with args.ref.open(encoding="utf-8", newline="") as f:
        ref = list(csv.DictReader(f))
        campos = list(ref[0].keys())

    # Leer e indexar Directorio.
    dir_filas = leer_directorio(archivo_dir)
    col_rbd, col_nombre, col_comuna = detectar_columnas(list(dir_filas[0].keys()))
    # Indice por comuna normalizada para acotar la busqueda.
    indice: dict[str, list[tuple[str, str, str]]] = {}
    for fila in dir_filas:
        comuna_n = normalizar(fila.get(col_comuna, ""))
        indice.setdefault(comuna_n, []).append(
            (str(fila.get(col_rbd, "")).strip(),
             fila.get(col_nombre, ""),
             normalizar(fila.get(col_nombre, "")))
        )

    print("\n=== Verificacion de RBD ===")
    n_auto = n_revisar = n_sin = 0
    for r in ref:
        objetivo = normalizar(r["nombre"])
        comuna_n = normalizar(r["comuna"])
        candidatos = indice.get(comuna_n, [])
        mejor_score, mejor_rbd, mejor_nom = 0.0, "", ""
        for rbd, nom_orig, nom_n in candidatos:
            s = similitud(objetivo, nom_n)
            if s > mejor_score:
                mejor_score, mejor_rbd, mejor_nom = s, rbd, nom_orig

        if mejor_score >= UMBRAL_AUTO:
            estado, n_auto = "si", n_auto + 1
        elif mejor_score >= UMBRAL_REVISAR:
            estado, n_revisar = "revisar", n_revisar + 1
        else:
            estado, n_sin = "no", n_sin + 1

        # No pisar un RBD ya verificado a mano.
        if r.get("rbd_verificado") == "si" and r.get("rbd"):
            print(f"[manual] {r['nombre']:45s} -> RBD {r['rbd']} (ya verificado)")
            continue

        if estado != "no":
            r["rbd"] = mejor_rbd
            r["rbd_verificado"] = estado
            r["fuente_verificacion"] = "Directorio MINEDUC (match automatico)"
            r["notas"] = f"match='{mejor_nom}' score={mejor_score:.2f}"
        print(f"[{estado:7s}] {r['nombre']:45s} (comuna {r['comuna']}) "
              f"-> RBD {mejor_rbd or '---'}  score={mejor_score:.2f}  "
              f"dir='{mejor_nom}'")

    # Escribir resultado.
    with args.ref.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(ref)

    print(f"\nResumen: {n_auto} automaticos, {n_revisar} a revisar, "
          f"{n_sin} sin match.")
    print(f"Archivo actualizado: {args.ref}")
    if n_revisar or n_sin:
        print("Revisa a mano las filas marcadas 'revisar'/'no' antes de usarlas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
