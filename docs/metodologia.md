# Metodología operativa

Documento vivo que fija las definiciones operativas del proyecto. Se actualiza
a medida que avanzamos. Replica la metodología de **Valenzuela, Kuzmanic,
Villalobos & Quaresma (2023)**, *"Cambio y recomposición social en
universidades y carreras de élite en Chile (2009-2019)"* (Estudios Pedagógicos
XLIX N°3: 63-84), extendiéndola al período ~2006-2025.

---

## 1. Definición del "40% más vulnerable" (índice NSE)

### Insumos (cuestionario de padres del SIMCE 2° medio)
Por estudiante, ligados vía `MRUN`:
- Escolaridad de la **madre**.
- Escolaridad del **padre**.
- **Ingreso bruto del hogar** (capturado en *tramos*).

### Construcción del índice NSE
1. Las tres variables alimentan un **análisis factorial** (primer factor /
   primer componente principal). El **puntaje factorial** de cada estudiante
   es el índice NSE continuo.
2. El ingreso viene en tramos → se convierte a escala numérica (marca de clase
   del tramo). Parametrizable.

### Deciles sobre población NO truncada (punto crítico)
Los deciles del índice NSE se calculan sobre **todos** los que rindieron SIMCE
2° medio en la cohorte, **no** sobre los que luego se matriculan en educación
superior (esa población está autoseleccionada). Orden obligatorio del pipeline:

1. Construir NSE para **toda** la cohorte SIMCE.
2. Asignar **decil** dentro de la cohorte.
3. *Recién entonces* cruzar con SIES y filtrar a quienes entran a carreras de élite.

### Corte
- **40% más vulnerable = deciles D1–D4.**
- Parámetro `corte` configurable (permite reproducir también el 50% = D1–D5 que
  usa el paper original, para comparar).

### Deciles por cohorte
Cada año de SIMCE 2° medio tiene su **propia** distribución y sus propios
deciles. Se mide *posición relativa* (movilidad), no nivel absoluto. No se
agrupan años (evita mezclar inflación de ingresos y expansión educativa
2006–2025).

### Enlace temporal de cohortes
SIMCE 2° medio año *t* ↔ matrícula 1er año educación superior año *t+3*, solo
**matrícula inmediata** (transición continua). Ej.: 2° medio 2006 → ES 2009.

### Tratamiento de faltantes
A decidir tras medir el % de no-respuesta en ingreso/escolaridad por año.
Opciones en evaluación: casos completos / imputación / exclusión.

---

## 2.0. Fuente para el NSE y el enlace (DECISIÓN ADOPTADA)

**Se usa la base DEMRE "Acceso a la educación superior", NO el SIMCE.**

Motivo: el enlace SIMCE↔SIES exige el identificador individual **MRUN**, que en
el SIMCE solo está en las bases **restringidas** (solicitud por Ley de
Transparencia, plazos de semanas). La base **DEMRE** es de acceso público, trae
**MRUN**, el **establecimiento de egreso** (RBD → dependencia y emblemáticos) e
**información socioeconómica** (ingreso/educación de los padres), y enlaza con
SIES por MRUN. Permite avanzar de inmediato.

**Limitación a declarar en el paper (importante):** el DEMRE solo cubre a
quienes rinden la PSU/PAES, es decir, una población **autoseleccionada
(truncada)**. Por lo tanto, el "40% más vulnerable" se define **entre los
postulantes a la educación superior**, no sobre toda la cohorte escolar (como sí
hace Valenzuela con SIMCE). Esto constituye una **extensión/variante documentada
de la metodología original**, no una réplica exacta.

> Pendiente opcional: si más adelante se obtiene el SIMCE con MRUN, se puede
> rehacer el 40% sobre población no truncada para contrastar.

## 2. Estrategia de cobertura temporal (decisión adoptada)

Prioriza **consistencia metodológica** en el grueso del período y documenta la
extensión a años recientes como tal:

- **2006–2016:** replicar **exactamente** el NSE-SIMCE (índice factorial +
  deciles por cohorte).
- **2017–2025:** evaluar con los datos en mano si el SIMCE 2° medio alcanza
  (hay años sin aplicación —p. ej. 2020 por pandemia— y cambios de formato del
  cuestionario). Si no, **complementar** con el NSE/quintil socioeconómico del
  **DEMRE** o la condición de **prioritario (SEP)**, dejándolo explícitamente
  documentado como extensión.

