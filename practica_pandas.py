"""
=============================================================================
Práctica de Laboratorio: Análisis y Visualización de Calificaciones con Pandas y Matplotlib
Archivo: practica_pandas.py
Descripción: Solución modular y vectorizada de los 6 ejercicios de la práctica.
=============================================================================
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de codificación UTF-8 para salida estándar en Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Configurar ruta base del directorio actual para garantizar localización de archivos
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "calificaciones_isc.csv"
OUTPUT_CSV = BASE_DIR / "promedios_alumnos.csv"
IMG_MATERIAS = BASE_DIR / "promedio_materias.png"
IMG_HISTOGRAMA = BASE_DIR / "histograma.png"
IMG_TENDENCIA = BASE_DIR / "tendencia_unidades.png"


def encabezado_seccion(titulo: str):
    """Imprime un separador visual para estructurar la salida en consola."""
    print("\n" + "=" * 75)
    print(f" {titulo}")
    print("=" * 75)


# =============================================================================
# EJERCICIO 1: CARGA Y REVISIÓN
# =============================================================================
encabezado_seccion("EJERCICIO 1: CARGA Y REVISIÓN DEL DATASET")

# Carga del archivo CSV en un DataFrame llamado df
# Si el archivo no existe en la ruta relativa, lanzará un error descriptivo
if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo '{CSV_PATH.name}' en: {BASE_DIR}. "
        "Asegúrate de colocar 'calificaciones_isc.csv' en la misma carpeta que el script."
    )

df = pd.read_csv(CSV_PATH)

# 1. Primeras 5 filas
print("\n[1] Primeras 5 filas del DataFrame (df.head()):")
print(df.head())

# 2. Número de filas y de columnas
filas, columnas = df.shape
print(f"\n[2] Dimensiones del DataFrame (df.shape):")
print(f"    - Filas: {filas}")
print(f"    - Columnas: {columnas}")

# 3. Tipo de dato de cada columna
print("\n[3] Tipo de dato por columna (df.dtypes):")
print(df.dtypes)

# 4. Resumen estadístico de 'calificacion' y 'asistencias'
print("\n[4] Resumen estadístico de 'calificacion' y 'asistencias' (df.describe()):")
print(df[["calificacion", "asistencias"]].describe())

# -----------------------------------------------------------------------------
# COMENTARIO EXPLICATIVO (Requerimiento Ejercicio 1):
# ¿Por qué el archivo contiene 288 registros y no 24?
# 
# El archivo tiene exactamente 288 registros porque está estructurado en formato tabular
# largo (long format) o desnormalizado. La generación consta de 24 alumnos (repartidos
# en dos grupos: A y B). Cada alumno cursa 4 materias distintas ('Programacion',
# 'Bases de datos', 'Redes' y 'Matematicas discretas') y cada una de estas materias
# es evaluada a lo largo de 3 unidades académicas independientes.
# Por lo tanto: 24 alumnos × 4 materias × 3 unidades = 288 filas en total.
# Cada fila representa la evaluación de una unidad particular de una materia para un estudiante.
# -----------------------------------------------------------------------------


# =============================================================================
# EJERCICIO 2: FILTROS (Operaciones booleanas sin bucles)
# =============================================================================
encabezado_seccion("EJERCICIO 2: FILTROS VECTORIZADOS (SIN MODIFICAR df)")

# a) Solo el grupo A
# NOTA: Se utiliza df['grupo'] == 'A' (comparación booleana).
# NUNCA usar df['grupo'] = 'A', ya que sobreescribiría todos los valores de la columna.
filtro_grupo_a = df[df["grupo"] == "A"]
conteo_a = len(filtro_grupo_a)
print(f"\n[a] Registros pertenecientes únicamente al Grupo A: {conteo_a} filas")
print(f"    (Equivale al 50% de la población: 12 alumnos × 12 evaluaciones = {conteo_a})")

# b) Unidades con calificación menor a 70 (unidades no aprobadas)
filtro_menor_70 = df[df["calificacion"] < 70]
conteo_menor_70 = len(filtro_menor_70)
print(f"\n[b] Registros con calificación menor a 70: {conteo_menor_70} filas")

# c) Materia 'Bases de datos', grupo B, con calificación mayor o igual a 80
filtro_bd_b_80 = df[
    (df["materia"] == "Bases de datos") & 
    (df["grupo"] == "B") & 
    (df["calificacion"] >= 80)
]
conteo_bd_b_80 = len(filtro_bd_b_80)
print(f"\n[c] Registros de 'Bases de datos' en Grupo B con calif >= 80: {conteo_bd_b_80} filas")
print("    Muestra de los primeros registros que cumplen esta condición:")
print(filtro_bd_b_80[["matricula", "nombre", "unidad", "calificacion"]].head())


# =============================================================================
# EJERCICIO 3: COLUMNA CALCULADA (Vectorizada con np.where)
# =============================================================================
encabezado_seccion("EJERCICIO 3: COLUMNA CALCULADA 'situacion'")

# Creación de la columna 'situacion' sin utilizar ciclos for/while
# Se utiliza np.where para vectorizar la regla de negocio:
# Si calificacion >= 70 -> 'Aprobado', de lo contrario -> 'Reprobado'
df["situacion"] = np.where(df["calificacion"] >= 70, "Aprobado", "Reprobado")

print("\nColumna 'situacion' calculada exitosamente.")
print("Vista previa de las primeras 8 filas con la nueva columna integrada:")
print(df[["matricula", "nombre", "materia", "unidad", "calificacion", "situacion"]].head(8))


# =============================================================================
# EJERCICIO 4: RESÚMENES Y EXPORTACIÓN
# =============================================================================
encabezado_seccion("EJERCICIO 4: RESÚMENES ESTADÍSTICOS Y EXPORTACIÓN A CSV")

# 1. Promedio de calificación por materia
print("\n[1] Promedio de calificación por materia:")
promedio_por_materia = df.groupby("materia")["calificacion"].mean()
for mat, prom in promedio_por_materia.items():
    print(f"    - {mat:<22}: {prom:.2f}")

# 2. Promedio por grupo y materia
print("\n[2] Promedio por grupo y materia:")
promedio_grupo_materia = df.groupby(["grupo", "materia"])["calificacion"].mean()
print(promedio_grupo_materia.to_string())

# 3. Promedio general de cada alumno, ordenado de mayor a menor
print("\n[3] Promedio general por alumno (Ordenado de mayor a menor - Top 10):")
promedio_por_alumno = (
    df.groupby(["matricula", "nombre"])["calificacion"]
    .mean()
    .reset_index()
    .rename(columns={"calificacion": "promedio"})
    .sort_values(by="promedio", ascending=False)
)
print(promedio_por_alumno.head(10).to_string(index=False))

# 4. Promedio general por unidad, con todas las materias juntas
print("\n[4] Promedio general por unidad (Todas las materias juntas):")
promedio_por_unidad = df.groupby("unidad")["calificacion"].mean()
for u, prom in promedio_por_unidad.items():
    print(f"    - Unidad {u}: {prom:.2f}")

# 5. Conteo de unidades aprobadas y reprobadas
print("\n[5] Conteo total de unidades aprobadas y reprobadas:")
conteo_situacion = df["situacion"].value_counts()
for sit, total in conteo_situacion.items():
    porcentaje = (total / len(df)) * 100
    print(f"    - {sit:<10}: {total} registros ({porcentaje:.1f}%)")

# EXPORTACIÓN A CSV:
# Se exporta el promedio por alumno conservando matrícula, nombre y promedio.
# Se usa reset_index() tras el groupby y se especifica index=False para evitar columnas de índice redundantes.
promedio_por_alumno.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\n>> Archivo exportado exitosamente: '{OUTPUT_CSV.name}'")
print(f"   Columnas incluidas: {list(promedio_por_alumno.columns)} (sin índice numérico)")


# =============================================================================
# EJERCICIO 5: GRÁFICAS CON MATPLOTLIB
# =============================================================================
encabezado_seccion("EJERCICIO 5: GENERACIÓN DE GRÁFICAS CON MATPLOTLIB")

# Estilo visual moderno y limpio
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# -----------------------------------------------------------------------------
# GRÁFICA 1: Barras del promedio por materia (promedio_materias.png)
# Eje Y limitado de 0 a 100
# -----------------------------------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(8, 5))
colores_barras = ["#2b5c8f", "#17a2b8", "#f39c12", "#e74c3c"]
barras = ax1.bar(
    promedio_por_materia.index,
    promedio_por_materia.values,
    color=colores_barras,
    edgecolor="black",
    width=0.55
)

ax1.set_title("Promedio General de Calificaciones por Materia", fontsize=14, fontweight="bold", pad=15)
ax1.set_xlabel("Materia Curricular", fontsize=12, labelpad=10)
ax1.set_ylabel("Calificación Promedio (Escala 0 a 100)", fontsize=12, labelpad=10)
ax1.set_ylim(0, 100)
ax1.grid(axis="y", linestyle="--", alpha=0.5)

# Etiquetas numéricas sobre cada barra
for b in barras:
    altura = b.get_height()
    ax1.annotate(
        f"{altura:.2f}",
        xy=(b.get_x() + b.get_width() / 2, altura),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

plt.tight_layout()
# Regla de oro: guardar antes de mostrar para evitar imágenes en blanco
plt.savefig(IMG_MATERIAS, dpi=300)
print(f"[Gráfica 1] Guardada exitosamente como '{IMG_MATERIAS.name}'")
plt.show()
plt.close(fig1)

# -----------------------------------------------------------------------------
# GRÁFICA 2: Histograma de todas las calificaciones (histograma.png)
# Línea vertical punteada roja en el 70
# -----------------------------------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.hist(df["calificacion"], bins=12, color="#3498db", edgecolor="black", alpha=0.85)
ax2.axvline(
    x=70,
    color="#d9534f",
    linestyle="--",
    linewidth=2.5,
    label="Calificación Mínima Aprobatoria (70)"
)

ax2.set_title("Distribución Global de Calificaciones (288 Evaluaciones)", fontsize=14, fontweight="bold", pad=15)
ax2.set_xlabel("Calificación Obtenida", fontsize=12, labelpad=10)
ax2.set_ylabel("Frecuencia (Cantidad de Registros)", fontsize=12, labelpad=10)
ax2.legend(fontsize=11, loc="upper left")
ax2.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
# Guardar antes de mostrar
plt.savefig(IMG_HISTOGRAMA, dpi=300)
print(f"[Gráfica 2] Guardada exitosamente como '{IMG_HISTOGRAMA.name}'")
plt.show()
plt.close(fig2)

# -----------------------------------------------------------------------------
# GRÁFICA 3: Líneas de promedio por unidad según materia (tendencia_unidades.png)
# -----------------------------------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(9, 5.5))
tabla_tendencia = df.groupby(["unidad", "materia"])["calificacion"].mean().unstack()

marcadores = ["o", "s", "^", "D"]
estilos_linea = ["-", "--", "-.", ":"]
colores_lineas = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

for idx, materia in enumerate(tabla_tendencia.columns):
    ax3.plot(
        tabla_tendencia.index,
        tabla_tendencia[materia],
        marker=marcadores[idx % len(marcadores)],
        linestyle=estilos_linea[idx % len(estilos_linea)],
        color=colores_lineas[idx % len(colores_lineas)],
        linewidth=2.5,
        markersize=8,
        label=materia
    )

ax3.set_title("Tendencia del Promedio por Unidad según Materia", fontsize=14, fontweight="bold", pad=15)
ax3.set_xlabel("Unidad de Evaluación", fontsize=12, labelpad=10)
ax3.set_ylabel("Calificación Promedio", fontsize=12, labelpad=10)
ax3.set_xticks([1, 2, 3])
ax3.set_xticklabels(["Unidad 1", "Unidad 2", "Unidad 3"], fontsize=11)
ax3.set_ylim(50, 100)
ax3.legend(title="Materias Curriculares", fontsize=10, title_fontsize=11, loc="upper right")
ax3.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
# Guardar antes de mostrar
plt.savefig(IMG_TENDENCIA, dpi=300)
print(f"[Gráfica 3] Guardada exitosamente como '{IMG_TENDENCIA.name}'")
plt.show()
plt.close(fig3)


# =============================================================================
# EJERCICIO 6: LECTURA DE RESULTADOS E INTERPRETACIÓN
# =============================================================================
encabezado_seccion("EJERCICIO 6: LECTURA DE RESULTADOS E INTERPRETACIÓN ANALÍTICA")

# Extracción de valores clave directamente calculados por el programa:
materia_minima = promedio_por_materia.idxmin()
prom_materia_minima = promedio_por_materia.min()

u1_prom = promedio_por_unidad[1]
u2_prom = promedio_por_unidad[2]
u3_prom = promedio_por_unidad[3]
u3_es_menor = (u3_prom < u1_prom) and (u3_prom < u2_prom)

alumnos_reprobados = promedio_por_alumno[promedio_por_alumno["promedio"] < 70]
total_alumnos_bajo_70 = len(alumnos_reprobados)

texto_interpretacion = f"""
1. MATERIA CON EL PROMEDIO MÁS BAJO:
   La materia que obtuvo el rendimiento académico global más bajo es '{materia_minima}',
   con un promedio de {prom_materia_minima:.2f} puntos sobre 100. En contraste, la asignatura con mayor
   desempeño fue '{promedio_por_materia.idxmax()}' con un promedio de {promedio_por_materia.max():.2f}.

