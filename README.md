# Acceso de estudiantes vulnerables a carreras universitarias de elite en Chile (2006–2025)

Proyecto de investigación para un paper de políticas educacionales. Analiza
cómo cambió, entre ~2006 y 2025, el acceso de estudiantes socioeconómicamente
vulnerables (el **40% más vulnerable**) a las **carreras universitarias de
elite** en Chile, y qué rol jugaron los **liceos públicos** —en particular los
**emblemáticos**— como vía de acceso.

## Objetivo

Replicar y extender la metodología de **Valenzuela, Kuzmanic, Villalobos y
Quaresma (2023)**, que cruza datos escolares (**SIMCE de 2° medio**) con la
matrícula de educación superior (**SIES**) usando el identificador individual
**MRUN**, para responder:

1. ¿Cómo evolucionó la probabilidad de acceso del 40% más vulnerable a las
   carreras de elite entre 2006 y 2025?
2. ¿Qué papel cumplieron los liceos públicos —y los emblemáticos en
   particular— como vía de movilidad hacia esas carreras?
3. ¿Cómo afectaron este patrón los cambios de política del período
   (p. ej. fin de la selección, Ley de Inclusión, gratuidad)?

### Carreras de elite consideradas

- Ingeniería Comercial
- Derecho
- Ingeniería Civil
- Medicina

## Metodología (resumen)

- **Unidad de análisis:** estudiantes individuales, enlazados mediante el
  identificador anonimizado **MRUN**.
- **Cruce principal:** SIMCE 2° medio (cohorte escolar y nivel
  socioeconómico) ↔ matrícula de educación superior SIES (carrera e
  institución de ingreso).
- **Definición de vulnerabilidad:** 40% más vulnerable, operacionalizado a
  partir de información socioeconómica (DEMRE / SEP / SIMCE; criterio a fijar
  en `scripts/`).
- **Ventana temporal:** cohortes desde ~2006 hasta 2025, según
  disponibilidad de las bases abiertas.

> El criterio exacto de vulnerabilidad, la definición operativa de "liceo
> emblemático" y las reglas de enlace MRUN se documentan en los scripts y se
> dejan explícitos para garantizar reproducibilidad.

## Fuentes de datos

Bases abiertas del MINEDUC — <https://datosabiertos.mineduc.cl>:

- **Matrícula de educación superior** (SIES)
- **Acceso a la educación superior** (puntajes e información socioeconómica del DEMRE)
- **Estudiantes prioritarios / SEP**
- **Matrícula escolar / SIMCE**

> Los datos crudos **no se versionan** en el repositorio (ver `.gitignore`);
> se redescargan desde la fuente y se colocan en `raw/`.

## Estructura del proyecto

```
.
├── raw/          # Datos crudos descargados del MINEDUC (NO versionados)
├── processed/    # Datos intermedios y finales generados por los scripts (NO versionados)
├── scripts/      # Código Python: descarga, limpieza, enlace MRUN, análisis y figuras
├── output/
│   ├── figures/  # Figuras generadas por código
│   └── tables/   # Tablas/resultados exportados
├── requirements.txt
└── README.md
```

Separación de responsabilidades:

- `raw/` es **inmutable**: nunca se edita a mano; sólo se escribe al descargar.
- `processed/` se **regenera** corriendo los scripts; es desechable.
- `output/` contiene los productos del paper (figuras y tablas), generados por código.

## Reproducibilidad

- Trabajo en **Python** sobre **Google Colab**.
- Datos crudos separados de datos procesados; figuras generadas por código.
- Scripts versionados y numerados según el flujo del pipeline.

### Flujo previsto (pipeline)

El orden de los scripts reflejará el pipeline, por ejemplo:

```
scripts/
├── 01_descarga.py        # descarga de las bases desde datosabiertos.mineduc.cl → raw/
├── 02_limpieza.py        # limpieza y estandarización por base → processed/
├── 03_enlace_mrun.py     # cruce SIMCE ↔ SIES por MRUN → processed/
├── 04_variables.py       # construcción de vulnerabilidad, elite, tipo de liceo
├── 05_analisis.py        # estadísticos y modelos
└── 06_figuras.py         # figuras y tablas → output/
```

> Esta lista es referencial; se irá completando a medida que avance el trabajo.

### Cómo empezar (en local)

```bash
pip install -r requirements.txt
```

### Cómo correr esto en Google Colab (recomendado para los datos)

El **código** vive en GitHub; los **datos** se descargan y procesan en Colab
(que tiene internet libre y máquinas gratis). El flujo es:

> escribir/versionar código aquí → `git push` a GitHub → en Colab `git pull` y ejecutar.

La forma más simple es abrir el notebook **`colab_inicio.ipynb`** en Colab y
correr sus celdas. O, manualmente, en una celda nueva:

```python
# 1. Traer el código y cambiarse a la rama de trabajo
!git clone https://github.com/vicenteiglesiasl-hub/proyecto-educacion-mpp.git
%cd proyecto-educacion-mpp
!git checkout claude/gifted-goodall-cs28te

# 2. Cada vez que retomes (para traer cambios nuevos)
!git pull origin claude/gifted-goodall-cs28te

# 3. Dependencias
!pip install -q -r requirements.txt

# 4. Descargar bases (ver scripts/fuentes.py antes)
!python scripts/01_descarga.py
```

> Nota: este repositorio se desarrolla en un entorno sin acceso a los portales
> del MINEDUC, por eso las descargas se hacen en Colab, no en el entorno de
> desarrollo.

## Referencia

Valenzuela, J. P., Kuzmanic, D., Villalobos, C., & Quaresma, M. L. (2023).
*Acceso de estudiantes vulnerables a carreras universitarias de elite en Chile.*
(Metodología base que este proyecto replica y extiende.)

## Estado

🚧 En construcción — esqueleto del proyecto montado. Aún no se descargan datos.
