#!/usr/bin/env python3
"""
Diagnóstico: distribución de la variable de ingreso sobre la MUESTRA COMPLETA de
postulantes inscritos (ArchivoB), por año. Sirve para ver si los tramos son
fijos en pesos (la forma cambia entre años) o deciles estables (forma constante).

Genera output/figures/fig_dist_ingreso.png (un panel por año) e imprime la tabla.

Uso:
    python scripts/07_dist_ingreso.py
"""

from __future__ import annotations

import glob
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RAW = RAIZ / "raw" / "demre_historico"
OUT = RAIZ / "output" / "figures"

ING_COLS = ("INGRESO_BRUTO_FAM", "INGRESO_PERCAPITA_GRUPO_FA")


def leer_b(anio_dir: Path) -> pd.DataFrame | None:
    cands = [f for f in glob.glob(str(anio_dir / "**" / "ArchivoB*.csv"),
                                  recursive=True) if "libro" not in f.lower()]
    if not cands:
        return None
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(cands[0], sep=";", encoding=enc, low_memory=False)
        except (UnicodeDecodeError, ValueError):
            continue
    return None


def main() -> int:
    if not RAW.exists():
        raise SystemExit(f"No existe {RAW}")
    anios = sorted(d for d in RAW.iterdir() if d.is_dir())
    datos = {}
    for d in anios:
        df = leer_b(d)
        if df is None:
            print(f"[{d.name}] sin ArchivoB"); continue
        col = next((c for c in ING_COLS if c in df.columns), None)
        if col is None:
            print(f"[{d.name}] sin columna de ingreso"); continue
        vc = (df[col].value_counts(dropna=False).sort_index()
              / len(df) * 100).round(2)
        datos[d.name] = (col, vc)
        print(f"\n### {d.name} | {col} | n={len(df):,}")
        print(vc.to_string())

    if not datos:
        raise SystemExit("No hay datos de ingreso para graficar.")

    OUT.mkdir(parents=True, exist_ok=True)
    n = len(datos)
    cols = 2
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(11, 4 * rows), squeeze=False)
    for ax, (anio, (col, vc)) in zip(axes.flat, datos.items()):
        # excluir 99 (no informa) del gráfico para ver bien la forma
        vc_plot = vc[[i for i in vc.index if i != 99]]
        ax.bar([str(i) for i in vc_plot.index], vc_plot.values, color="#4c72b0")
        ax.set_title(f"{anio} — {col}")
        ax.set_xlabel("Tramo de ingreso")
        ax.set_ylabel("% de inscritos")
        ax.grid(True, axis="y", alpha=0.3)
        if 99 in vc.index:
            ax.text(0.98, 0.95, f"99 (no informa): {vc.loc[99]:.1f}%",
                    transform=ax.transAxes, ha="right", va="top", fontsize=8,
                    color="#888")
    for ax in axes.flat[len(datos):]:
        ax.axis("off")
    fig.suptitle("Distribución del ingreso sobre la muestra completa de "
                 "postulantes inscritos, por año", y=1.0)
    fig.tight_layout()
    salida = OUT / "fig_dist_ingreso.png"
    fig.savefig(salida, dpi=150)
    plt.close(fig)
    print(f"\nGuardado: {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
