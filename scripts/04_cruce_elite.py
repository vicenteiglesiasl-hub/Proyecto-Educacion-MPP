#!/usr/bin/env python3
"""
Cruce final: une matrícula de elite (SIES) + vulnerabilidad (DEMRE socio) +
colegio de egreso/dependencia (DEMRE puntajes) + marca de liceo emblemático,
todo por MRUN (y RBD para emblemáticos). Produce el primer set de resultados.

Entradas:
    processed/matricula_elite.csv          (02)
    processed/vulnerabilidad_demre.csv     (03)
    raw/.../*PUNTAJES*.csv                  (DEMRE: RBD, DEPENDENCIA del egreso)
    scripts/referencias/liceos_emblematicos.csv

Salidas:
    processed/cruce_elite.csv  (una fila por estudiante de carrera de elite)
    + tablas resumen impresas en consola.

Uso:
    python scripts/04_cruce_elite.py
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
PROC = RAIZ / "processed"
RAW_ACCESO = RAIZ / "raw" / "acceso_educacion_superior"
EMBLEMATICOS = AQUI / "referencias" / "liceos_emblematicos.csv"
SALIDA = PROC / "cruce_elite.csv"


def leer(ruta: str, cols=None) -> pd.DataFrame:
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(ruta, sep=";", encoding=enc, usecols=cols,
                               low_memory=False)
        except (UnicodeDecodeError, ValueError):
            continue
    raise SystemExit(f"No pude leer {ruta}")


def clasificar_dependencia(valor) -> str:
    """Mapea DEPENDENCIA (texto o código) a público / subvencionado / pagado."""
    if pd.isna(valor):
        return "sin dato"
    s = str(valor).strip().upper()
    # Si es código numérico (estándar MINEDUC/DEMRE).
    codigos = {
        "1": "Público", "2": "Público",         # corp. municipal / municipal DAEM
        "3": "Particular Subvencionado",
        "4": "Particular Pagado",
        "5": "Público",                          # corp. administración delegada
        "6": "Público",                          # servicio local (SLEP)
    }
    if s in codigos:
        return codigos[s]
    # Si es texto.
    if "PAGAD" in s:
        return "Particular Pagado"
    if "SUBVENC" in s:
        return "Particular Subvencionado"
    if any(k in s for k in ("MUNICIPAL", "SERVICIO LOCAL", "SLEP",
                            "ADMINISTRACION DELEGADA", "CORP")):
        return "Público"
    return "sin dato"


def pct(numerador, denominador) -> str:
    return f"{100*numerador/denominador:.1f}%" if denominador else "—"


def main() -> int:
    # 1. Matrícula de elite (una fila por matrícula; nos quedamos 1 por mrun+carrera).
    elite = pd.read_csv(PROC / "matricula_elite.csv", low_memory=False)
    cols_elite = ["mrun", "carrera_elite", "cat_periodo", "nomb_inst"]
    if "grupo_univ_elite" in elite.columns:
        cols_elite.append("grupo_univ_elite")
    elite = elite[cols_elite].drop_duplicates(["mrun", "carrera_elite"])
    if "grupo_univ_elite" not in elite.columns:
        elite["grupo_univ_elite"] = None
        print("[aviso] matricula_elite.csv no trae grupo_univ_elite; "
              "vuelve a correr el 02 para clasificar universidades de elite.")
    print(f"Entrantes de elite (mrun+carrera únicos): {len(elite):,}")

    # 2. Vulnerabilidad.
    vuln = pd.read_csv(PROC / "vulnerabilidad_demre.csv", low_memory=False)
    vuln = vuln[["mrun", "ingreso_tramo", "ingreso_valido", "vulnerable40"]]

    # 3. Colegio de egreso / dependencia (DEMRE puntajes).
    insc = [f for f in glob.glob(str(RAW_ACCESO / "**" / "*.csv"), recursive=True)
            if "PUNTAJES" in f.upper()]
    if not insc:
        raise SystemExit("No encontré la base DEMRE de puntajes (RBD/dependencia).")
    cole = leer(insc[0], ["MRUN", "RBD", "DEPENDENCIA"])
    cole = cole.rename(columns={"MRUN": "mrun", "RBD": "rbd",
                                "DEPENDENCIA": "dependencia_cod"})
    print("\n-- DEPENDENCIA: valores en la base DEMRE --")
    print(cole["dependencia_cod"].value_counts(dropna=False).to_string())
    cole["dependencia"] = cole["dependencia_cod"].map(clasificar_dependencia)

    # 4. Emblemáticos (RBD -> 1).
    emb = pd.read_csv(EMBLEMATICOS)
    rbds_emb = set(pd.to_numeric(emb["rbd"], errors="coerce").dropna().astype(int))

    # --- Merge por MRUN ---
    df = elite.merge(vuln, on="mrun", how="left")
    df = df.merge(cole, on="mrun", how="left")
    df["rbd"] = pd.to_numeric(df["rbd"], errors="coerce")
    df["emblematico"] = df["rbd"].isin(rbds_emb)

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False, encoding="utf-8")

    # Resultados para todas las universidades y solo las de elite (Valenzuela).
    reportar(df, emb, "TODAS las universidades")
    elite_df = df[df["grupo_univ_elite"].notna()]
    reportar(elite_df, emb, "SOLO universidades de ELITE (8 de Valenzuela)")

    # Desglose por grupo de universidad de elite.
    if len(elite_df):
        print("\n=== % del 40% más vulnerable por grupo de universidad de elite ===")
        b = elite_df[elite_df["ingreso_valido"] == True]  # noqa: E712
        g = b.groupby("grupo_univ_elite").agg(
            n=("mrun", "size"), vuln=("vulnerable40", "sum"))
        g["% vulnerable40"] = (100 * g["vuln"] / g["n"]).round(1)
        print(g.to_string())

    print(f"\nGuardado: {SALIDA}")
    return 0


def reportar(df: pd.DataFrame, emb: pd.DataFrame, etiqueta: str) -> None:
    """Imprime los tres resultados principales para un subconjunto `df`."""
    n = len(df)
    print(f"\n{'='*70}\n### {etiqueta}  (n={n:,} entrantes de elite)\n{'='*70}")
    if n == 0:
        return
    con_demre = df["dependencia_cod"].notna().sum()
    con_ingreso = (df["ingreso_valido"] == True).sum()  # noqa: E712
    print(f"  cobertura DEMRE: {pct(con_demre, n)} | "
          f"ingreso válido: {pct(con_ingreso, n)}")

    # Resultado 1: % vulnerable40 por carrera.
    base = df[df["ingreso_valido"] == True]  # noqa: E712
    print("\n  -- % del 40% más vulnerable, por carrera (base: ingreso válido) --")
    r1 = base.groupby("carrera_elite").agg(
        n_validos=("mrun", "size"), n_vuln=("vulnerable40", "sum"))
    r1["%_vuln40"] = (100 * r1["n_vuln"] / r1["n_validos"]).round(1)
    print(r1.to_string())
    print(f"  TOTAL: {pct(base['vulnerable40'].sum(), len(base))} del 40% más vulnerable")

    # Resultado 2: dependencia por carrera.
    print("\n  -- Dependencia del colegio de egreso, por carrera (%) --")
    dep = (df[df["dependencia"] != "sin dato"]
           .groupby("carrera_elite")["dependencia"]
           .value_counts(normalize=True).mul(100).round(1).unstack(fill_value=0))
    print(dep.to_string())

    # Resultado 3: emblemáticos.
    n_emb = df["emblematico"].sum()
    print(f"\n  -- Liceos emblemáticos: {n_emb:,} entrantes ({pct(n_emb, n)}) --")
    if n_emb:
        eb = df[df["emblematico"] & (df["ingreso_valido"] == True)]  # noqa: E712
        print(f"     de ellos, del 40% más vulnerable: "
              f"{pct(eb['vulnerable40'].sum(), len(eb))}")
        top = (df[df["emblematico"]].merge(emb[["rbd", "nombre"]], on="rbd",
                                           how="left")
               .groupby("nombre").size().sort_values(ascending=False).head(8))
        print(top.to_string())


if __name__ == "__main__":
    sys.exit(main())