### Validación del índice
Como chequeo de que el NSE está bien construido, correlacionar el decil NSE con:
- la **dependencia** del establecimiento (público / particular subvencionado /
  particular pagado), y
- el **quintil socioeconómico del DEMRE**.
Debe reproducir los patrones de composición del paper original.

---

## 2.1. Limitaciones y notas (para declarar en el paper)

1. **Nuevas universidades de élite ausentes en 2009.** La matrícula DEMRE es la
   del sistema centralizado de admisión. UANDES, UAI y UDD se incorporaron a ese
   sistema recién ~2012–2013, por lo que el grupo "nuevas" solo aparece en la
   serie desde 2014; en 2009 figura como s/d. Como las nuevas son las más
   cerradas socioeconómicamente, su ausencia en 2009 sesga el total de ese año
   levemente al alza (es decir, el alza real 2009→2025 podría ser algo mayor).
2. **Cambio en la variable de ingreso (y por qué se usa posición relativa).**
   - PSU (2009–2019): `INGRESO_BRUTO_FAM` = ingreso **bruto familiar total**,
     en **tramos fijos en pesos de ancho constante ($144.000)**: tramo 1
     $0–144.000, …, tramo 12 $1.584.001 y más. (El Libro lo rotula "deciles"
     pero NO lo son: son rangos nominales fijos.)
   - PAES (2023+): `INGRESO_PERCAPITA_GRUPO_FA` = ingreso **per cápita**, en
     **deciles nacionales** con rangos en pesos (decil 1 $0–81.150, …, decil 10
     $904.200 y más).
   Como los tramos PSU son **nominales fijos**, con inflación la gente sube de
   tramo sin cambiar su posición relativa (se ve en `fig_dist_ingreso.png`: la
   distribución de 2009 está cargada en tramos bajos y la de 2019 corrida a la
   derecha). Por eso NO se comparan tramos absolutos entre años, sino la
   **posición relativa** (bottom 40%), que es comparable. En 2025 los tramos
   sí son deciles nacionales per cápita (medida más fuerte para ese año).
   Además, la no-respuesta de ingreso (código 99) es ~27% en 2025 y casi nula en
   los años PSU: asimetría a tener presente.
3. **Emblemáticos no disponibles en 2009.** El ArchivoB de 2009 no incluye el RBD
   del colegio de egreso; la dimensión de liceos emblemáticos arranca en 2014.
4. **Denominador truncado.** El "40% más vulnerable" se define entre postulantes
   PSU/PAES, no sobre toda la cohorte escolar (ver 2.0).
5. **Bottom-40% fraccional.** Como los tramos de ingreso son gruesos y cambian
   entre años, se pondera el tramo frontera hasta completar exactamente 40%, para
   que la definición sea idéntica y comparable cada año.

## 2.2. Construcción operativa del 40% (peso fraccional)

**Definición adoptada (única) del proyecto:** el "40% más vulnerable" es el
**40% de menor ingreso de los postulantes PSU/PAES de cada año** (universo de
referencia = postulantes inscritos, no la población nacional), construido con el
peso fraccional que se describe abajo. Es una definición **relativa a los
postulantes** y por año.

La variable de ingreso viene en **tramos gruesos** (cajones), así que el límite
del 40% casi nunca cae justo en el borde de un tramo. Para definir el "40% más
vulnerable" de forma **exacta, determinista y comparable entre años** se usa un
**bottom-40% fraccional**, implementado como una columna `peso_vuln40` por
estudiante:

- Tramos **bajo** la frontera → `peso_vuln40 = 1` (cuentan entero).
- Tramo **frontera** → `peso_vuln40 = w`, donde
  `w = (0,40 − acumulado_hasta_el_tramo_anterior) / share_del_tramo_frontera`.
  **Todos** los estudiantes de ese tramo reciben el mismo `w`.
- Tramos **sobre** la frontera → `peso_vuln40 = 0`.

El indicador "% del 40% más vulnerable" es el **promedio de `peso_vuln40`** sobre
el grupo de interés. El corte (tramo frontera y `w`) se calcula sobre **toda la
población de postulantes inscritos** de cada año y se guarda en
`results/cortes_40.csv`.