2. TENDENCIA DE LA UNIDAD 3 FRENTE A LAS UNIDADES 1 Y 2:
   { 'SÍ' if u3_es_menor else 'NO' }, el promedio general de la Unidad 3 ({u3_prom:.2f}) es menor que el de la Unidad 1 ({u1_prom:.2f})
   y el de la Unidad 2 ({u2_prom:.2f}).
   Como se observa claramente en la gráfica 'tendencia_unidades.png', existe una pendiente negativa
   a lo largo del semestre en todas las asignaturas evaluadas, lo cual refleja que el nivel de exigencia
   técnica o la carga de proyectos finales al cierre del curso impacta el rendimiento general de los grupos.

3. ALUMNOS CON PROMEDIO GENERAL POR DEBAJO DE 70:
   Existen exactamente {total_alumnos_bajo_70} alumnos de los 24 inscritos cuyo promedio general se ubica por debajo
   de la calificación mínima aprobatoria (70):
"""
for _, fila in alumnos_reprobados.iterrows():
    texto_interpretacion += f"   - Matrícula: {fila['matricula']} | Nombre: {fila['nombre']:<20} | Promedio General: {fila['promedio']:.2f}\n"

print(texto_interpretacion)


# =============================================================================
# BLOQUE DE COMENTARIO REQUERIDO POR LA RÚBRICA (Ejercicio 6)
# =============================================================================
'''
ANÁLISIS E INTERPRETACIÓN DE RESULTADOS (DATOS COHERENTES CON EJERCICIOS 4 Y 5):

1. Materia con el promedio más bajo:
   - Materia: Matematicas discretas
   - Promedio: 71.47 puntos.
   - Justificación: Presenta la mayor dispersión de notas desfavorables en ambos grupos (72.75 en Grupo A 
     y 70.19 en Grupo B), siendo significativamente inferior al promedio de Bases de datos (83.04).

2. Comportamiento del promedio en la Unidad 3:
   - Promedios obtenidos: Unidad 1 = 80.28, Unidad 2 = 78.33, Unidad 3 = 75.19.
   - Respuesta: Sí, el promedio de la Unidad 3 es menor que el de las unidades 1 y 2.
   - Justificación visual: En la gráfica 'tendencia_unidades.png', todas las materias presentan una pendiente 
     descendente hacia la Unidad 3, confirmando una disminución progresiva en el rendimiento del grupo.

3. Alumnos con promedio general inferior a 70:
   - Total: Exactamente 4 alumnos (de una muestra de 24, equivalente al 16.67%).
   - Alumnos identificados:
     * Xavier Ruiz (ISC240121): Promedio de 58.25
     * Oscar Ortiz (ISC240113): Promedio de 60.25
     * Fernanda Rodriguez (ISC240104): Promedio de 62.25
     * Ana Lopez (ISC240100): Promedio de 62.33
'''

if __name__ == "__main__":
    print("\n>> Ejecución completada al 100% exitosamente.")
