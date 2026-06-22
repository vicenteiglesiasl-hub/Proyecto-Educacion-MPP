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

---

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