**No hay asignación aleatoria.** No se sortea quién del tramo frontera "es"
vulnerable (eso metería ruido y no sería reproducible). En su lugar, cada persona
del tramo frontera aporta una fracción `w`.

*Ejemplo (2014, frontera = tramo 2 con w = 0,86):* si 100 entrantes a la élite
están en el tramo 2, no se eligen 86 al azar; a los 100 se les asigna peso 0,86,
de modo que aportan 86 al conteo de vulnerables. Al promediar sobre muchos casos,
el resultado es el % correcto.

**Supuesto.** Dentro del tramo frontera no se observa el ingreso fino, así que se
asume que el ingreso *dentro* de ese tramo no está correlacionado con acceder a la
élite (supuesto estándar para datos agrupados). Bajo ese supuesto, el estimador
agregado es insesgado.

**Robustez.** Se conserva además `vulnerable40` (binario estricto = solo tramos
bajo la frontera, sin el tramo frontera) como referencia. Para modelos a nivel
individual se recomienda usar `peso_vuln40` como ponderador, o reportar
sensibilidad incluyendo/excluyendo el tramo frontera; no se recomienda la
asignación aleatoria.

## 2.3. Extensión evaluada y NO adoptada: anclaje nacional vía CASEN

> **Decisión:** esta extensión fue evaluada y **no se adopta**. El proyecto usa
> la definición relativa a postulantes (§2.2). Se documenta aquí solo como
> alternativa para trabajo futuro. Motivo: para un "40% nacional **de cada año**"
> en los años PSU haría falta la distribución nacional por año (CASEN); se
> prefirió mantener una única definición simple y reproducible sin datos
> externos.

El 40% adoptado es relativo a los **postulantes** (denominador truncado). Para
expresarlo como "40% más vulnerable de **toda la población**" se podría anclar los
tramos a la distribución nacional usando la encuesta **CASEN**:

1. **Rangos en pesos por tramo y año.** PAES (2022, 2025) ya usa deciles
   nacionales per cápita (no requiere CASEN: el 40% nacional = deciles 1–4). Para
   los años PSU (2009–2019, `INGRESO_BRUTO_FAM` en tramos fijos de $144.000) se
   toman los rangos del Libro de Códigos.
2. **CASEN del año más cercano.** Se usa la distribución de ingreso de los
   hogares (concepto comparable: ingreso familiar total para PSU; per cápita para
   PAES), idealmente acotada a hogares con un integrante de la edad de egreso.
3. **Percentil nacional de cada tramo.** Se ubica cada borde de tramo en la
   distribución acumulada de CASEN → percentil nacional de ese corte.
4. **Redefinir el 40% sobre la escala nacional** (mismo peso fraccional, pero la
   frontera es el percentil 40 *nacional*, no el de los postulantes).

**Cuidados:** emparejar años para que los pesos nominales coincidan (evita
deflactar manualmente); homogeneizar el concepto de ingreso (familiar vs per
cápita); CASEN es muestral (usar factores de expansión); y definir la población
de referencia (todos los hogares vs hogares con jóvenes en edad de postular).
Esto resolvería la limitación del denominador truncado y haría la serie
comparable con el enfoque poblacional de Valenzuela (SIMCE).

## 3. Carreras de élite

Ingeniería Comercial, Derecho, Ingeniería Civil y Medicina.

### Operacionalización en la base SIES (columna `area_carrera_generica`)
Implementada en `scripts/02_matricula_elite.py`:

| Carrera de élite | Regla sobre `area_carrera_generica` |
|---|---|
| Medicina | exactamente `"Medicina"` (excluye `Medicina Veterinaria`) |
| Ingeniería Comercial | exactamente `"Ingeniería Comercial"` |
| Derecho | exactamente `"Derecho"` (excluye bachillerato, magister, doctorado y postítulo) |
| Ingeniería Civil | empieza con `"Ingeniería Civil"` + `"Otras Ingenierías Civiles"` (excluye `Construcción Civil` y técnicos) |

**Filtros transversales:** `nivel_global == "Pregrado"`,
`tipo_inst_1 == "Universidades"`, `nivel_carrera_1 == "Profesional Con Licenciatura"`.

**Primer año (entrante nuevo):** `anio_ing_carr_ori == cat_periodo`.

