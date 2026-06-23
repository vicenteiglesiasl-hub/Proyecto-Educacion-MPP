#!/usr/bin/env python3
"""
Genera las figuras del paper a partir de processed/serie_demre.csv (salida del
script 05). Todas las figuras se guardan en output/figures/ como PNG.

Figuras:
  1. fig_vulnerable_serie.png  -> % del 40% más vulnerable en universidades de
     elite, total y por grupo (tradicional/nueva/regional), por año.
  2. fig_dependencia.png       -> composición por dependencia del colegio de
     egreso (público/subvencionado/pagado) en univ. de elite, por año.
  3. fig_emblematicos.png      -> % de entrantes de elite desde liceos
     emblemáticos y % del 40% vulnerable entre ellos, por año.

Uso:
    python scripts/06_figuras.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # backend sin pantalla (Colab/servidor)
import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SERIE = RAIZ / "processed" / "serie_demre.csv"
OUT = RAIZ / "output" / "figures"

COLORES = {"tradicional": "#1f77b4", "nueva": "#d62728", "regional": "#2ca02c"}


def cargar() -> pd.DataFrame:
    if not SERIE.exists():
        raise SystemExit(f"No existe {SERIE}. Corre antes scripts/05_demre_historico.py")
    df = pd.read_csv(SERIE, low_memory=False)
    return df[df["grupo_univ_elite"].notna()].copy()


def fig_vulnerable(df: pd.DataFrame) -> None:
    base = df[df["ingreso_valido"] == True]  # noqa: E712
    col = "peso_vuln40" if "peso_vuln40" in base.columns else "vulnerable40"
    total = (base.groupby("anio")[col].mean().mul(100))
    porgrupo = (base.groupby(["anio", "grupo_univ_elite"])[col]
                .mean().mul(100).unstack())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(total.index, total.values, "o-", color="black", lw=2.5,
            label="Total elite", zorder=5)
    for grupo in ["tradicional", "nueva", "regional"]:
        if grupo in porgrupo.columns:
            ax.plot(porgrupo.index, porgrupo[grupo], "o--",
                    color=COLORES.get(grupo), label=grupo.capitalize())
    ax.set_title("Acceso del 40% más vulnerable a carreras de élite\n"
                 "(universidades de élite, por grupo)")
    ax.set_xlabel("Año de admisión")
    ax.set_ylabel("% del 40% más vulnerable")
    ax.set_xticks(sorted(df["anio"].unique()))
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig_vulnerable_serie.png", dpi=150)
    plt.close(fig)


def fig_dependencia(df: pd.DataFrame) -> None:
    d = df[df["dependencia"] != "sin dato"]
    comp = (d.groupby("anio")["dependencia"].value_counts(normalize=True)
            .mul(100).unstack())
    orden = ["Público", "Particular Subvencionado", "Particular Pagado"]
    comp = comp[[c for c in orden if c in comp.columns]]

    fig, ax = plt.subplots(figsize=(8, 5))
    comp.plot(kind="bar", stacked=True, ax=ax,
              color=["#2ca02c", "#ff7f0e", "#7f7f7f"])
    ax.set_title("Dependencia del colegio de egreso\n"
                 "(entrantes a carreras de élite en universidades de élite)")
    ax.set_xlabel("Año de admisión")
    ax.set_ylabel("% de entrantes")
    ax.legend(title="", bbox_to_anchor=(1.0, 1.0))
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(OUT / "fig_dependencia.png", dpi=150)
    plt.close(fig)


def fig_emblematicos(df: pd.DataFrame) -> None:
    # Solo años con RBD disponible (2009 no lo trae).
    de = df[df["emblematico"].notna()].copy()
    de["emblematico"] = de["emblematico"].astype(bool)
    share = de.groupby("anio")["emblematico"].mean().mul(100)
    eb = de[de["emblematico"] & (de["ingreso_valido"] == True)]  # noqa: E712
    col = "peso_vuln40" if "peso_vuln40" in eb.columns else "vulnerable40"
    vuln = eb.groupby("anio")[col].mean().mul(100)

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(share.index, share.values, color="#9467bd", alpha=0.7,
            label="% entrantes desde emblemáticos")
    ax1.set_xlabel("Año de admisión")
    ax1.set_ylabel("% de entrantes de élite desde emblemáticos", color="#9467bd")
    ax1.set_xticks(sorted(df["anio"].unique()))
    ax2 = ax1.twinx()
    ax2.plot(vuln.index, vuln.values, "o-", color="#d62728", lw=2.5,
             label="% del 40% vulnerable (entre emblemáticos)")
    ax2.set_ylabel("% del 40% vulnerable entre ellos", color="#d62728")
    ax1.set_title("Liceos emblemáticos como vía de acceso a la élite")
    fig.tight_layout()
    fig.savefig(OUT / "fig_emblematicos.png", dpi=150)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = cargar()
    fig_vulnerable(df)
    fig_dependencia(df)
    fig_emblematicos(df)
    print(f"Figuras guardadas en {OUT}/:")
    for f in sorted(OUT.glob("*.png")):
        print("  -", f.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
