#!/usr/bin/env python3
"""
Extrae de la matrícula de educación superior (SIES) a los estudiantes de las
CUATRO carreras de elite, dejando una tabla limpia en processed/.

Carreras de elite (sobre la columna `area_carrera_generica`):
  - Medicina            -> exactamente "Medicina" (excluye Medicina Veterinaria)
  - Ingeniería Comercial-> exactamente "Ingeniería Comercial"
  - Derecho             -> exactamente "Derecho" (excluye bachillerato/magister/etc.)
  - Ingeniería Civil    -> empieza con "Ingeniería Civil" + "Otras Ingenierías
                           Civiles" (excluye Construcción Civil y técnicos)

Filtros transversales: Pregrado, Universidades, Profesional Con Licenciatura.

Lee TODOS los archivos *MRUN.csv que existan en raw/matricula_educacion_superior
(uno por año), los junta y deja:
    processed/matricula_elite.csv

Uso:
    python scripts/02_matricula_elite.py
    python scripts/02_matricula_elite.py --todos-los-anios   # no filtrar primer año
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RAW = RAIZ / "raw" / "matricula_educacion_superior"
SALIDA = RAIZ / "processed" / "matricula_elite.csv"

# Columnas que necesitamos (ahorra memoria; la base trae 52).
COLS = [
    "cat_periodo", "mrun", "anio_ing_carr_ori", "anio_ing_carr_act",
    "tipo_inst_1", "cod_inst", "nomb_inst", "cod_carrera", "nomb_carrera",
    "area_carrera_generica", "nivel_global", "nivel_carrera_1", "codigo_demre",
    "region_sede",
]


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).upper().strip()


def grupo_univ_elite(nomb_inst: str) -> str | None:
    """Clasifica la institución en uno de los 3 grupos de universidad de elite
    de Valenzuela (8 universidades), o None si no es de elite."""
    n = _norm(nomb_inst)
    if n == "UNIVERSIDAD DE CHILE" or "CATOLICA DE CHILE" in n:
        return "tradicional"                      # UCH, PUC
    if "DE LOS ANDES" in n or "ADOLFO IBANEZ" in n or "DEL DESARROLLO" in n:
        return "nueva"                            # UANDES, UAI, UDD
    if ("FEDERICO SANTA MARIA" in n or "DE CONCEPCION" in n
            or "CATOLICA DE VALPARAISO" in n):
        return "regional"                         # UTFSM, UDEC, PUCV
    return None


def es_sede_rm(region_sede) -> bool:
    """True si la sede está en la Región Metropolitana (para UAI y UDD)."""
    return "METROPOLITANA" in _norm(region_sede)


# Universidades cuyas sedes se restringen a la RM (regla de Valenzuela).
SOLO_RM = ("ADOLFO IBANEZ", "DEL DESARROLLO")


def clasificar_elite(area: str) -> str | None:
    """Mapea `area_carrera_generica` a una de las 4 carreras de elite, o None."""
    if not isinstance(area, str):
        return None
    a = area.strip()
    if a == "Medicina":
        return "Medicina"
    if a == "Ingeniería Comercial":
        return "Ingeniería Comercial"
    if a == "Derecho":
        return "Derecho"
    if a.startswith("Ingeniería Civil") or a == "Otras Ingenierías Civiles":
        return "Ingeniería Civil"
    return None


def leer_csv(ruta: Path) -> pd.DataFrame:
    """Lee un CSV del SIES probando codificaciones (suele ser UTF-8)."""
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(ruta, sep=";", encoding=enc, usecols=COLS,
                               low_memory=False)
        except (UnicodeDecodeError, ValueError):
            continue
    raise SystemExit(f"No pude leer {ruta} (codificación/columnas).")


def procesar(solo_primer_anio: bool) -> pd.DataFrame:
    archivos = sorted(RAW.rglob("*MRUN.csv"))
    if not archivos:
        raise SystemExit(
            f"No hay archivos en {RAW}. Descarga la matrícula superior "
            "(scripts/01_descarga.py) y descomprime el .rar."
        )
    partes = []
    for ruta in archivos:
        print(f"[leer] {ruta.name}")
        df = leer_csv(ruta)

        # Filtros transversales.
        df = df[
            (df["nivel_global"] == "Pregrado")
            & (df["tipo_inst_1"] == "Universidades")
            & (df["nivel_carrera_1"] == "Profesional Con Licenciatura")
        ].copy()

        # Clasificar carrera de elite.
        df["carrera_elite"] = df["area_carrera_generica"].map(clasificar_elite)
        df = df[df["carrera_elite"].notna()]

        # Clasificar universidad de elite (grupo de Valenzuela) o None.
        df["grupo_univ_elite"] = df["nomb_inst"].map(grupo_univ_elite)
        # UAI y UDD: solo sedes metropolitanas.
        n_norm = df["nomb_inst"].map(_norm)
        fuera_rm = n_norm.str.contains("|".join(SOLO_RM)) & \
            ~df["region_sede"].map(es_sede_rm)
        df.loc[fuera_rm, "grupo_univ_elite"] = None

        # Primer año: ingreso original == periodo del archivo (entrante nuevo).
        if solo_primer_anio:
            df = df[df["anio_ing_carr_ori"] == df["cat_periodo"]]

        print(f"       -> {len(df):,} matriculados en carreras de elite")
        partes.append(df)

    res = pd.concat(partes, ignore_index=True)
    # Quitar duplicados exactos (por si un año se repite).
    res = res.drop_duplicates()
    return res


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--todos-los-anios", action="store_true",
                    help="No filtrar a primer año (deja toda la matrícula).")
    ap.add_argument("--solo-univ-elite", action="store_true",
                    help="Dejar solo las 8 universidades de elite (Valenzuela).")
    args = ap.parse_args(argv)

    df = procesar(solo_primer_anio=not args.todos_los_anios)
    if args.solo_univ_elite:
        df = df[df["grupo_univ_elite"].notna()]

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False, encoding="utf-8")

    print("\n=== Resumen: matriculados de elite por año y carrera ===")
    tabla = (df.groupby(["cat_periodo", "carrera_elite"])
               .size().unstack(fill_value=0))
    print(tabla)

    print("\n=== Universidades de elite detectadas (cod_inst -> n) ===")
    eli = df[df["grupo_univ_elite"].notna()]
    ver = (eli.groupby(["grupo_univ_elite", "nomb_inst"]).size()
           .sort_values(ascending=False))
    print(ver.to_string())
    print(f"\nEn universidades de elite: {len(eli):,} de {len(df):,} "
          f"({100*len(eli)/len(df):.1f}%)")
    print(f"Total filas: {len(df):,}")
    print(f"MRUN únicos: {df['mrun'].nunique():,}")
    print(f"Guardado en: {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