**Decisión pendiente:** "Ingeniería Civil" agrupa todas sus variantes
(Industrial incluida), lo que la infla respecto de las otras tres. Evaluar si
se restringe a una definición más estrecha. Verificación 2025: Ing. Civil
20.039, Derecho 10.129, Ing. Comercial 9.017, Medicina 3.112 entrantes.

**Nota técnica:** la base SIES viene en **UTF-8** (a diferencia del Directorio,
que es latin-1).

### Operacionalización en el DEMRE histórico (nombres crudos de carrera)
Implementada en `scripts/05_demre_historico.py` (`clasificar_elite`), sobre el
nombre `CARRERA` de la Oferta académica:

| Carrera | Regla |
|---|---|
| Medicina | empieza con "MEDICINA"; excluye "MEDICINA VETERINARIA" y "TECNOLOGIA MEDICA" |
| Derecho | empieza con "DERECHO" |
| Ingeniería Comercial | contiene "INGENIERIA COMERCIAL" |
| Ingeniería Civil | contiene "CIVIL" (excepto "CONSTRUCCION CIVIL"); **más** el plan común de ingeniería de elite que no dice "civil" (p. ej. "INGENIERIA Y CIENCIAS, PLAN COMUN" de la U. de Chile), excluyendo "QUIMICA, PLAN COMUN" |

**Decisión clave (Ing. Civil):** se incluye el "plan común de ingeniería" porque
en las universidades de elite la Ingeniería Civil se ingresa por esa vía; exigir
la palabra "civil" dejaría fuera justamente a las más selectivas (U. de Chile,
PUC).

### Unificación de fuentes (decisión)
La **serie histórica oficial** del paper se construye **100% desde el portal
DEMRE** (2004–2025, mismo formato Inscripción+Matrícula+Oferta unidos por
`ID_aux`), para garantizar criterios homogéneos entre años. El trabajo previo
con SIES/datosabiertos (2025) queda como **validación cruzada**. La matrícula
DEMRE corresponde siempre al **sistema centralizado** (misma cobertura todos los
años). El ingreso cambia de definición entre años (bruto familiar vs per cápita),
pero siempre se toma el **40% inferior dentro de cada año** (posición relativa).

---

## 3b. Universidades de elite (8, según Valenzuela)

El "elite" tiene dos dimensiones: las 4 carreras **y** las universidades. Se
replican las **8 universidades** de Valenzuela, en tres grupos:

| Grupo | Universidades |
|---|---|
| Tradicionales | U. de Chile, P. U. Católica de Chile |
| Nuevas | U. de los Andes, U. Adolfo Ibáñez*, U. del Desarrollo* |
| Regionales | U. Téc. Federico Santa María, U. de Concepción, P. U. Católica de Valparaíso |

(*De UAI y UDD se consideran **solo las sedes metropolitanas**.)

Lista en `scripts/referencias/universidades_elite.csv`; clasificación por nombre
en `scripts/02_matricula_elite.py` (`grupo_univ_elite`). Los resultados se
reportan tanto para todas las universidades como restringidos a estas 8.

## 4. Liceos emblemáticos

Listado tradicional (20 establecimientos, fuente Wikipedia confirmada
manualmente) en `scripts/referencias/liceos_emblematicos.csv`. La
identificación operativa se hace por **RBD**, verificado por código contra el
Directorio Oficial de Establecimientos del MINEDUC
(`scripts/referencias/verificar_rbd_emblematicos.py`).

---

## 5. Bases de datos requeridas (datosabiertos.mineduc.cl)

| Base | Para qué | Variables clave |
|---|---|---|
| Cuestionarios SIMCE 2° medio (padres) | índice NSE | MRUN, escolaridad padres, ingreso hogar |
| Matrícula / rendimiento SIMCE 2° medio | cohorte, RBD, dependencia | MRUN, RBD, dependencia, año |
| Directorio de Establecimientos | RBD de emblemáticos, dependencia | RBD, nombre, comuna |
| Matrícula educación superior (SIES) | carrera e institución de ingreso | MRUN, carrera, institución, año |
| Acceso a la educación superior (DEMRE) | validación NSE, quintil | MRUN, quintil/NSE, puntajes |
| Estudiantes prioritarios / SEP | fuente complementaria años recientes | MRUN, condición prioritario |
