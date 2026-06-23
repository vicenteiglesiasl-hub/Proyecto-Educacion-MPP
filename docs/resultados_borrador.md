# Resultados (borrador)

> Borrador de trabajo. Cifras generadas por `scripts/05_demre_historico.py` y
> graficadas por `scripts/06_figuras.py` / `scripts/07_dist_ingreso.py`. Años
> ancla disponibles: 2009, 2014, 2019, 2025. Ver supuestos y limitaciones en
> `docs/metodologia.md`.

## 1. Acceso del 40% más vulnerable a las carreras de élite

El acceso de estudiantes del 40% más vulnerable a las cuatro carreras de élite
(Medicina, Derecho, Ingeniería Comercial e Ingeniería Civil) en las ocho
universidades de élite **aumentó de forma sostenida** en el período, pasando de
**13,7% (2009)** a **24,9% (2025)** —prácticamente el doble— con el alza más
marcada hacia el final del período (ver `output/figures/fig_vulnerable_serie.png`
y `results/serie_vulnerabilidad_total.csv`).

| Año | % del 40% más vulnerable (univ. de élite) |
|---|---|
| 2009 | 13,7% |
| 2014 | 12,7% |
| 2019 | 17,0% |
| 2025 | 24,9% |

Este patrón es consistente con la implementación de políticas de inclusión y de
gratuidad (a partir de 2016) y con programas de acceso como el PACE.

### 1.1. Heterogeneidad entre grupos de universidades

El aumento ocurre en los tres grupos, **pero la jerarquía se mantiene
inalterada**: las nuevas universidades privadas de élite son sistemáticamente
las más cerradas socioeconómicamente, y las regionales las más diversas
(`results/serie_vulnerabilidad_por_grupo.csv`).

| Año | Tradicionales | Nuevas | Regionales |
|---|---|---|---|
| 2009 | 6,3% | s/d | 18,4% |
| 2014 | 9,1% | 3,8% | 21,0% |
| 2019 | 11,6% | 4,7% | 28,0% |
| 2025 | 16,7% | 8,5% | 34,3% |

(Las nuevas universidades de élite ingresaron al sistema centralizado de
admisión desde ~2013; por eso no hay dato para 2009.)

## 2. Composición por dependencia del colegio de egreso

Entre quienes acceden a carreras de élite en universidades de élite, el colegio
**particular pagado** sigue siendo el origen dominante, aunque su peso
**disminuyó** (52,7% en 2014 a 46,7% en 2025), con un alza leve del sector
público (`results/dependencia_por_anio.csv`,
`output/figures/fig_dependencia.png`).

| Año | Pagado | Subvencionado | Público |
|---|---|---|---|
| 2009 | 43,3% | 37,7% | 19,0% |
| 2014 | 52,7% | 34,6% | 12,7% |
| 2019 | 52,5% | 34,5% | 13,0% |
| 2025 | 46,7% | 38,8% | 14,5% |

## 3. El rol de los liceos emblemáticos

Hallazgo doble (`results/emblematicos_por_anio.csv`,
`results/emblematicos_vulnerabilidad.csv`, `output/figures/fig_emblematicos.png`):

1. **Declive como vía de acceso.** La proporción de entrantes a carreras de
   élite egresados de liceos emblemáticos **se redujo a menos de la mitad**:
   4,25% (2014) → 3,18% (2019) → 1,88% (2025).
2. **Mayor focalización en los vulnerables.** Entre los que sí acceden desde
   emblemáticos, la proporción del 40% más vulnerable **subió fuertemente**:
   23,5% (2014) → 24,9% (2019) → 41,3% (2025).

Es decir, los liceos emblemáticos pasaron de ser un canal más amplio a uno más
estrecho pero socialmente más vulnerable, coherente con su declive tras el fin de
la selección y la Ley de Inclusión. (Sin dato para 2009: el DEMRE de ese año no
registra el RBD del colegio de egreso.)

## 4. Validación

La estimación de 2025 obtenida con la base DEMRE (27,5% sin ponderar / 24,9% con
bottom-40% fraccional) coincide con la obtenida de forma independiente cruzando
SIES + DEMRE (28,2%; `scripts/04_cruce_elite.py`), lo que respalda la
construcción del indicador.

## 5. Limitaciones principales

Ver `docs/metodologia.md` §2.1. En síntesis: denominador truncado (postulantes
PSU/PAES, no toda la cohorte escolar); cambio en la variable de ingreso entre
PSU (tramos nominales fijos de ingreso familiar) y PAES (deciles nacionales per
cápita), por lo que la comparación más limpia es 2009→2019; ~27% de no respuesta
de ingreso en 2025; emblemáticos no disponibles en 2009; y nuevas universidades
ausentes del sistema centralizado en 2009.
