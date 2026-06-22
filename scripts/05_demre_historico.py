#!/usr/bin/env python3
"""
Pipeline histórico DEMRE: procesa los procesos de admisión antiguos (formato
PSU/PDT, "Archivo B" + "Archivo Matrícula" + "Oferta académica"), 100% dentro
del DEMRE, sin SIES ni MRUN (la llave es ID_aux).

Por cada carpeta raw/demre_historico/<anio>/ espera encontrar:
  - ArchivoB*.csv          (Inscripción: ID_aux, RBD, GRUPO_DEPENDENCIA,
                            INGRESO_BRUTO_FAM, ...)
  - ArchivoMat*.csv        (Matrícula: ID_aux, CODIGO_UNIV, CODIGO)
  - Oferta*Académica*.xlsx (CODIGO_UNIV, UNIVERSIDAD, CODIGO, CARRERA)

Produce:
  processed/serie_demre.csv  (una fila por matriculado de elite, con año,
                              carrera, universidad/grupo, dependencia,
                              emblemático y vulnerable40)
  + resumen por año impreso en consola.

Definiciones (ver docs/metodologia.md):
  - Carreras de elite: Medicina, Ingeniería Comercial, Derecho, Ingeniería Civil.
  - 8 universidades de elite (3 grupos) de Valenzuela.
  - 40% más vulnerable: tramos bajos de INGRESO_BRUTO_FAM hasta acumular 40%
    de la población válida (por año).
  - Dependencia histórica DEMRE: 1=Pagado, 2=Subvencionado, 3/4=Público.

Uso:
    python scripts/05_demre_historico.py
"""

from __future__ import annotations

import glob
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RAW = RAIZ / "raw" / "demre_historico"
EMBLEMATICOS = AQUI / "referencias" / "liceos_emblematicos.csv"
SALIDA = RAIZ / "processed" / "serie_demre.csv"

UMBRAL_VULN = 0.40


