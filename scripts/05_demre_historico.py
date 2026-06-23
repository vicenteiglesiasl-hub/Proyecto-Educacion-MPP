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
    # El separador y la codificación cambian entre años; probamos combinaciones
    # y nos quedamos con la que produce más de una columna.
    for sep in (";", ","):
        for enc in ("utf-8", "latin-1"):
            try:
                df = pd.read_csv(ruta, sep=sep, encoding=enc, usecols=cols,
                                 low_memory=False, on_bad_lines="skip")
                if df.shape[1] > 1:
                    return df
            except (UnicodeDecodeError, ValueError):
                continue
    raise SystemExit(f"No pude leer {ruta}")


def _buscar(anio_dir: Path, patron: str) -> str | None:
    h = [f for f in glob.glob(str(anio_dir / "**" / "*"), recursive=True)
         if patron.lower() in Path(f).name.lower()
         and f.lower().endswith((".csv", ".xlsx", ".xls"))
         and "libro" not in Path(f).name.lower()]   # ignorar diccionarios
    # Para datos preferimos .csv; la Oferta solo viene en .xlsx.
    csvs = [f for f in h if f.lower().endswith(".csv")]
    cand = csvs or h
    return cand[0] if cand else None


def estandariza_oferta(of: pd.DataFrame):
    """Devuelve la oferta con columnas estándar (CODIGO_UNIV, CODIGO,
    UNIVERSIDAD, CARRERA) y las llaves de cruce, manejando las variantes de
    nombres entre años (PSU/PAES). Si no puede mapear, devuelve (None, None)."""
    of = of.rename(columns=lambda c: str(c).strip())
    up = {c.upper(): c for c in of.columns}

    def buscar(cands):
        for k in cands:
            if k in up:
                return up[k]
        return None

    mapa = {
        "CODIGO_UNIV": buscar(["CODIGO_UNIV", "UNI_CODIGO", "COD_UNIV",
                               "CODIGO_UNIVERSIDAD", "COD_UNIVERSIDAD"]),
        "CODIGO": buscar(["CODIGO", "CODIGO_CARRERA", "COD_CARRERA"]),
        "UNIVERSIDAD": buscar(["UNIVERSIDAD", "NOMBRE_UNIVERSIDAD",
                               "NOM_UNIVERSIDAD"]),
        "CARRERA": buscar(["CARRERA", "NOMBRE_CARRERA", "NOM_CARRERA"]),
    }
    falta = [k for k in ("CODIGO", "UNIVERSIDAD", "CARRERA") if mapa[k] is None]
    if falta:
        print(f"   [oferta] faltan {falta}. Columnas disponibles: "
              f"{list(of.columns)}")
        return None, None
    cols = {v: k for k, v in mapa.items() if v is not None}
    out = of[list(cols)].rename(columns=cols)
    keys = ["CODIGO_UNIV", "CODIGO"] if "CODIGO_UNIV" in out.columns else ["CODIGO"]
    return out.drop_duplicates(keys), keys


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
    oferta, keys = estandariza_oferta(pd.read_excel(fo))
    if oferta is None:
        print(f"[{anio}] no pude estandarizar la Oferta -> se omite")
        return None

    # Matrícula -> nombres (universidad/carrera).
    df = mat.merge(oferta, on=keys, how="left")
    sin_of = df["UNIVERSIDAD"].isna().sum()
    if sin_of:
        print(f"[{anio}] aviso: {sin_of:,} matriculados sin match en Oferta "
              f"(llaves={keys})")
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

    # Columna de ingreso (cambia entre años: PSU INGRESO_BRUTO_FAM;
    # PAES INGRESO_PERCAPITA_GRUPO_FA).
    col_ing = next((c for c in ("INGRESO_BRUTO_FAM",
                                "INGRESO_PERCAPITA_GRUPO_FA")
                    if c in insc.columns), None)
    if col_ing is None:
        print(f"[{anio}] sin columna de ingreso reconocible -> se omite")
        return None

    # CORTE del 40% más vulnerable: se define sobre TODA la población de
    # postulantes inscritos (no sobre los matriculados de elite). Como los
    # tramos de ingreso son gruesos y cambian entre años, se usa un "bottom 40%"
    # FRACCIONAL: tramos completos bajo el 40% + el tramo frontera ponderado
    # hasta completar 40% exacto -> definición idéntica y comparable cada año.
    # 99 = "no informa" -> faltante.
    ing_all = pd.to_numeric(insc[col_ing], errors="coerce")
    val_all = ing_all.notna() & (ing_all != 99)
    shares = ing_all[val_all].value_counts().sort_index() / int(val_all.sum())
    cum = shares.cumsum()
    k = float(cum[cum >= UMBRAL_VULN].index.min())     # tramo frontera
    cum_prev = float(cum[cum.index < k].max()) if (cum.index < k).any() else 0.0
    w = (UMBRAL_VULN - cum_prev) / float(shares.loc[k])  # peso del frontera 0..1
    print(f"[{anio}] 40% vulnerable: tramos < {k:.0f} completos + tramo {k:.0f} "
          f"al {w:.0%} ({col_ing}, {int(val_all.sum()):,} inscritos)")

    # + datos socioeconómicos / colegio (por ID_aux).
    cols_b = ["ID_aux", "RBD", "GRUPO_DEPENDENCIA", col_ing]
    insc_b = insc[[c for c in cols_b if c in insc.columns]].copy()
    insc_b = insc_b.rename(columns={col_ing: "ingreso_tramo"})
    df = df.merge(insc_b, on="ID_aux", how="left")

    df["anio"] = int(anio)
    df["fuente_ingreso"] = col_ing
    df["dependencia"] = df["GRUPO_DEPENDENCIA"].map(clasificar_dependencia)
    if "RBD" in df.columns:
        df["rbd"] = pd.to_numeric(df["RBD"], errors="coerce")
        df["emblematico"] = df["rbd"].isin(rbds_emb)
    else:
        # Años antiguos (p. ej. 2009) no traen RBD del colegio de egreso.
        print(f"[{anio}] sin columna RBD -> emblemáticos no disponibles")
        df["rbd"] = pd.NA
        df["emblematico"] = pd.NA

    # Aplicar el corte (definido sobre todos los inscritos) a los matriculados.
    # peso_vuln40: 1 si el tramo está bajo la frontera, w si es el frontera, 0 si
    # está sobre. Su promedio = % comparable del 40% más vulnerable.
    ing = pd.to_numeric(df["ingreso_tramo"], errors="coerce")
    valido = ing.notna() & (ing != 99)
    df["ingreso_valido"] = valido

    def _peso(t):
        if pd.isna(t):
            return None
        if t < k:
            return 1.0
        if t == k:
            return w
        return 0.0
    df["peso_vuln40"] = ing.map(_peso)
    df["vulnerable40"] = valido & (ing < k)   # versión estricta (referencia)

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
                "fuente_ingreso", "ingreso_tramo", "ingreso_valido",
                "vulnerable40", "peso_vuln40"]
    serie[[c for c in cols_out if c in serie.columns]].to_csv(
        SALIDA, index=False, encoding="utf-8")

    # --- Verificación: qué carreras/universidades se detectaron ---
    print("\n=== Carreras detectadas (CARRERA -> categoría de elite) ===")
    print(serie.groupby(["carrera_elite"])["UNIVERSIDAD"].size().to_string())
    print("\n=== Universidades de elite detectadas ===")
    print(serie[serie["grupo_univ_elite"].notna()]
          .groupby(["grupo_univ_elite", "UNIVERSIDAD"]).size().to_string())

    # --- Serie: % del 40% vulnerable por año (solo universidades de elite) ---
    # Se usa peso_vuln40 (bottom-40% fraccional) -> comparable entre años.
    eli = serie[serie["grupo_univ_elite"].notna() & serie["ingreso_valido"]]
    print("\n=== SERIE: % del 40% más vulnerable en universidades de ELITE ===")
    t = eli.groupby("anio").agg(n=("ID_aux", "size"))
    t["%_vuln40"] = (eli.groupby("anio")["peso_vuln40"].mean() * 100).round(1)
    print(t.to_string())

    print("\n=== % vulnerable por grupo de universidad y año ===")
    g = (eli.groupby(["anio", "grupo_univ_elite"])["peso_vuln40"]
         .mean().mul(100).round(1).unstack())
    print(g.to_string())

    # --- Dependencia del colegio de egreso (univ. de elite) por año ---
    ele = serie[serie["grupo_univ_elite"].notna()]
    print("\n=== Dependencia del colegio (univ. de elite) por año (%) ===")
    dep = (ele[ele["dependencia"] != "sin dato"]
           .groupby("anio")["dependencia"]
           .value_counts(normalize=True).mul(100).round(1).unstack())
    print(dep.to_string())

    # --- Liceos emblemáticos como vía de acceso (solo años con RBD) ---
    ele_emb = ele[ele["emblematico"].notna()].copy()
    ele_emb["emblematico"] = ele_emb["emblematico"].astype(bool)
    print("\n=== Liceos emblemáticos (univ. de elite) por año ===")
    print("    (2009 omitido: el DEMRE de ese año no trae RBD del colegio)")
    emb_t = ele_emb.groupby("anio").agg(n=("ID_aux", "size"),
                                        emblematicos=("emblematico", "sum"))
    emb_t["%_emblematico"] = (100 * emb_t["emblematicos"] / emb_t["n"]).round(2)
    print(emb_t.to_string())
    print("\n=== Entrantes desde emblemáticos: ¿cuántos son del 40% vulnerable? ===")
    eb = ele_emb[ele_emb["emblematico"] & ele_emb["ingreso_valido"]]
    if len(eb):
        ebt = eb.groupby("anio").agg(n=("ID_aux", "size"))
        ebt["%_vuln40"] = (eb.groupby("anio")["peso_vuln40"].mean() * 100).round(1)
        print(ebt.to_string())

    # --- Guardar resúmenes agregados en results/ (sí se versionan en git) ---
    RESULTS = RAIZ / "results"
    RESULTS.mkdir(exist_ok=True)
    t.to_csv(RESULTS / "serie_vulnerabilidad_total.csv")
    g.to_csv(RESULTS / "serie_vulnerabilidad_por_grupo.csv")
    dep.to_csv(RESULTS / "dependencia_por_anio.csv")
    emb_t.to_csv(RESULTS / "emblematicos_por_anio.csv")
    if len(eb):
        ebt.to_csv(RESULTS / "emblematicos_vulnerabilidad.csv")
    print(f"Resúmenes (versionables) en {RESULTS}/")

    print(f"\nGuardado: {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
