"""
Registro central de las fuentes de datos del proyecto.

Cada base apunta a:
  - `portal`:  página humana donde encontrar y verificar los archivos.
  - `ckan_id`: (opcional) identificador del dataset en datos.gob.cl, para
               autodescubrir las URLs vía su API (modo automático).
  - `urls`:    (opcional) lista de enlaces de descarga DIRECTA. Tiene prioridad
               sobre `ckan_id`. Aquí pegas tú los enlaces si el modo automático
               no encuentra el archivo.

Cómo obtener un enlace directo:
  abre la página `portal` en tu navegador → botón "Descargar"/"Download" →
  clic derecho → "Copiar dirección del enlace" → pégalo en `urls`.

NOTA: los `portal`/`ckan_id` de abajo son los puntos de partida conocidos;
algunos están marcados "verificar" porque no se pudieron comprobar desde el
entorno de desarrollo (sin acceso a esos dominios). Confírmalos al correr en
Colab y ajusta lo que haga falta.
"""

# Carpeta destino (relativa a la raíz del repo). Cada base baja a raw/<carpeta>/.
RAW_DIR = "raw"

FUENTES = {
    "matricula_educacion_superior": {
        "descripcion": "Matrícula en educación superior (SIES). MRUN, carrera, "
                       "institución, año de ingreso.",
        "portal": "https://datosabiertos.mineduc.cl/matricula-en-educacion-superior/",
        "ckan_id": None,
        "urls": [
            # Un archivo .rar por año. Agrega los años que necesites.
            "https://datosabiertos.mineduc.cl/wp-content/uploads/2025/09/Matricula-Ed-Superior-2025.rar",
        ],
    },
    "acceso_educacion_superior": {
        "descripcion": "Acceso a la educación superior (DEMRE): puntajes e "
                       "información socioeconómica (quintil/NSE). Validación.",
        "portal": "https://datosabiertos.mineduc.cl/acceso-a-la-educacion-superior/",  # verificar
        "ckan_id": None,
        "urls": [],
    },
    "matricula_escolar": {
        "descripcion": "Matrícula escolar por estudiante. MRUN, RBD, dependencia, "
                       "comuna, año.",
        "portal": "https://datosabiertos.mineduc.cl/matricula-por-estudiante/",
        "ckan_id": None,
        "urls": [],
    },
    "directorio_establecimientos": {
        "descripcion": "Directorio oficial de establecimientos. RBD, nombre, "
                       "comuna, dependencia (para verificar RBD de emblemáticos).",
        "portal": "https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/",
        "ckan_id": None,
        "urls": [
            "https://datosabiertos.mineduc.cl/wp-content/uploads/2025/11/Directorio-Oficial-EE-2025.rar",
        ],
    },
    "simce_2medio": {
        "descripcion": "Bases SIMCE 2° medio: cuestionario de padres (escolaridad "
                       "e ingreso del hogar) + resultados, con MRUN. Base del NSE.",
        # OJO: el SIMCE lo distribuye la Agencia de Calidad de la Educación, no
        # el portal de datos abiertos del MINEDUC.
        "portal": "https://www.agenciaeducacion.cl/evaluaciones/bases-de-datos-nacionales/",  # verificar
        "ckan_id": None,
        "urls": [],
    },
    "estudiantes_prioritarios_sep": {
        "descripcion": "Estudiantes prioritarios / SEP. Fuente complementaria de "
                       "vulnerabilidad para años recientes (2017-2025).",
        "portal": "https://datosabiertos.mineduc.cl/",  # verificar (buscar 'prioritarios')
        "ckan_id": None,
        "urls": [],
    },
}
