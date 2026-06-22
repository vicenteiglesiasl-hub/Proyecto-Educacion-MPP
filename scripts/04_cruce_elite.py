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
    elite = elite[["mrun", "carrera_elite", "cat_periodo",
                   "nomb_inst"]].drop_duplicates(["mrun", "carrera_elite"])
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

    # --- Cobertura del enlace ---
    n = len(df)
    con_demre = df["dependencia_cod"].notna().sum()
    con_ingreso = df["ingreso_valido"].fillna(False).sum()
    print(f"\n=== Cobertura del enlace (sobre {n:,} entrantes de elite) ===")
    print(f"  con registro DEMRE (colegio): {con_demre:,} ({pct(con_demre, n)})")
    print(f"  con ingreso válido:           {con_ingreso:,} ({pct(con_ingreso, n)})")

    # --- Resultado 1: % vulnerable40 por carrera (sobre ingreso válido) ---
    base = df[df["ingreso_valido"] == True]  # noqa: E712
    print("\n=== % del 40% más vulnerable, por carrera de elite ===")
    print("    (base: entrantes con ingreso válido)")
    r1 = base.groupby("carrera_elite").agg(
        n_validos=("mrun", "size"),
        n_vulnerables=("vulnerable40", "sum"))
    r1["% vulnerable40"] = (100 * r1["n_vulnerables"] / r1["n_validos"]).round(1)
    print(r1.to_string())
    tot_v = base["vulnerable40"].sum()
    print(f"  TOTAL: {pct(tot_v, len(base))} del 40% más vulnerable")

    # --- Resultado 2: dependencia del colegio por carrera ---
    print("\n=== Dependencia del colegio de egreso, por carrera (%) ===")
    dep = (df[df["dependencia"] != "sin dato"]
           .groupby("carrera_elite")["dependencia"]
           .value_counts(normalize=True).mul(100).round(1)
           .unstack(fill_value=0))
    print(dep.to_string())

    # --- Resultado 3: liceos emblemáticos ---
    print("\n=== Liceos emblemáticos ===")
    n_emb = df["emblematico"].sum()
    print(f"  Entrantes de elite egresados de un emblemático: {n_emb:,} "
          f"({pct(n_emb, n)})")
    if n_emb:
        emb_base = df[df["emblematico"] & (df["ingreso_valido"] == True)]  # noqa: E712
        print(f"  De ellos, del 40% más vulnerable: "
              f"{pct(emb_base['vulnerable40'].sum(), len(emb_base))}")
        print("  Top emblemáticos por nº de entrantes de elite:")
        top = (df[df["emblematico"]].merge(emb[["rbd", "nombre"]], on="rbd",
                                           how="left")
               .groupby("nombre").size().sort_values(ascending=False).head(10))
        print(top.to_string())

    print(f"\nGuardado: {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
