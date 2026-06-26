# Resultados por carrera de élite (borrador)

> Desagregación por carrera de los indicadores principales. Cifras generadas por
> `scripts/08_por_carrera.py` a partir de `processed/serie_demre.csv`. Tablas
> versionadas en `results/carrera_*.csv`; figura `output/figures/fig_carreras.png`.
> Recordar que la comparación válida de niveles es **intra-régimen** (bruto
> familiar 2006–2020 vs per cápita 2021–2025); ver `docs/metodologia.md`.

## 1. Acceso del 40% más vulnerable, por carrera

| Año | Derecho | Ing. Civil | Ing. Comercial | Medicina |
|---|---|---|---|---|
| 2006 | 17,1 | 19,2 | 15,0 | 10,4 |
| 2010 | 12,4 | 14,7 | 15,8 | 9,2 |
| 2013 | 11,9 | 14,7 | 8,7 | 5,9 |
| 2016 | 12,4 | 16,8 | 10,5 | 9,3 |
| 2019 | 15,6 | 20,1 | 12,4 | 10,2 |
| 2020 | 18,4 | 19,3 | 15,4 | 10,4 |
| 2022 | 24,2 | 25,2 | 21,3 | 11,7 |
| 2025 | 22,3 | 27,2 | 21,3 | 19,1 |

**Jerarquía robusta y estable entre carreras** (se mantiene en casi todos los años):

> **Ingeniería Civil ≳ Derecho > Ingeniería Comercial ≫ Medicina**

1. **Ingeniería Civil es la carrera de élite más abierta** en toda la serie: parte
   de ~14–19% y es la que más sube en el régimen reciente (27,2% en 2025). Es una
   carrera de alto volumen (>6.000 entrantes/año) repartida en muchas sedes,
   incluidas las regionales, que son las más diversas.
2. **Medicina es, por lejos, la más cerrada y la más estable.** Se mantiene en
   ~7–10% durante casi 15 años (2008–2021) sin tendencia, muy por debajo del resto.
   El **único movimiento real** aparece al final: 11,7% (2022) → **19,1% (2025)**,
   un alza que merece atención porque ocurre dentro del mismo régimen per cápita
   (no es artefacto del cambio de variable).
3. **Derecho** es intermedia y traza la subida más “de manual”: plana en el régimen
   bruto y un salto en el per cápita (18,4% en 2020 → 24,2% en 2022).
4. **Ingeniería Comercial muestra un quiebre en 2012**: cae de ~16% (2010–11) a
   ~9% (2012–2017). No es un cambio de inclusión real, sino de **composición
   institucional**: en 2012 entran al sistema centralizado las nuevas
   universidades privadas (UAI, UDD), muy fuertes en Ing. Comercial y muy cerradas
   socialmente, lo que **más que duplica el denominador** de la carrera (n: 1.055
   en 2011 → 2.397 en 2012) y arrastra el promedio hacia abajo.

## 2. Acceso desde colegio público, por carrera (%)

| Año | Derecho | Ing. Civil | Ing. Comercial | Medicina |
|---|---|---|---|---|
| 2006 | 22,3 | 23,3 | 16,6 | 17,8 |
| 2011 | 18,5 | 19,7 | 20,1 | 14,5 |
| 2013 | 11,9 | 14,1 | 9,5 | 10,2 |
| 2019 | 12,5 | 15,1 | 9,8 | 8,4 |
| 2025 | 12,6 | 16,5 | 11,6 | 7,3 |

- El **escalón 2011→2012** (caída general del acceso público) reaparece aquí y es
  coherente con la entrada de las nuevas universidades privadas.
- **Ingeniería Civil** vuelve a ser la más permeable al sector público (~15–16% al
  final). **Medicina** es la menos permeable y, de hecho, **cae** a 7,3% en 2025,
  en contraste con su alza en el indicador del 40% vulnerable: es decir, su mayor
  apertura reciente por ingreso **no** se traduce en más egresados de colegio
  público (entran más vulnerables, pero de colegios subvencionados/particulares).

## 3. Liceos emblemáticos como vía, por carrera (%)

| Año | Derecho | Ing. Civil | Ing. Comercial | Medicina |
|---|---|---|---|---|
| 2010 | 7,98 | 7,49 | 4,92 | 10,82 |
| 2013 | 4,37 | 4,71 | 2,11 | 6,67 |
| 2016 | 3,59 | 4,45 | 1,56 | 3,72 |
| 2019 | 2,93 | 3,88 | 1,76 | 3,64 |
| 2025 | 2,48 | 1,95 | 1,15 | 2,18 |

- El **declive de los emblemáticos como vía de acceso es transversal a las cuatro
  carreras**, lo que refuerza el hallazgo agregado.
- En 2010 los emblemáticos eran **especialmente importantes para Medicina** (10,8%
  de sus entrantes de élite —la cifra más alta de toda la matriz—) y para Derecho
  (8,0%): los liceos emblemáticos eran la principal vía pública hacia las carreras
  más selectivas. Para 2025 todas convergen a ~1–2%.
- **Ingeniería Comercial** es la que históricamente menos recluta de emblemáticos,
  consistente con su perfil socioeconómico más alto.

## 4. Síntesis

- La heterogeneidad **entre carreras** es tan importante como la heterogeneidad
  entre grupos de universidades: **Medicina** concentra el cierre social y
  **Ingeniería Civil** la apertura.
- Dos artefactos de composición a tener presentes: (i) el quiebre 2011→2012 de Ing.
  Comercial y del acceso público por la entrada de las nuevas universidades; (ii)
  el escalón 2021 confundido con el cambio de variable de ingreso.
- Hallazgos que parecen **reales** (no artefactos): el declive transversal de los
  emblemáticos y el **alza reciente y específica de Medicina** en el 40% vulnerable
  (2022–2025), que conviene mirar de cerca al redactar (paso 4).
