#!/usr/bin/env python3
"""
Análisis POR CARRERA de élite a partir de processed/serie_demre.csv (salida del
script 05). Desagrega los indicadores principales por cada una de las cuatro
carreras de élite (Derecho, Ingeniería Civil, Ingeniería Comercial, Medicina).

Produce, por año y carrera:
  1. % del 40% más vulnerable (peso_vuln40, ponderado) -> output/tables/
       carrera_vulnerabilidad.csv  (años en filas, carreras en columnas)
  2. Composición por dependencia del colegio de egreso (% público) ->
       carrera_dependencia_publico.csv
  3. % de entrantes desde liceos emblemáticos ->
       carrera_emblematicos.csv
  4. n de entrantes por carrera ->
       carrera_n.csv

Y una figura: output/figures/fig_carreras.png (serie de %vuln40 por carrera).

Las tablas se imprimen en consola para copiarlas a results/ (la copia versionada
se mantiene a mano, igual que con el script 05).

Uso:
    python scripts/08_por_carrera.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SERIE = RAIZ / "processed" / "serie_demre.csv"
OUT_TAB = RAIZ / "output" / "tables"
OUT_FIG = RAIZ / "output" / "figures"

CARRERAS = ["Derecho", "Ingeniería Civil", "Ingeniería Comercial", "Medicina"]
COLORES = {
    "Derecho": "#1f77b4",
    "Ingeniería Civil": "#ff7f0e",
    "Ingeniería Comercial": "#2ca02c",
    "Medicina": "#d62728",
}


def cargar() -> pd.DataFrame:
    if not SERIE.exists():
        raise SystemExit(
            f"No existe {SERIE}. Corre antes scripts/05_demre_historico.py")
    df = pd.read_csv(SERIE, low_memory=False)
    # Solo entrantes a carreras de elite en universidades de elite.
    df = df[df["grupo_univ_elite"].notna() & df["carrera_elite"].notna()].copy()
    return df


def tabla_vulnerabilidad(df: pd.DataFrame) -> pd.DataFrame:
    base = df[df["ingreso_valido"] == True]  # noqa: E712
    col = "peso_vuln40" if "peso_vuln40" in base.columns else "vulnerable40"
    t = (base.groupby(["anio", "carrera_elite"])[col].mean()
         .mul(100).unstack().round(1))
    return t[[c for c in CARRERAS if c in t.columns]]


def tabla_n(df: pd.DataFrame) -> pd.DataFrame:
    t = (df.groupby(["anio", "carrera_elite"]).size()
         .unstack(fill_value=0))
    return t[[c for c in CARRERAS if c in t.columns]]


def tabla_publico(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["dependencia"] != "sin dato"].copy()
    d["es_publico"] = (d["dependencia"] == "Público")
    t = (d.groupby(["anio", "carrera_elite"])["es_publico"].mean()
         .mul(100).unstack().round(1))
    return t[[c for c in CARRERAS if c in t.columns]]


def tabla_emblematicos(df: pd.DataFrame) -> pd.DataFrame:
    de = df[df["emblematico"].notna()].copy()
    de["emblematico"] = de["emblematico"].astype(bool)
    t = (de.groupby(["anio", "carrera_elite"])["emblematico"].mean()
         .mul(100).unstack().round(2))
    return t[[c for c in CARRERAS if c in t.columns]]


def figura(vuln: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for c in CARRERAS:
        if c in vuln.columns:
            ax.plot(vuln.index, vuln[c], "o-", color=COLORES[c], label=c)
    ax.set_title("Acceso del 40% más vulnerable por carrera de élite\n"
                 "(universidades de élite)")
    ax.set_xlabel("Año de admisión")
    ax.set_ylabel("% del 40% más vulnerable")
    ax.set_xticks(sorted(vuln.index))
    ax.grid(True, alpha=0.3)
    ax.legend()
    nota = ("Nota: ingreso bruto familiar (PSU 2006–2020) vs per cápita "
            "(PDT/PAES 2021–2025); la comparación válida es intra-régimen.")
    fig.subplots_adjust(bottom=0.18)
    fig.text(0.01, 0.01, nota, fontsize=7, color="#555555")
    fig.savefig(OUT_FIG / "fig_carreras.png", dpi=150)
    plt.close(fig)


def main() -> int:
    OUT_TAB.mkdir(parents=True, exist_ok=True)
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    df = cargar()

    vuln = tabla_vulnerabilidad(df)
    n = tabla_n(df)
    pub = tabla_publico(df)
    emb = tabla_emblematicos(df)

    vuln.to_csv(OUT_TAB / "carrera_vulnerabilidad.csv")
    n.to_csv(OUT_TAB / "carrera_n.csv")
    pub.to_csv(OUT_TAB / "carrera_dependencia_publico.csv")
    emb.to_csv(OUT_TAB / "carrera_emblematicos.csv")

    print("=== % del 40% más vulnerable por carrera (univ. de elite) ===")
    print(vuln.to_string())
    print("\n=== n de entrantes por carrera ===")
    print(n.to_string())
    print("\n=== % desde colegio PÚBLICO por carrera ===")
    print(pub.to_string())
    print("\n=== % desde liceos emblemáticos por carrera ===")
    print(emb.to_string())

    figura(vuln)
    print(f"\nTablas en {OUT_TAB}/ ; figura fig_carreras.png en {OUT_FIG}/")
    print("(Copia las tablas a results/ a mano, como con el script 05.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
