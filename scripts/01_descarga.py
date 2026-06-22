#!/usr/bin/env python3
"""
Descarga las bases de datos del proyecto hacia raw/.

Pensado para ejecutarse en GOOGLE COLAB (internet libre). En el entorno de
desarrollo de Claude el acceso a los portales del MINEDUC está bloqueado, así
que este script no descarga ahí; solo se versiona el código.

Modos por base (definidos en scripts/fuentes.py):
  1. `urls` directas  -> descarga cada enlace (prioridad).
  2. `ckan_id`        -> autodescubre los recursos vía la API de datos.gob.cl.
  3. ninguno          -> imprime instrucciones para que pegues el enlace.

Características:
  - Descarga en streaming, con reanudación si se corta (.part).
  - Omite archivos ya descargados (idempotente).
  - Descomprime .zip automáticamente.
  - Barra de progreso si `tqdm` está instalado.

Uso:
    python scripts/01_descarga.py                 # todas las bases
    python scripts/01_descarga.py matricula_escolar directorio_establecimientos
"""

from __future__ import annotations

import json
import sys
import urllib.request
import zipfile
from pathlib import Path

# Permitir importar fuentes.py esté donde esté el cwd.
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from fuentes import FUENTES, RAW_DIR  # noqa: E402

RAIZ = AQUI.parent
DESTINO_RAW = RAIZ / RAW_DIR

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None

UA = "Mozilla/5.0 (proyecto-educacion-mpp; investigacion academica)"


def _nombre_archivo(url: str) -> str:
    nombre = url.split("?")[0].rstrip("/").split("/")[-1]
    return nombre or "descarga.bin"


def descargar(url: str, destino: Path) -> Path:
    """Descarga `url` a `destino` con reanudación y barra de progreso."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        print(f"   [skip] ya existe: {destino.name}")
        return destino

    parcial = destino.with_suffix(destino.suffix + ".part")
    ya = parcial.stat().st_size if parcial.exists() else 0

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if ya:
        req.add_header("Range", f"bytes={ya}-")
        print(f"   [resume] reanudando desde {ya/1e6:.1f} MB")

    with urllib.request.urlopen(req, timeout=120) as resp:
        total = resp.length or 0
        if total:
            total += ya
        modo = "ab" if ya else "wb"
        barra = tqdm(total=total or None, initial=ya, unit="B", unit_scale=True,
                     desc=f"   {destino.name}") if tqdm else None
        with parcial.open(modo) as f:
            while True:
                trozo = resp.read(1 << 16)
                if not trozo:
                    break
                f.write(trozo)
                if barra is not None:
                    barra.update(len(trozo))
        if barra is not None:
            barra.close()

    parcial.rename(destino)
    print(f"   [ok] {destino.name} ({destino.stat().st_size/1e6:.1f} MB)")
    return destino


def descomprimir_si_zip(archivo: Path) -> None:
    if archivo.suffix.lower() != ".zip":
        return
    carpeta = archivo.with_suffix("")
    if carpeta.exists():
        print(f"   [skip] ya descomprimido: {carpeta.name}")
        return
    print(f"   [unzip] {archivo.name} -> {carpeta.name}/")
    with zipfile.ZipFile(archivo) as z:
        z.extractall(carpeta)


def urls_desde_ckan(ckan_id: str) -> list[str]:
    """Obtiene las URLs de descarga directa de un dataset de datos.gob.cl."""
    api = f"https://datos.gob.cl/api/3/action/package_show?id={ckan_id}"
    req = urllib.request.Request(api, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except Exception as e:  # noqa: BLE001
        print(f"   [aviso] no pude consultar CKAN ({ckan_id}): {e}")
        return []
    recursos = data.get("result", {}).get("resources", [])
    urls = [r["url"] for r in recursos if r.get("url")]
    print(f"   [ckan] {len(urls)} recurso(s) encontrado(s).")
    return urls


def procesar_base(clave: str, cfg: dict) -> None:
    print(f"\n=== {clave} ===")
    print(f"    {cfg['descripcion']}")
    carpeta = DESTINO_RAW / clave

    urls = list(cfg.get("urls") or [])
    if not urls and cfg.get("ckan_id"):
        urls = urls_desde_ckan(cfg["ckan_id"])

    if not urls:
        print("   [falta] sin URLs. Abre el portal y pega los enlaces en "
              "scripts/fuentes.py (campo 'urls'):")
        print(f"           {cfg.get('portal', '(sin portal)')}")
        return

    for url in urls:
        archivo = descargar(url, carpeta / _nombre_archivo(url))
        descomprimir_si_zip(archivo)


def main(argv: list[str]) -> int:
    claves = argv or list(FUENTES.keys())
    desconocidas = [c for c in claves if c not in FUENTES]
    if desconocidas:
        raise SystemExit(f"Bases desconocidas: {desconocidas}\n"
                         f"Disponibles: {list(FUENTES.keys())}")

    print(f"Destino: {DESTINO_RAW}")
    for clave in claves:
        procesar_base(clave, FUENTES[clave])
    print("\nListo.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
