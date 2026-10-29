# 🐍 Guía Práctica de Tkinter en Python

Un repositorio educativo, modular y completo que demuestra las principales características, widgets y buenas prácticas para el desarrollo de aplicaciones de escritorio con la biblioteca estándar Tkinter en Python.

Todo el código fuente, la documentación, los comentarios y los textos de interfaz están completamente en español.

## 📌 Tabla de Contenidos

1. [Características del Proyecto](#características-del-proyecto)
2. [Estructura del Repositorio](#estructura-del-repositorio)
3. [Requisitos](#requisitos)
4. [Instalación y Uso](#instalación-y-uso)
5. [Detalle de los Módulos](#detalle-de-los-módulos)
6. [Buenas Prácticas en Tkinter](#buenas-prácticas-en-tkinter)
7. [Licencia](#licencia)

---

## Características del Proyecto

- **Consola de Cálculos Moderna**: Interfaz gráfica en una vista única, optimizada y libre de menús innecesarios, orientada al flujo de trabajo del usuario.
- **Terminal Integrada con Scroll**: Cuadro de texto interactivo (`scrolledtext.ScrolledText`) que simula la salida de una terminal estándar para inspeccionar los resultados de los cálculos en tiempo real.
- **Procesamiento Vectorizado con Pandas y NumPy**: Carga, exploración, filtrado y cálculo de promedios sin bucles tradicionales (`for`/`while`), aprovechando el rendimiento de operaciones vectorizadas.
- **Generación Automatizada de Gráficas**: Creación de figuras analíticas con Matplotlib a 300 DPI (gráficas de barras, histogramas de frecuencia y líneas de tendencia por unidad).
- **Exportación Directa de Entregables**: Generación de archivos CSV normalizados (`promedios_alumnos.csv`) y guardado de imágenes PNG mediante botones de acción accesibles.
- **Doble Modalidad de Ejecución**: Soporte para ejecución en entorno de escritorio interactivo (GUI) y modo de línea de comandos (`--cli`) para automatización o entornos sin servidor X/pantalla.
- **Soporte DPI en Windows**: Configuración de conciencia de alta resolución para garantizar nitidez tipográfica en pantallas modernas.

---

## Estructura del Repositorio

```text
Practica2_Unidad2/
│
├── Main.py                   # Aplicación principal con interfaz gráfica (Consola de Cálculos)
├── practica_pandas.py        # Script modular para ejecución de los 6 ejercicios por consola
├── calificaciones_isc.csv    # Dataset base con 288 registros de evaluaciones académicas
│
├── promedios_alumnos.csv     # Entregable CSV generado con promedios ordenados por alumno
├── promedio_materias.png     # Gráfica de barras de promedios por materia (300 DPI)
├── histograma.png            # Histograma de distribución de calificaciones (300 DPI)
├── tendencia_unidades.png    # Gráfica de líneas de rendimiento por unidad académica (300 DPI)
│
└── README.md                 # Documentación técnica y guía de usuario del proyecto
```

---

## Requisitos

El proyecto está desarrollado para ser ligero y requerir una cantidad mínima de dependencias externas:

- **Python**: 3.9 o superior
- **Tkinter**: Incluido de forma nativa en la mayoría de las instalaciones estándar de Python.
- **Pandas**: Manipulación, agregación y filtrado tabular de datos.
- **NumPy**: Operaciones lógicas y condicionales vectorizadas (`np.where`).
- **Matplotlib**: Trazado y renderizado de figuras estadísticas en alta resolución.

---

## Instalación y Uso

### 1. Clonar o descargar el repositorio
Descarga la carpeta del proyecto en tu equipo local y accede a ella desde tu terminal o explorador de archivos.

### 2. Crear entorno virtual (Recomendado)
```bash
# En Windows (PowerShell / CMD)
python -m venv .venv
.venv\Scripts\activate

# En Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install pandas numpy matplotlib
```

### 4. Ejecutar la aplicación gráfica (GUI)
Para iniciar la **Consola de Cálculos**:
```bash
python Main.py
```

### 5. Ejecutar en modo consola (CLI)
Si prefieres ejecutar el análisis directamente en la terminal estándar:
```bash
# Opción 1: Mediante la bandera --cli de la aplicación principal
python Main.py --cli

# Opción 2: Mediante el script modular independiente
python practica_pandas.py
```

---

## Detalle de los Módulos

### 1. Interfaz Gráfica (`Main.py`)
La aplicación implementa una arquitectura orientada a eventos con separación entre la lógica de negocio (`CalculosEngine`) y la capa visual con pestañas (`DashboardNotebookApp`):

- **Panel de Pestañas (Notebook de 7 Pestañas)**:
  - **Pestañas 1 a 6 (`Ejercicio 1` a `Ejercicio 6`)**: Cada pestaña dispone de un cuadro de texto con scroll en modo solo lectura (`ScrolledText`) que presenta de manera exclusiva y estructurada la salida de cálculos del ejercicio correspondiente. Cada una cuenta además con un botón de copiado rápido al portapapeles.
  - **Pestaña 7 (`Visualización de Gráficas`)**: Incrusta interactivamente mediante `FigureCanvasTkAgg` las 3 figuras estadísticas de Matplotlib (`Promedio por Materia`, `Histograma Global` y `Tendencia por Unidad`). Cada figura incluye una tarjeta con su **ruta física exacta en disco** (`.resolve()`), especificaciones técnicas y accesos directos para abrir la imagen o la carpeta local.
- **Botones Globales de Entregables**:
  - `🔄 Recalcular Todo`: Procesa nuevamente las agregaciones y actualiza en tiempo real todas las pestañas.
  - `📁 Exportar CSV`: Genera y guarda `promedios_alumnos.csv` con las columnas `matricula`, `nombre` y `promedio`.
  - `💾 Guardar Gráficas PNG`: Guarda en disco las 3 gráficas a 300 DPI y confirma su ubicación.

### 2. Lógica de los 6 Ejercicios de Análisis

| Ejercicio | Descripción Técnica | Métodos / Funciones Utilizadas |
| :--- | :--- | :--- |
| **Ejercicio 1: Carga y Revisión** | Carga del CSV, dimensiones (288 filas, 7 columnas), dtypes y estadística descriptiva (`describe`). | `pd.read_csv`, `df.shape`, `df.dtypes`, `df.describe()` |
| **Ejercicio 2: Filtros Vectorizados** | Consultas booleanas sin ciclos: a) Grupo A, b) Calificaciones < 70, c) Bases de datos en Grupo B con nota >= 80. | Operadores `&`, `==`, `<`, `>=` sobre Series de Pandas |
| **Ejercicio 3: Columna Calculada** | Creación de columna `situacion` clasificando valores en *Aprobado* o *Reprobado*. | `np.where(df['calificacion'] >= 70, 'Aprobado', 'Reprobado')` |
| **Ejercicio 4: Resúmenes y Exportación** | Agrupaciones por materia, grupo y alumno; cálculo de medias y exportación a CSV sin índice. | `df.groupby()`, `mean()`, `to_csv(index=False)` |
| **Ejercicio 5: Gráficas Estadísticas** | Renderizado y guardado de las 3 visualizaciones oficiales a 300 DPI. | `plt.subplots`, `ax.bar`, `ax.hist`, `ax.plot`, `savefig` |
| **Ejercicio 6: Interpretación Analítica** | Detección de asignatura más baja, análisis de la tendencia decreciente en Unidad 3 y detección de alumnos con promedio < 70. | Análisis de mínimos (`idxmin`), series de promedios y filtrado |

---

## Buenas Prácticas en Tkinter

En este proyecto se aplican diversas buenas prácticas recomendadas para el desarrollo con Tkinter en Python:

1. **Separación de Lógica y Presentación**: El motor de cálculo (`CalculosEngine`) no depende de widgets de Tkinter, lo que permite reutilizar el código tanto en interfaz de usuario como en pruebas de consola o scripts de procesamiento batch.
2. **Soporte de Alta Densidad de Píxeles (DPI Awareness)**: En sistemas Windows, se invoca `windll.shcore.SetProcessDpiAwareness(1)` al inicio para evitar que las fuentes y botones se vean borrosos en pantallas con escalado superior al 100%.
3. **Manejo Seguro del Backend de Matplotlib**: Al generar y guardar gráficas para exportación, se emplea el backend estático `matplotlib.use("Agg")`, evitando interferencias o congelamientos en el ciclo de eventos principal de Tkinter (`mainloop`).
4. **Terminal Simulada de Solo Lectura**: El widget `ScrolledText` se protege con `state="disabled"` para prevenir edición accidental por parte del usuario, alternando temporalmente a `state="normal"` únicamente durante las escrituras del programa.
5. **Retroalimentación Visual Inmediata**: La interfaz notifica al usuario mediante insignias de estado (badges), cambios de cursor, mensajes contextuales e interactividad visual con modales `messagebox`.
6. **Diseño Limpio y Minimalista**: Se eligen paletas de color con contraste balanceado, jerarquía tipográfica consistente y espaciado proporcional con `pack` y `grid`.

---

## Licencia

Este proyecto se distribuye bajo los términos de la [Licencia MIT](https://opensource.org/licenses/MIT). Eres libre de usar, modificar y distribuir este código con propósitos académicos y profesionales.