def _norm(t) -> str:
    s = unicodedata.normalize("NFKD", str(t or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).upper().strip()


def _limpia(t) -> str:
    """Normaliza nombre de carrera: mayúsculas, sin tildes ni puntuación,
    espacios colapsados."""
    s = unicodedata.normalize("NFKD", str(t or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).upper()
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def clasificar_elite(carrera: str) -> str | None:
    """Clasifica el nombre de carrera del DEMRE en una de las 4 de elite.

    Ingeniería Civil incluye todas las que dicen 'civil' (menos Construcción
    Civil) y el 'plan común' de ingeniería de las universidades de elite, que
    es la vía a Ing. Civil aunque no diga 'civil' en el nombre.
    """
    c = _limpia(carrera)
    if not c:
        return None
    if "VETERINARIA" in c:                 # excluir Medicina Veterinaria
        return None
    if c.startswith("CONSTRUCCION"):       # excluir Construcción Civil
        return None
    if c.startswith("TECNOLOGIA"):         # excluir Tecnología Médica, etc.
        return None
    if c.startswith("MEDICINA"):
        return "Medicina"
    if c.startswith("DERECHO"):
        return "Derecho"
    if "INGENIERIA COMERCIAL" in c:
        return "Ingeniería Comercial"
    if "CIVIL" in c:
        return "Ingeniería Civil"
    # Plan común / licenciatura de ingeniería de elite que no dice "civil"
    # (p. ej. "INGENIERIA Y CIENCIAS PLAN COMUN" UCh, "INGENIERIA" UC):
    if "CIENCIAS DE LA INGENIERIA" in c:
        return "Ingeniería Civil"
    if c == "INGENIERIA":
        return "Ingeniería Civil"
    if "INGENIERIA" in c and "PLAN COMUN" in c and "QUIMICA" not in c:
        return "Ingeniería Civil"
    return None


def grupo_univ_elite(universidad: str) -> str | None:
    n = _norm(universidad)
    if n == "UNIVERSIDAD DE CHILE" or "CATOLICA DE CHILE" in n:
        return "tradicional"
    if "DE LOS ANDES" in n or "ADOLFO IBANEZ" in n or "DEL DESARROLLO" in n:
        return "nueva"
    if ("FEDERICO SANTA MARIA" in n or "DE CONCEPCION" in n
            or "CATOLICA DE VALPARAISO" in n):
        return "regional"
    return None


def clasificar_dependencia(cod) -> str:
    # Código histórico DEMRE: 1=Pagado, 2=Subvencionado, 3/4=Público (Municipal).
    m = {1: "Particular Pagado", 2: "Particular Subvencionado",
         3: "Público", 4: "Público"}
    try:
        return m.get(int(cod), "sin dato")
    except (ValueError, TypeError):
        return "sin dato"


def leer_csv(ruta: str, cols=None) -> pd.DataFrame:
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(ruta, sep=";", encoding=enc, usecols=cols,
                               low_memory=False)
        except (UnicodeDecodeError, ValueError):
            continue
    raise SystemExit(f"No pude leer {ruta}")


def _buscar(anio_dir: Path, patron: str) -> str | None:
    h = [f for f in glob.glob(str(anio_dir / "**" / "*"), recursive=True)
         if patron.lower() in Path(f).name.lower() and f.lower().endswith(
             (".csv", ".xlsx", ".xls"))]
    return h[0] if h else None


def procesar_anio(anio_dir: Path, rbds_emb: set) -> pd.DataFrame | None:
    anio = anio_dir.name
    fb = _buscar(anio_dir, "ArchivoB")
    fm = _buscar(anio_dir, "ArchivoMat") or _buscar(anio_dir, "Matricula")
    fo = _buscar(anio_dir, "Oferta")
    faltan = [n for n, f in [("ArchivoB", fb), ("Matrícula", fm),
                             ("Oferta", fo)] if not f]
    if faltan:
        print(f"[{anio}] faltan archivos: {faltan} -> se omite")
        return None

    insc = leer_csv(fb)
    insc.columns = [c.strip() for c in insc.columns]
    mat = leer_csv(fm)
    mat.columns = [c.strip() for c in mat.columns]
    oferta = pd.read_excel(fo)
    oferta.columns = [c.strip() for c in oferta.columns]
    oferta = oferta[["CODIGO_UNIV", "CODIGO", "UNIVERSIDAD", "CARRERA"]].drop_duplicates(
        ["CODIGO_UNIV", "CODIGO"])

    # Matrícula -> nombres (universidad/carrera).
    df = mat.merge(oferta, on=["CODIGO_UNIV", "CODIGO"], how="left")
    df["carrera_elite"] = df["CARRERA"].map(clasificar_elite)
    df["grupo_univ_elite"] = df["UNIVERSIDAD"].map(grupo_univ_elite)

    # Autodiagnóstico: en las universidades de elite, ¿qué quedó sin clasificar?
    eli_all = df[df["grupo_univ_elite"].notna()]
    sin = eli_all[eli_all["carrera_elite"].isna()]
    print(f"[{anio}] univ. elite: {len(eli_all):,} matriculados, "
          f"{eli_all['carrera_elite'].notna().sum():,} en carreras de elite, "
          f"{len(sin):,} sin clasificar")
    if len(sin):
        top = sin["CARRERA"].value_counts().head(6)
        print(f"        top carreras NO-elite/ignoradas: "
              f"{dict(top)}")

    df = df[df["carrera_elite"].notna()].copy()

    # + datos socioeconómicos / colegio (por ID_aux).
    cols_b = ["ID_aux", "RBD", "GRUPO_DEPENDENCIA", "INGRESO_BRUTO_FAM"]
    insc_b = insc[[c for c in cols_b if c in insc.columns]].copy()
    df = df.merge(insc_b, on="ID_aux", how="left")

    df["anio"] = int(anio)
    df["dependencia"] = df["GRUPO_DEPENDENCIA"].map(clasificar_dependencia)
    df["rbd"] = pd.to_numeric(df.get("RBD"), errors="coerce")
    df["emblematico"] = df["rbd"].isin(rbds_emb)

    # vulnerable40: tramos bajos de ingreso hasta acumular el umbral (por año).
    ing = pd.to_numeric(df["INGRESO_BRUTO_FAM"], errors="coerce")
    valido = ing.notna()
    df["ingreso_valido"] = valido
    if valido.any():
        conteo = ing[valido].value_counts().sort_index()
        acum = (conteo / conteo.sum()).cumsum()
        corte = float(acum[acum >= UMBRAL_VULN].index.min())
        df["vulnerable40"] = valido & (ing <= corte)
        cob = float(acum.loc[corte])
        print(f"[{anio}] corte 40% en tramo <= {corte:.0f} "
              f"(cobertura {cob:.1%})")
    else:
        df["vulnerable40"] = False

    print(f"[{anio}] {len(df):,} matriculados de elite | "
          f"en univ. de elite: {df['grupo_univ_elite'].notna().sum():,}")
    return df


def main() -> int:
    if not RAW.exists():
        raise SystemExit(f"No existe {RAW}. Crea raw/demre_historico/<anio>/ "
                         "con los archivos DEMRE.")
    emb = pd.read_csv(EMBLEMATICOS)
    rbds_emb = set(pd.to_numeric(emb["rbd"], errors="coerce").dropna().astype(int))

    anios = sorted([d for d in RAW.iterdir() if d.is_dir()])
    if not anios:
        raise SystemExit(f"No hay carpetas de año en {RAW}")

    partes = [p for p in (procesar_anio(d, rbds_emb) for d in anios) if p is not None]
    if not partes:
        raise SystemExit("No se pudo procesar ningún año.")
    serie = pd.concat(partes, ignore_index=True)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    cols_out = ["anio", "ID_aux", "carrera_elite", "UNIVERSIDAD",
                "grupo_univ_elite", "dependencia", "rbd", "emblematico",
                "INGRESO_BRUTO_FAM", "ingreso_valido", "vulnerable40"]
    serie[[c for c in cols_out if c in serie.columns]].to_csv(
        SALIDA, index=False, encoding="utf-8")

    # --- Verificación: qué carreras/universidades se detectaron ---
    print("\n=== Carreras detectadas (CARRERA -> categoría de elite) ===")
    print(serie.groupby(["carrera_elite"])["UNIVERSIDAD"].size().to_string())
    print("\n=== Universidades de elite detectadas ===")
    print(serie[serie["grupo_univ_elite"].notna()]
          .groupby(["grupo_univ_elite", "UNIVERSIDAD"]).size().to_string())

    # --- Serie: % del 40% vulnerable por año (solo universidades de elite) ---
    eli = serie[serie["grupo_univ_elite"].notna() & serie["ingreso_valido"]]
    print("\n=== SERIE: % del 40% más vulnerable en universidades de ELITE ===")
    t = eli.groupby("anio").agg(n=("ID_aux", "size"),
                                vuln=("vulnerable40", "sum"))
    t["%_vuln40"] = (100 * t["vuln"] / t["n"]).round(1)
    print(t.to_string())

    print("\n=== % vulnerable por grupo de universidad y año ===")
    g = (eli.groupby(["anio", "grupo_univ_elite"])["vulnerable40"]
         .mean().mul(100).round(1).unstack())
    print(g.to_string())

    print(f"\nGuardado: {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
