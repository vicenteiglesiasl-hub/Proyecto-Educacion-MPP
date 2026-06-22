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
from pathlib import Path

# Rutas por defecto (relativas a la raiz del repo).
AQUI = Path(__file__).resolve().parent
REF_CSV = AQUI / "liceos_emblematicos.csv"

# Umbrales sobre la "cobertura" (fraccion de palabras clave del nombre objetivo
# que aparecen en el nombre del Directorio).
UMBRAL_AUTO = 1.0       # todas las palabras presentes -> "si"
UMBRAL_REVISAR = 0.5    # la mitad o mas -> "revisar" (mirar a mano)

# Palabras genericas que no ayudan a identificar el establecimiento.
# OJO: NO se incluyen "instituto"/"nacional"/"internado"/"comercial" porque
# justamente esas distinguen casos como el Instituto Nacional.
RELLENO = {
    "liceo", "colegio", "escuela", "centro", "educacional", "polivalente",
    "de", "del", "la", "el", "los", "las", "y", "n", "nro", "no", "nº",
}


def _sin_tildes(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto or ""))
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def tokens(texto: str) -> list[str]:
    """Palabras clave del nombre: sin tildes, sin puntuacion, sin relleno,
    sin numeros sueltos ni letras sueltas (codigos tipo 'A-1', 'Nº4')."""
    t = _sin_tildes(texto)
    for ch in ".,;:()[]\"'/\\-°ºª":
        t = t.replace(ch, " ")
    out = []
    for p in t.split():
        if not p or p in RELLENO or p.isdigit() or len(p) == 1:
            continue
        out.append(p)
    return out


def normalizar(texto: str) -> str:
    """Version texto-plano (para comparar comunas)."""
    return " ".join(_sin_tildes(texto).split())


def puntaje(objetivo: list[str], candidato: list[str]) -> tuple[float, int]:
    """Cobertura del nombre objetivo dentro del candidato.

    Devuelve (cobertura, penalizacion_por_palabras_extra). La cobertura es
    cuantas palabras clave del objetivo estan en el candidato; la penalizacion
    (negativa) sirve de desempate para preferir el candidato mas ajustado.
    """
    if not objetivo:
        return 0.0, 0
    cset = set(candidato)
    cubiertos = sum(1 for tk in objetivo if tk in cset)
    cobertura = cubiertos / len(objetivo)
    extra = len(set(candidato) - set(objetivo))
    return cobertura, -extra


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
    # Cada entrada: (rbd, nombre_original, tokens_nombre, comuna_normalizada).
    registros = []
    indice: dict[str, list[int]] = {}
    for fila in dir_filas:
        comuna_n = normalizar(fila.get(col_comuna, ""))
        registros.append((
            str(fila.get(col_rbd, "")).strip(),
            fila.get(col_nombre, ""),
            tokens(fila.get(col_nombre, "")),
            comuna_n,
        ))
        indice.setdefault(comuna_n, []).append(len(registros) - 1)

    def mejores(objetivo: list[str], idxs: list[int], n: int = 3):
        puntuados = []
        for i in idxs:
            rbd, nom, toks, _ = registros[i]
            cob, desempate = puntaje(objetivo, toks)
            if cob > 0:
                puntuados.append((cob, desempate, rbd, nom))
        puntuados.sort(reverse=True)
        return puntuados[:n]

    print("\n=== Verificacion de RBD ===")
    n_auto = n_revisar = n_sin = 0
    for r in ref:
        objetivo = tokens(r["nombre"])
        comuna_n = normalizar(r["comuna"])
        candidatos = mejores(objetivo, indice.get(comuna_n, []))
        ambito = "comuna"
        if not candidatos:  # respaldo: buscar en todas las comunas
            candidatos = mejores(objetivo, range(len(registros)))
            ambito = "GLOBAL"

        cob = candidatos[0][0] if candidatos else 0.0
        mejor_rbd = candidatos[0][2] if candidatos else ""
        mejor_nom = candidatos[0][3] if candidatos else ""

        if cob >= UMBRAL_AUTO and ambito == "comuna":
            estado, n_auto = "si", n_auto + 1
        elif cob >= UMBRAL_REVISAR:
            estado, n_revisar = "revisar", n_revisar + 1
        else:
            estado, n_sin = "no", n_sin + 1

        # No pisar un RBD ya verificado a mano.
        if r.get("rbd_verificado") == "si" and r.get("rbd"):
            print(f"[manual ] {r['nombre']:45s} -> RBD {r['rbd']} (ya verificado)")
            continue

        if estado != "no":
            r["rbd"] = mejor_rbd
            r["rbd_verificado"] = estado
            r["fuente_verificacion"] = f"Directorio MINEDUC (match {ambito})"
            r["notas"] = f"match='{mejor_nom}' cobertura={cob:.2f}"
        print(f"[{estado:7s}] {r['nombre']:45s} (comuna {r['comuna']}) "
              f"-> RBD {mejor_rbd or '---'}  cob={cob:.2f} [{ambito}]")
        for cob_c, _, rbd_c, nom_c in candidatos:
            print(f"            · {cob_c:.2f}  RBD {rbd_c:>6}  {nom_c}")

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
