# Resultados (borrador)

> Borrador de trabajo. Cifras generadas por `scripts/05_demre_historico.py` y
> graficadas por `scripts/06_figuras.py` / `scripts/07_dist_ingreso.py`. Años
> disponibles: 2009, 2011, 2014, 2016, 2019, 2022, 2025. Ver supuestos y
> limitaciones en `docs/metodologia.md`.

## 1. Acceso del 40% más vulnerable a las carreras de élite

| Año | % del 40% más vulnerable (univ. de élite) | Variable de ingreso |
|---|---|---|
| 2009 | 13,7% | bruto familiar (PSU) |
| 2011 | 15,1% | bruto familiar (PSU) |
| 2014 | 12,7% | bruto familiar (PSU) |
| 2016 | 14,2% | bruto familiar (PSU) |
| 2019 | 17,0% | bruto familiar (PSU) |
| 2022 | 23,5% | per cápita (PDT) |
| 2025 | 24,9% | per cápita (PAES) |

**Lectura con cautela (hallazgo metodológico).** El mayor salto de la serie
ocurre entre 2019 y 2022 (17,0% → 23,5%), que coincide **exactamente** con el
cambio en la variable de ingreso (de bruto familiar a per cápita, en el paso
PSU → PDT/PAES). Por lo tanto, una parte no determinada de ese salto puede ser un
**artefacto de la medición** y no inclusión real. La interpretación se hace por
**régimen de medición**:

- **2009–2019 (ingreso bruto familiar, comparable):** aumento **modesto pero
  consistente**, de ~13–14% a 17%. Es la tendencia robusta de la serie.
- **2022–2025 (per cápita, comparable entre sí):** nivel más alto y estable
  (23,5% → 24,9%).
- **El "escalón" 2019→2022 no debe leerse como efecto causal de política**, por
  estar confundido con el cambio de variable.

### 1.1. Heterogeneidad entre grupos de universidades

El alza ocurre en los tres grupos y la jerarquía se mantiene: las nuevas
universidades privadas son sistemáticamente las más cerradas; las regionales, las
más diversas (`results/serie_vulnerabilidad_por_grupo.csv`).

| Año | Tradicionales | Nuevas | Regionales |
|---|---|---|---|
| 2009 | 6,3% | s/d | 18,4% |
| 2011 | 6,8% | s/d | 20,4% |
| 2014 | 9,1% | 3,8% | 21,0% |
| 2016 | 8,6% | 3,8% | 24,4% |
| 2019 | 11,6% | 4,7% | 28,0% |
| 2022 | 15,6% | 8,7% | 32,3% |
| 2025 | 16,7% | 8,5% | 34,3% |

Dentro del régimen comparable 2009–2019, el aumento es claro en regionales
(18→28) y tradicionales (6→12), lo que **sí constituye evidencia robusta** de
mayor apertura social, independiente del cambio de medición. (Las nuevas
universidades de élite ingresaron al sistema centralizado desde ~2013; sin dato
2009–2011.)

## 2. Composición por dependencia del colegio de egreso

El colegio particular pagado sigue siendo el origen dominante en las carreras de
élite, con un peso que **baja levemente** hacia el final del período; el sector
público se mantiene en torno a 13–19% (`results/dependencia_por_anio.csv`,
`output/figures/fig_dependencia.png`).

| Año | Pagado | Subvencionado | Público |
|---|---|---|---|
| 2009 | 43,3% | 37,7% | 19,0% |
| 2011 | 41,5% | 39,2% | 19,3% |
| 2014 | 52,7% | 34,6% | 12,7% |
| 2016 | 51,0% | 36,0% | 13,0% |
| 2019 | 52,5% | 34,5% | 13,0% |
| 2022 | 46,4% | 39,0% | 14,6% |
| 2025 | 46,7% | 38,8% | 14,5% |

## 3. El rol de los liceos emblemáticos

Hallazgo doble y consistente a lo largo de toda la serie
(`results/emblematicos_por_anio.csv`, `results/emblematicos_vulnerabilidad.csv`,
`output/figures/fig_emblematicos.png`):

1. **Declive sostenido como vía de acceso.** La proporción de entrantes a
   carreras de élite egresados de liceos emblemáticos cae de **6,93% (2011)** a
   **1,88% (2025)**.
2. **Mayor focalización en los vulnerables.** Entre quienes acceden desde
   emblemáticos, la proporción del 40% más vulnerable sube de **21,3% (2011)** a
   **41,3% (2025)**.

| Año | % entrantes desde emblemáticos | % del 40% vulnerable entre ellos |
|---|---|---|
| 2011 | 6,93% | 21,3% |
| 2014 | 4,25% | 23,5% |
| 2016 | 3,60% | 24,5% |
| 2019 | 3,18% | 24,9% |
| 2022 | 2,74% | 36,9% |
| 2025 | 1,88% | 41,3% |

Los liceos emblemáticos pasaron de ser un canal amplio a uno más estrecho pero
socialmente más vulnerable, coherente con su declive tras el fin de la selección
y la Ley de Inclusión. (El declive es monótono ya dentro del régimen 2011–2019,
por lo que no depende del cambio de medición de ingreso.)

## 4. Validación

La estimación de 2025 obtenida con la base DEMRE coincide con la obtenida de
forma independiente cruzando SIES + DEMRE (≈28% sin ponderar;
`scripts/04_cruce_elite.py`), lo que respalda la construcción del indicador.

## 5. Limitaciones principales

Ver `docs/metodologia.md` §2.1. En síntesis: denominador truncado (postulantes
PSU/PAES, no toda la cohorte escolar); **cambio en la variable de ingreso**
entre PSU (tramos nominales fijos de ingreso familiar) y PDT/PAES (deciles
nacionales per cápita), que confunde el nivel a partir de 2022 —la comparación
limpia es intra-régimen—; ~27% de no respuesta de ingreso en los años PAES;
emblemáticos no disponibles en 2009; y nuevas universidades ausentes del sistema
centralizado en 2009–2011.
