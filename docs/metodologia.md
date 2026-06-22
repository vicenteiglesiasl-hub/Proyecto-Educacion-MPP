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
