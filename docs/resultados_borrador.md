# Resultados (borrador)

> Borrador de trabajo. Cifras generadas por `scripts/05_demre_historico.py` y
> graficadas por `scripts/06_figuras.py` / `scripts/07_dist_ingreso.py`. Años
> disponibles: 2006–2025 (procesos de admisión), **excepto 2012** (su archivo de
> Oferta vino vacío). Ver supuestos y limitaciones en `docs/metodologia.md`.

## 1. Acceso del 40% más vulnerable a las carreras de élite

| Año | % del 40% más vulnerable (univ. élite) | Variable de ingreso |
|---|---|---|
| 2006 | 17,7% | bruto familiar (PSU) |
| 2007 | 15,2% | bruto familiar (PSU) |
| 2008 | 12,5% | bruto familiar (PSU) |
| 2009 | 13,7% | bruto familiar (PSU) |
| 2010 | 14,2% | bruto familiar (PSU) |
| 2011 | 15,1% | bruto familiar (PSU) |
| 2013 | 12,4% | bruto familiar (PSU) |
| 2014 | 12,7% | bruto familiar (PSU) |
| 2016 | 14,2% | bruto familiar (PSU) |
| 2019 | 17,0% | bruto familiar (PSU) |
| 2022 | 23,5% | per cápita (PDT) |
| 2025 | 24,9% | per cápita (PAES) |

**Lectura (clave, y más cauta que con pocos años).** La serie densa muestra que,
**dentro del régimen de medición comparable (2006–2019, ingreso bruto familiar),
el acceso del 40% más vulnerable es esencialmente plano y ruidoso** (oscila entre
~12% y ~17%, sin tendencia secular clara). El **gran aumento aparece sólo en
2022–2025** (23–25%), que es precisamente cuando cambia la variable de ingreso
(de bruto familiar a per cápita, en el paso PSU→PDT/PAES). Por lo tanto, **buena
parte del salto está confundida con el cambio de medición** y no puede leerse sin
más como un aumento real de la inclusión. Esta es una conclusión importante que
sólo se vuelve visible al densificar la serie.

(Nota: en 2006–2007 el corte del 40% cae casi enteramente dentro del primer tramo
de ingreso —medición especialmente gruesa en pesos de la época—, por lo que esos
dos puntos deben tomarse con cautela.)

### 1.1. Heterogeneidad entre grupos de universidades

El hallazgo **robusto y transversal** es la jerarquía, estable en todos los años:
las nuevas universidades privadas de élite son sistemáticamente las más cerradas;
las regionales, las más diversas; las tradicionales, intermedias.

| Año | Tradicionales | Nuevas | Regionales |
|---|---|---|---|
| 2006 | 8,9% | s/d | 23,4% |
| 2008 | 5,1% | s/d | 17,6% |
| 2011 | 6,8% | s/d | 20,4% |
| 2013 | 6,8% | 2,9% | 21,5% |
| 2016 | 8,6% | 3,8% | 24,4% |
| 2019 | 11,6% | 4,7% | 28,0% |
| 2022 | 15,6% | 8,7% | 32,3% |
| 2025 | 16,7% | 8,5% | 34,3% |

Dentro del régimen comparable, los grupos también muestran trayectorias planas o
levemente al alza con bastante ruido; el contraste entre grupos (nuevas ≪
tradicionales < regionales) es mucho más estable que cualquier tendencia
temporal. (Las nuevas universidades de élite ingresaron al sistema centralizado
de admisión recién ~2013; sin dato 2006–2011.)

## 2. Composición por dependencia del colegio de egreso

| Año | Pagado | Subvencionado | Público |
|---|---|---|---|
| 2006 | 44,6% | 33,5% | 21,9% |
| 2009 | 43,3% | 37,7% | 19,0% |
| 2011 | 41,5% | 39,2% | 19,3% |
| 2013 | 52,1% | 35,4% | 12,5% |
| 2016 | 51,0% | 36,0% | 13,0% |
| 2019 | 52,5% | 34,5% | 13,0% |
| 2022 | 46,4% | 39,0% | 14,6% |
| 2025 | 46,7% | 38,8% | 14,5% |

Se observa un **escalón entre 2011 y 2013** (el colegio pagado sube de ~41% a
~52% y el público baja de ~19% a ~12%) que **coincide con la incorporación de las
nuevas universidades privadas de élite al sistema centralizado** (que aparecen en
la serie justo en 2013 y reclutan mayoritariamente de colegios pagados). Es decir,
parte de este cambio refleja un cambio de **cobertura institucional**, no
necesariamente una caída real del acceso del sector público. Hacia el final
(2022–2025) el colegio pagado retrocede levemente (~47%).

## 3. El rol de los liceos emblemáticos

El resultado **más robusto** del estudio (monótono en toda la serie):

| Año | % entrantes desde emblemáticos | % del 40% vulnerable entre ellos |
|---|---|---|
| 2010 | 7,35% | 18,4% |
| 2011 | 6,92% | 21,4% |
| 2013 | 4,17% | 20,8% |
| 2014 | 4,25% | 23,5% |
| 2016 | 3,60% | 24,5% |
| 2019 | 3,18% | 24,8% |
| 2022 | 2,71% | 37,4% |
| 2025 | 1,87% | 41,6% |

1. **Declive sostenido como vía de acceso:** la proporción de entrantes a carreras
   de élite egresados de liceos emblemáticos cae de **7,35% (2010)** a **1,87%
   (2025)** —se reduce a la cuarta parte—.
2. **Mayor focalización en los vulnerables:** entre quienes sí acceden desde
   emblemáticos, la proporción del 40% más vulnerable sube de **~18–21% (2010–11)**
   a **41,6% (2025)**.

Los liceos emblemáticos pasaron de ser un canal amplio a uno mucho más estrecho
pero socialmente más vulnerable, coherente con su declive tras el fin de la
selección y la Ley de Inclusión. (Parte de la caída 2011→2013 también refleja el
aumento del denominador por la incorporación de nuevas universidades.)

## 4. Validación

La estimación de 2025 obtenida con la base DEMRE coincide con la obtenida de forma
independiente cruzando SIES + DEMRE (≈28% sin ponderar; `scripts/04_cruce_elite.py`),
lo que respalda la construcción del indicador.

## 5. Limitaciones principales

Ver `docs/metodologia.md` §2.1–2.3. En síntesis:
- **Denominador truncado** (postulantes PSU/PAES, no la cohorte escolar completa):
  el nivel depende de la composición del conjunto de postulantes, que cambia en el
  tiempo.
- **Cambio en la variable de ingreso** (bruto familiar → per cápita) en torno a
  2022: confunde el nivel; la comparación válida es intra-régimen (2006–2019).
- **Cobertura institucional**: las nuevas universidades de élite entran al sistema
  centralizado recién ~2013, lo que genera el escalón 2011→2013 en dependencia y
  emblemáticos.
- **Medición gruesa en años antiguos** (2006–2007): el 40% se define casi dentro
  de un solo tramo de ingreso.
- **Emblemáticos** no identificables antes de 2010 (sin RBD en el DEMRE).
- **2012** ausente (archivo de Oferta vacío en la fuente).
- **No respuesta de ingreso** ~27% en años PAES, excluida del cálculo.
