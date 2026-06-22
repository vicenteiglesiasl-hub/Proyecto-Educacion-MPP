#!/usr/bin/env python3
"""
Construye la clasificación de vulnerabilidad socioeconómica a partir de la base
DEMRE (PAES) "Socioeconómico", y marca al "40% más vulnerable".

Contexto (ver docs/metodologia.md): se usa DEMRE en vez de SIMCE. La única
variable socioeconómica disponible en PAES es INGRESO_PERCAPITA_GRUPO_FA, que
viene en 10 tramos de ingreso (1 = menor ingreso) + código 99 = "no informa".

Como los tramos NO son deciles de población (tienen tamaños distintos), el
"40% más vulnerable" se define por la FRACCIÓN ACUMULADA de población válida:
se incluyen los tramos hasta que la acumulada alcanza el umbral (40%).

Limitaciones declaradas:
  - Población truncada: solo quienes rinden PAES (postulantes).
  - ~27% con ingreso "no informa" (99): se excluyen del cálculo y se marcan
    aparte (la no-respuesta puede no ser aleatoria).

Salida:
    processed/vulnerabilidad_demre.csv  (mrun, anio, ingreso_tramo,
                                         ingreso_valido, vulnerable40)

Uso:
    python scripts/03_nse_demre.py
    python scripts/03_nse_demre.py --umbral 0.40
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RAW = RAIZ / "raw" / "acceso_educacion_superior"
SALIDA = RAIZ / "processed" / "vulnerabilidad_demre.csv"

COD_NO_INFORMA = 99  # INGRESO_PERCAPITA_GRUPO_FA: 99 = no informa


def _buscar(patron: str) -> list[str]:
    return [f for f in glob.glob(str(RAW / "**" / "*.csv"), recursive=True)
            if patron in f.upper()]


def leer(ruta: str, cols: list[str]) -> pd.DataFrame:
    for enc in ("utf-8", "latin-1"):
        try:
            return pd.read_csv(ruta, sep=";", encoding=enc, usecols=cols,
                               low_memory=False)
        except (UnicodeDecodeError, ValueError):
            continue
    raise SystemExit(f"No pude leer {ruta}")


def chequear_direccion(socio: pd.DataFrame) -> None:
    """Confirma que tramo 1 = menor ingreso, cruzando con el puntaje PAES.

    Se usa el puntaje PAES estandarizado (PROMEDIO_CM_MAX, comprension lectora +
    matematica), que SI correlaciona con el ingreso. NO se usa el NEM, que esta
    normalizado dentro de cada colegio y no sirve para comparar entre colegios.
    """
    insc = _buscar("PUNTAJES")
    if not insc:
        print("[aviso] no encontre la base de puntajes; omito chequeo de direccion.")
        return
    cols = ["MRUN", "PROMEDIO_CM_MAX", "CLEC_MAX"]
    sc = leer(insc[0], cols)
    var = "PROMEDIO_CM_MAX" if sc["PROMEDIO_CM_MAX"].notna().any() else "CLEC_MAX"
    sc[var] = pd.to_numeric(sc[var], errors="coerce")
    sc = sc[sc[var] > 0]  # 0 = no rindio esa prueba
    m = socio.merge(sc, on="MRUN", how="inner")
    val = m[m["INGRESO_PERCAPITA_GRUPO_FA"] != COD_NO_INFORMA]
    prom = val.groupby("INGRESO_PERCAPITA_GRUPO_FA")[var].mean()
    print(f"\n-- Chequeo de direccion ({var} promedio por tramo de ingreso) --")
    print(prom.round(0).to_string())
    if prom.notna().sum() >= 2:
        creciente = prom.dropna().is_monotonic_increasing
        corr = (val[["INGRESO_PERCAPITA_GRUPO_FA", var]]
                .corr().iloc[0, 1])
        print(f"   Monotono creciente: {creciente} | correlacion tramo-puntaje: "
              f"{corr:+.2f}")
        print(f"   => {'OK: tramo 1 = menor ingreso' if corr > 0 else 'REVISAR orden'}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--umbral", type=float, default=0.40,
                    help="Fraccion acumulada para el corte (default 0.40).")
    args = ap.parse_args(argv)

    socios = _buscar("SOCIO")
    if not socios:
        raise SystemExit(f"No encontre la base socioeconomica en {RAW}")
    socio = leer(socios[0], ["MRUN", "ANYO_PROCESO", "INGRESO_PERCAPITA_GRUPO_FA"])
    socio["INGRESO_PERCAPITA_GRUPO_FA"] = pd.to_numeric(
        socio["INGRESO_PERCAPITA_GRUPO_FA"], errors="coerce")

    valido = socio["INGRESO_PERCAPITA_GRUPO_FA"].notna() & \
        (socio["INGRESO_PERCAPITA_GRUPO_FA"] != COD_NO_INFORMA)
    n_val = int(valido.sum())
    n_99 = int((~valido).sum())
    print(f"Total inscritos: {len(socio):,}")
    print(f"Con ingreso valido: {n_val:,} | sin informar (99/NaN): {n_99:,} "
          f"({n_99/len(socio):.1%})")

    # Tabla de tramos: frecuencia y acumulada sobre la poblacion VALIDA.
    conteo = (socio.loc[valido, "INGRESO_PERCAPITA_GRUPO_FA"]
              .value_counts().sort_index())
    share = conteo / n_val
    acum = share.cumsum()
    tabla = pd.DataFrame({"n": conteo, "share": share.round(3),
                          "cum_share": acum.round(3)})

    # Corte: primer tramo cuya acumulada alcanza el umbral.
    corte = int(acum[acum >= args.umbral].index.min())
    cobertura = float(acum.loc[corte])
    tabla["vulnerable40"] = tabla.index <= corte
    print(f"\n-- Tramos de ingreso (sobre poblacion valida) --")
    print(tabla.to_string())
    print(f"\nCorte 40% -> tramos 1..{corte} "
          f"(cobertura real {cobertura:.1%})")

    chequear_direccion(socio)

    # Construir salida por MRUN.
    out = socio[["MRUN", "ANYO_PROCESO"]].copy()
    out = out.rename(columns={"MRUN": "mrun", "ANYO_PROCESO": "anio"})
    out["ingreso_tramo"] = socio["INGRESO_PERCAPITA_GRUPO_FA"]
    out["ingreso_valido"] = valido.values
    out["vulnerable40"] = valido.values & \
        (socio["INGRESO_PERCAPITA_GRUPO_FA"] <= corte).values

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"\nGuardado: {SALIDA}")
    print(f"Marcados vulnerable40: {int(out['vulnerable40'].sum()):,}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
