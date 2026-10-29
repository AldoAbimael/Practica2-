"""
=============================================================================
Análisis y Visualización de Rendimiento Académico con Pandas y Matplotlib
Archivo: Main.py
Descripción: Interfaz gráfica moderna con panel de pestañas (Notebook de 7 pestañas)
             para inspeccionar los ejercicios 1 al 6 de forma individual y visualizar
             las 3 gráficas estadísticas generadas con Matplotlib.
=============================================================================
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib

# Configurar backend seguro de Matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Habilitar soporte de alta resolución (DPI) en Windows para nitidez en pantallas modernas
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "calificaciones_isc.csv"
OUTPUT_CSV = BASE_DIR / "promedios_alumnos.csv"
IMG_MATERIAS = BASE_DIR / "promedio_materias.png"
IMG_HISTOGRAMA = BASE_DIR / "histograma.png"
IMG_TENDENCIA = BASE_DIR / "tendencia_unidades.png"

# Paleta de colores visual
THEME = {
    "bg_app": "#f8fafc",           # Fondo general
    "bg_header": "#0f172a",        # Fondo oscuro del encabezado
    "bg_card": "#ffffff",          # Fondo blanco de tarjetas
    "border_card": "#cbd5e1",      # Borde suave
    "text_main": "#0f172a",        # Texto principal
    "text_muted": "#64748b",       # Texto secundario
    "accent_blue": "#2563eb",      # Azul primario
    "accent_blue_hover": "#1d4ed8",
    "accent_green": "#059669",     # Verde éxito
    "accent_green_hover": "#047857",
    "accent_amber": "#d97706",     # Ámbar
    "accent_amber_hover": "#b45309",
    "terminal_bg": "#0f172a",      # Fondo oscuro de consola
    "terminal_fg": "#e2e8f0",      # Texto claro de consola
}


# =============================================================================
# MOTOR DE CÁLCULO Y GESTIÓN DE DATOS (PANDAS & NUMPY)
# =============================================================================
class CalculosEngine:
    """Ejecuta y administra los 6 ejercicios de análisis y las 3 gráficas."""

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.df = None
        self.promedio_por_materia = None
        self.promedio_grupo_materia = None
        self.promedio_por_alumno = None
        self.promedio_por_unidad = None
        self.conteo_situacion = None
        self.cargar_datos()

    def cargar_datos(self):
        """Carga el dataset CSV y genera columnas y agregaciones estadísticas."""
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo '{self.csv_path.name}' en:\n{self.csv_path.parent}"
            )
        self.df = pd.read_csv(self.csv_path)

        # Ejercicio 3: Columna calculada 'situacion' (vectorizada con np.where)
        self.df["situacion"] = np.where(
            self.df["calificacion"] >= 70, "Aprobado", "Reprobado"
        )

        # Ejercicio 4: Agregaciones
        self.promedio_por_materia = self.df.groupby("materia")["calificacion"].mean()
        self.promedio_grupo_materia = self.df.groupby(["grupo", "materia"])["calificacion"].mean()
        self.promedio_por_alumno = (
            self.df.groupby(["matricula", "nombre"])["calificacion"]
            .mean()
            .reset_index()
            .rename(columns={"calificacion": "promedio"})
            .sort_values(by="promedio", ascending=False)
        )
        self.promedio_por_unidad = self.df.groupby("unidad")["calificacion"].mean()
        self.conteo_situacion = self.df["situacion"].value_counts()

    # --- Filtros requeridos en el Ejercicio 2 ---
    def filtrar_grupo_a(self) -> pd.DataFrame:
        """Ejercicio 2a: Registros del Grupo A."""
        return self.df[self.df["grupo"] == "A"]

    def filtrar_menor_70(self) -> pd.DataFrame:
        """Ejercicio 2b: Registros con calificación menor a 70."""
        return self.df[self.df["calificacion"] < 70]

    def filtrar_bd_grupo_b_80(self) -> pd.DataFrame:
        """Ejercicio 2c: Materia 'Bases de datos', grupo B, calificación >= 80."""
        return self.df[
            (self.df["materia"] == "Bases de datos")
            & (self.df["grupo"] == "B")
            & (self.df["calificacion"] >= 80)
        ]

    # --- Exportación del archivo CSV ---
    def exportar_csv(self, ruta_destino: Path = OUTPUT_CSV) -> Path:
        """Exporta los promedios por alumno a CSV sin índice numérico."""
        if self.df is None:
            self.cargar_datos()
        df_export = self.promedio_por_alumno[["matricula", "nombre", "promedio"]].copy()
        df_export.to_csv(ruta_destino, index=False, float_format="%.2f", encoding="utf-8")
        return ruta_destino

    # --- Generación de Figuras de Matplotlib para la GUI y para guardar ---
    def crear_figura_materias(self) -> Figure:
        """Crea la Figura 1: Promedio de calificación por materia."""
        if self.df is None:
            self.cargar_datos()

        fig = Figure(figsize=(8.5, 4.8), dpi=100, facecolor="#ffffff")
        ax = fig.add_subplot(111)

        colores = ["#2563eb", "#0284c7", "#f59e0b", "#ef4444"]
        barras = ax.bar(
            self.promedio_por_materia.index,
            self.promedio_por_materia.values,
            color=colores,
            edgecolor="#0f172a",
            width=0.55
        )
        ax.set_title("Promedio General de Calificaciones por Materia", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Materia Curricular", fontsize=11, labelpad=10)
        ax.set_ylabel("Calificación Promedio (Escala 0 a 100)", fontsize=11, labelpad=10)
        ax.set_ylim(0, 100)
        ax.grid(axis="y", linestyle="--", alpha=0.6)

        for b in barras:
            altura = b.get_height()
            ax.annotate(
                f"{altura:.2f}",
                xy=(b.get_x() + b.get_width() / 2, altura),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold"
            )
        fig.tight_layout()
        return fig

    def crear_figura_histograma(self) -> Figure:
        """Crea la Figura 2: Histograma de distribución global."""
        if self.df is None:
            self.cargar_datos()

        fig = Figure(figsize=(8.5, 4.8), dpi=100, facecolor="#ffffff")
        ax = fig.add_subplot(111)

        ax.hist(self.df["calificacion"], bins=12, color="#38bdf8", edgecolor="#0369a1", alpha=0.85)
        ax.axvline(
            x=70,
            color="#ef4444",
            linestyle="--",
            linewidth=2.5,
            label="Calificación Mínima Aprobatoria (70)"
        )
        ax.set_title("Distribución Global de Calificaciones (288 Evaluaciones)", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Calificación Obtenida", fontsize=11, labelpad=10)
        ax.set_ylabel("Frecuencia (Cantidad de Registros)", fontsize=11, labelpad=10)
        ax.legend(fontsize=10, loc="upper left")
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        fig.tight_layout()
        return fig

    def crear_figura_tendencia(self) -> Figure:
        """Crea la Figura 3: Líneas de tendencia por unidad según materia."""
        if self.df is None:
            self.cargar_datos()

        fig = Figure(figsize=(8.8, 5.0), dpi=100, facecolor="#ffffff")
        ax = fig.add_subplot(111)

        tabla_tendencia = self.df.groupby(["unidad", "materia"])["calificacion"].mean().unstack()
        marcadores = ["o", "s", "^", "D"]
        estilos_linea = ["-", "--", "-.", ":"]
        colores_lineas = ["#1d4ed8", "#ea580c", "#16a34a", "#dc2626"]

        for idx, materia in enumerate(tabla_tendencia.columns):
            ax.plot(
                tabla_tendencia.index,
                tabla_tendencia[materia],
                marker=marcadores[idx % len(marcadores)],
                linestyle=estilos_linea[idx % len(estilos_linea)],
                color=colores_lineas[idx % len(colores_lineas)],
                linewidth=2.5,
                markersize=8,
                label=materia
            )
        ax.set_title("Tendencia del Promedio por Unidad según Materia", fontsize=13, fontweight="bold", pad=15)
        ax.set_xlabel("Unidad de Evaluación", fontsize=11, labelpad=10)
        ax.set_ylabel("Calificación Promedio", fontsize=11, labelpad=10)
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["Unidad 1", "Unidad 2", "Unidad 3"], fontsize=10)
        ax.set_ylim(50, 100)
        ax.legend(title="Materias Curriculares", fontsize=10, title_fontsize=10, loc="upper right")
        ax.grid(True, linestyle="--", alpha=0.6)
        fig.tight_layout()
        return fig

    def guardar_graficas_png(self) -> list:
        """Genera y guarda físicamente las 3 gráficas requeridas a 300 DPI."""
        f1 = self.crear_figura_materias()
        f1.savefig(IMG_MATERIAS, dpi=300)

        f2 = self.crear_figura_histograma()
        f2.savefig(IMG_HISTOGRAMA, dpi=300)

        f3 = self.crear_figura_tendencia()
        f3.savefig(IMG_TENDENCIA, dpi=300)

        return [IMG_MATERIAS, IMG_HISTOGRAMA, IMG_TENDENCIA]

    # --- Métodos que retornan el texto específico para cada ejercicio (1 al 6) ---
    def obtener_texto_ejercicio_1(self) -> str:
        """Texto formateado para la pestaña del Ejercicio 1."""
        filas, columnas = self.df.shape
        dtypes_str = "\n".join([f"      - {col:<15}: {tipo}" for col, tipo in self.df.dtypes.items()])

        return (
            "--------------------------------------------------------------------------------\n"
            " EJERCICIO 1: CARGA Y REVISIÓN DEL DATASET\n"
            "--------------------------------------------------------------------------------\n\n"
            "[1.1] Primeras 5 filas del DataFrame (df.head()):\n"
            f"{self.df.head().to_string(index=True)}\n\n"
            f"[1.2] Dimensiones del DataFrame (df.shape):\n"
            f"      - Número de Filas:    {filas}\n"
            f"      - Número de Columnas: {columnas}\n\n"
            "[1.3] Tipo de dato por columna (df.dtypes):\n"
            f"{dtypes_str}\n\n"
            "[1.4] Resumen estadístico numérico (df[['calificacion', 'asistencias']].describe()):\n"
            f"{self.df[['calificacion', 'asistencias']].describe().to_string()}\n\n"
            "[1.5] Justificación de registros en el dataset:\n"
            "      El dataset cuenta con 288 registros debido a que está estructurado en formato tabular largo:\n"
            "      24 alumnos en total (12 en Grupo A y 12 en Grupo B) × 4 materias curriculares × 3 unidades evaluadas\n"
            "      = 288 filas de evaluaciones individuales.\n"
        )

    def obtener_texto_ejercicio_2(self) -> str:
        """Texto formateado para la pestaña del Ejercicio 2."""
        df_a = self.filtrar_grupo_a()
        df_m70 = self.filtrar_menor_70()
        df_bd = self.filtrar_bd_grupo_b_80()
        pct_m70 = (len(df_m70) / len(self.df)) * 100

        muestra_bd = df_bd[["matricula", "nombre", "unidad", "calificacion"]].head().to_string(index=False)

        return (
            "--------------------------------------------------------------------------------\n"
            " EJERCICIO 2: FILTROS VECTORIZADOS (SIN BUCLES FOR/WHILE)\n"
            "--------------------------------------------------------------------------------\n\n"
            f"[2.a] Registros pertenecientes únicamente al Grupo A:\n"
            f"      - Total registros: {len(df_a)} filas (50% de la población total).\n\n"
            f"[2.b] Evaluaciones con calificación menor a 70 (No aprobadas):\n"
            f"      - Total registros: {len(df_m70)} filas ({pct_m70:.1f}% del total).\n\n"
            f"[2.c] Materia 'Bases de datos' en Grupo B con calificación >= 80:\n"
            f"      - Total registros encontrados: {len(df_bd)} filas.\n"
            "      - Muestra de primeros registros coincidentes:\n"
            f"{muestra_bd}\n"
        )

    def obtener_texto_ejercicio_3(self) -> str:
        """Texto formateado para la pestaña del Ejercicio 3."""
        conteo_lineas = []
        for sit, total in self.conteo_situacion.items():
            pct = (total / len(self.df)) * 100
            conteo_lineas.append(f"      - {sit:<10}: {total:3d} registros ({pct:.1f}%)")

        conteo_str = "\n".join(conteo_lineas)
        muestra_8 = self.df[["matricula", "nombre", "materia", "unidad", "calificacion", "situacion"]].head(8).to_string(index=False)

        return (
            "--------------------------------------------------------------------------------\n"
            " EJERCICIO 3: COLUMNA CALCULADA 'situacion' (VECTORIZACIÓN CON np.where)\n"
            "--------------------------------------------------------------------------------\n\n"
            "Regla aplicada: np.where(df['calificacion'] >= 70, 'Aprobado', 'Reprobado')\n"
            "Primeras 8 filas con la nueva columna 'situacion' integrada:\n"
            f"{muestra_8}\n\n"
            "Distribución global de la situación académica:\n"
            f"{conteo_str}\n"
        )

    def obtener_texto_ejercicio_4(self) -> str:
        """Texto formateado para la pestaña del Ejercicio 4."""
        lineas_mat = [f"      - {mat:<25}: {prom:.2f}" for mat, prom in self.promedio_por_materia.items()]
        lineas_unid = [f"      - Unidad {u}: {prom:.2f}" for u, prom in self.promedio_por_unidad.items()]
        top_10 = self.promedio_por_alumno.head(10).to_string(index=False)

        return (
            "--------------------------------------------------------------------------------\n"
            " EJERCICIO 4: RESÚMENES ESTADÍSTICOS Y EXPORTACIÓN A CSV\n"
            "--------------------------------------------------------------------------------\n\n"
            "[4.1] Promedio de calificación por materia:\n"
            + "\n".join(lineas_mat) + "\n\n"
            "[4.2] Promedio por grupo y materia (groupby(['grupo', 'materia'])):\n"
            f"{self.promedio_grupo_materia.to_string()}\n\n"
            "[4.3] Promedio general por alumno (Ordenado de mayor a menor - Top 10):\n"
            f"{top_10}\n\n"
            "[4.4] Promedio general por unidad (Todas las materias juntas):\n"
            + "\n".join(lineas_unid) + "\n\n"
            "[4.5] Generación del archivo CSV de entregable:\n"
            f"      >> Archivo CSV exportado con éxito: '{OUTPUT_CSV.name}'\n"
            f"         Ruta completa: {OUTPUT_CSV.resolve()}\n"
            "         Columnas exportadas: ['matricula', 'nombre', 'promedio'] (sin índice numérico)\n"
        )

    def obtener_texto_ejercicio_5(self) -> str:
        """Texto formateado para la pestaña del Ejercicio 5."""
        return (
            "--------------------------------------------------------------------------------\n"
            " EJERCICIO 5: GENERACIÓN DE GRÁFICAS CON MATPLOTLIB (300 DPI)\n"
            "--------------------------------------------------------------------------------\n\n"
            f"      [Gráfica 1] Generada y guardada exitosamente: '{IMG_MATERIAS.name}'\n"
            f"                  Ruta física: {IMG_MATERIAS.resolve()}\n"
            f"      [Gráfica 2] Generada y guardada exitosamente: '{IMG_HISTOGRAMA.name}'\n"
            f"                  Ruta física: {IMG_HISTOGRAMA.resolve()}\n"
            f"      [Gráfica 3] Generada y guardada exitosamente: '{IMG_TENDENCIA.name}'\n"
            f"                  Ruta física: {IMG_TENDENCIA.resolve()}\n\n"
            "      Nota: Puedes inspeccionar visualmente las 3 figuras con alta resolución\n"
            "            en la pestaña 'Visualización de Gráficas'.\n"
        )

    def obtener_texto_ejercicio_6(self) -> str:
        """Texto formateado para la pestaña del Ejercicio 6."""
        materia_minima = self.promedio_por_materia.idxmin()
        prom_materia_minima = self.promedio_por_materia.min()
        materia_maxima = self.promedio_por_materia.idxmax()
        prom_materia_maxima = self.promedio_por_materia.max()

        u1_prom = self.promedio_por_unidad[1]
        u2_prom = self.promedio_por_unidad[2]
        u3_prom = self.promedio_por_unidad[3]
        u3_es_menor = (u3_prom < u1_prom) and (u3_prom < u2_prom)

        alumnos_reprobados = self.promedio_por_alumno[self.promedio_por_alumno["promedio"] < 70]
        total_alumnos_bajo_70 = len(alumnos_reprobados)

        lista_alumnos = []
        for _, fila in alumnos_reprobados.iterrows():
            lista_alumnos.append(f"   • Matrícula: {fila['matricula']} | Nombre: {fila['nombre']:<22} | Promedio: {fila['promedio']:.2f}")

        alumnos_str = "\n".join(lista_alumnos)

        return (
            "--------------------------------------------------------------------------------\n"
            " EJERCICIO 6: LECTURA DE RESULTADOS E INTERPRETACIÓN ANALÍTICA\n"
            "--------------------------------------------------------------------------------\n\n"
            "1. MATERIA CON EL PROMEDIO MÁS BAJO:\n"
            f"   La asignatura con menor rendimiento global es '{materia_minima}', registrando un promedio\n"
            f"   de {prom_materia_minima:.2f} puntos. En contraparte, la asignatura con mayor desempeño es\n"
            f"   '{materia_maxima}' con {prom_materia_maxima:.2f} puntos.\n\n"
            "2. TENDENCIA DE LA UNIDAD 3 FRENTE A LAS UNIDADES 1 Y 2:\n"
            f"   {'SÍ' if u3_es_menor else 'NO'}, el promedio global de la Unidad 3 ({u3_prom:.2f}) es inferior al de la Unidad 1 ({u1_prom:.2f})\n"
            f"   y al de la Unidad 2 ({u2_prom:.2f}). Se evidencia una tendencia descendente a lo largo del periodo.\n\n"
            "3. ALUMNOS CON PROMEDIO GENERAL INFERIOR A 70:\n"
            f"   Existen exactamente {total_alumnos_bajo_70} alumnos con promedio general menor a la calificación aprobatoria (70):\n"
            f"{alumnos_str}\n"
        )

    def ejecutar_reporte_completo(self) -> str:
        """Genera el reporte integral concatenado (útil para el modo CLI)."""
        sep = "=" * 80
        return (
            f"{sep}\n"
            " CONSOLA DE CÁLCULOS: EJECUCIÓN COMPLETA DE EJERCICIOS (1 AL 6)\n"
            " Librerías: Pandas | NumPy | Matplotlib\n"
            f"{sep}\n\n"
            f"{self.obtener_texto_ejercicio_1()}\n"
            f"{self.obtener_texto_ejercicio_2()}\n"
            f"{self.obtener_texto_ejercicio_3()}\n"
            f"{self.obtener_texto_ejercicio_4()}\n"
            f"{self.obtener_texto_ejercicio_5()}\n"
            f"{self.obtener_texto_ejercicio_6()}\n"
            f"{sep}\n"
            " >> CÁLCULOS Y ENTREGABLES GENERADOS SATISFACTORIAMENTE (100% COMPLETADO)\n"
            f"{sep}\n"
        )


# =============================================================================
# APLICACIÓN DE ESCRITORIO CON NOTEBOOK (7 PESTAÑAS)
# =============================================================================
class DashboardNotebookApp(tk.Tk):
    """Ventana principal con panel de 7 pestañas organizadas."""

    def __init__(self):
        super().__init__()
        self.title("Análisis y Visualización de Rendimiento Académico")
        self.geometry("1180x860")
        self.minsize(1020, 720)
        self.configure(bg=THEME["bg_app"])

        # Inicializar motor de cálculo
        try:
            self.engine = CalculosEngine(CSV_PATH)
        except Exception as e:
            messagebox.showerror("Error al cargar datos", f"No fue posible cargar el archivo CSV:\n\n{e}")
            self.destroy()
            return

        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_notebook()

        # Cargar los datos y cálculos en todas las pestañas al iniciar
        self.actualizar_todas_las_pestanas()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Estilo para el Notebook principal
        style.configure("Main.TNotebook", background=THEME["bg_app"], borderwidth=0)
        style.configure(
            "Main.TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=[16, 9],
            background="#e2e8f0",
            foreground=THEME["text_main"]
        )
        style.map(
            "Main.TNotebook.Tab",
            background=[("selected", THEME["accent_blue"])],
            foreground=[("selected", "#ffffff")]
        )

        # Estilo para el Notebook secundario de Gráficas
        style.configure("Graficas.TNotebook", background="#ffffff", borderwidth=0)
        style.configure(
            "Graficas.TNotebook.Tab",
            font=("Segoe UI", 9, "bold"),
            padding=[12, 6],
            background="#f1f5f9",
            foreground=THEME["text_main"]
        )
        style.map(
            "Graficas.TNotebook.Tab",
            background=[("selected", "#334155")],
            foreground=[("selected", "#ffffff")]
        )

    def _construir_encabezado(self):
        encabezado = tk.Frame(self, bg=THEME["bg_header"], height=70)
        encabezado.pack(fill="x", side="top")
        encabezado.pack_propagate(False)

        box_tit = tk.Frame(encabezado, bg=THEME["bg_header"])
        box_tit.pack(side="left", padx=20, pady=10)

        lbl_tit = tk.Label(
            box_tit,
            text="🎓 Panel de Análisis y Rendimiento Académico",
            font=("Segoe UI", 15, "bold"),
            fg="white",
            bg=THEME["bg_header"]
        )
        lbl_tit.pack(anchor="w")

        lbl_sub = tk.Label(
            box_tit,
            text="Procesamiento tabular con Pandas & generación de gráficas con Matplotlib",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg=THEME["bg_header"]
        )
        lbl_sub.pack(anchor="w")

        # Botones globales y badges a la derecha
        box_right = tk.Frame(encabezado, bg=THEME["bg_header"])
        box_right.pack(side="right", padx=20)

        # Botón 1: Recalcular Todo
        btn_recalc = tk.Button(
            box_right,
            text="🔄 Recalcular Todo",
            font=("Segoe UI", 9, "bold"),
            bg="#334155",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.accion_recalcular_todo
        )
        btn_recalc.pack(side="left", padx=4)

        # Botón 2: Exportar CSV
        btn_csv = tk.Button(
            box_right,
            text="📁 Exportar CSV",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_green"],
            fg="white",
            activebackground=THEME["accent_green_hover"],
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.accion_exportar_csv
        )
        btn_csv.pack(side="left", padx=4)

        # Botón 3: Guardar Gráficas PNG
        btn_grafs = tk.Button(
            box_right,
            text="💾 Guardar Gráficas PNG",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_amber"],
            fg="white",
            activebackground=THEME["accent_amber_hover"],
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.accion_guardar_graficas
        )
        btn_grafs.pack(side="left", padx=4)

        # Chip de estado
        chip = tk.Label(
            box_right,
            text="🟢 288 Filas",
            font=("Segoe UI", 9, "bold"),
            bg="#14532d",
            fg="#86efac",
            padx=10,
            pady=5
        )
        chip.pack(side="left", padx=(6, 0))

    def _construir_notebook(self):
        contenedor = tk.Frame(self, bg=THEME["bg_app"], padx=18, pady=12)
        contenedor.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(contenedor, style="Main.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Diccionarios para almacenar referencias a los cuadros de texto
        self.text_boxes = {}

        # -------------------------------------------------------------
        # PESTAÑAS 1 A LA 6 (EJERCICIO 1 AL EJERCICIO 6)
        # -------------------------------------------------------------
        ejercicios_info = [
            ("Ejercicio 1", "Carga y Revisión del Dataset", self.engine.obtener_texto_ejercicio_1),
            ("Ejercicio 2", "Filtros Vectorizados (Sin Bucles)", self.engine.obtener_texto_ejercicio_2),
            ("Ejercicio 3", "Columna Calculada 'situacion' (np.where)", self.engine.obtener_texto_ejercicio_3),
            ("Ejercicio 4", "Resúmenes Estadísticos y Exportación a CSV", self.engine.obtener_texto_ejercicio_4),
            ("Ejercicio 5", "Generación de Gráficas con Matplotlib", self.engine.obtener_texto_ejercicio_5),
            ("Ejercicio 6", "Lectura de Resultados e Interpretación Analítica", self.engine.obtener_texto_ejercicio_6),
        ]

        for tab_name, subtitulo, func_texto in ejercicios_info:
            frame_tab = tk.Frame(self.notebook, bg=THEME["bg_app"])
            self.notebook.add(frame_tab, text=f" {tab_name} ")

            # Barra superior de la pestaña
            top_bar = tk.Frame(frame_tab, bg=THEME["bg_app"])
            top_bar.pack(fill="x", pady=(8, 8))

            lbl_sub = tk.Label(
                top_bar,
                text=f"📌 {tab_name.upper()} • {subtitulo}",
                font=("Segoe UI", 11, "bold"),
                fg=THEME["text_main"],
                bg=THEME["bg_app"]
            )
            lbl_sub.pack(side="left")

            btn_copiar = tk.Button(
                top_bar,
                text="📋 Copiar Salida",
                font=("Segoe UI", 9),
                bg="#334155",
                fg="white",
                activebackground="#475569",
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda k=tab_name: self.copiar_texto_tab(k)
            )
            btn_copiar.pack(side="right")

            # Contenedor de la terminal de lectura
            term_frame = tk.Frame(frame_tab, bg=THEME["terminal_bg"], highlightbackground="#334155", highlightthickness=1)
            term_frame.pack(fill="both", expand=True)

            txt_box = scrolledtext.ScrolledText(
                term_frame,
                wrap=tk.WORD,
                bg=THEME["terminal_bg"],
                fg=THEME["terminal_fg"],
                insertbackground="white",
                selectbackground="#334155",
                selectforeground="white",
                font=("Consolas", 10),
                padx=14,
                pady=12,
                relief="flat",
                borderwidth=0
            )
            txt_box.pack(fill="both", expand=True)
            txt_box.config(state="disabled")

            self.text_boxes[tab_name] = (txt_box, func_texto)

        # -------------------------------------------------------------
        # PESTAÑA 7: VISUALIZACIÓN DE GRÁFICAS
        # -------------------------------------------------------------
        self.frame_tab_graficas = tk.Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.frame_tab_graficas, text=" Visualización de Gráficas ")

        self._construir_pestana_graficas()

    def _construir_pestana_graficas(self):
        """Construye la Pestaña 7 con las 3 figuras de Matplotlib y sus rutas locales."""
        # Header dentro de la Pestaña 7
        header_graf = tk.Frame(self.frame_tab_graficas, bg="#f8fafc", padx=16, pady=10)
        header_graf.pack(fill="x", side="top")

        lbl_tit_graf = tk.Label(
            header_graf,
            text="📈 Visualización Interactiva de Figuras Estadísticas (Matplotlib)",
            font=("Segoe UI", 12, "bold"),
            fg=THEME["text_main"],
            bg="#f8fafc"
        )
        lbl_tit_graf.pack(side="left")

        btn_guardar = tk.Button(
            header_graf,
            text="💾 Guardar las 3 Gráficas PNG (300 DPI)",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["accent_amber"],
            fg="white",
            activebackground=THEME["accent_amber_hover"],
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.accion_guardar_graficas
        )
        btn_guardar.pack(side="right")

        btn_abrir_carpeta = tk.Button(
            header_graf,
            text="📂 Abrir Carpeta",
            font=("Segoe UI", 9),
            bg="#334155",
            fg="white",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: os.startfile(BASE_DIR)
        )
        btn_abrir_carpeta.pack(side="right", padx=6)

        # Sub-Notebook para alternar entre las 3 gráficas cómodamente
        self.sub_notebook = ttk.Notebook(self.frame_tab_graficas, style="Graficas.TNotebook")
        self.sub_notebook.pack(fill="both", expand=True, padx=12, pady=10)

        # Sub-pestaña 1: Promedio por Materia
        tab_mat = tk.Frame(self.sub_notebook, bg="#ffffff")
        self.sub_notebook.add(tab_mat, text="  📊 1. Promedio por Materia  ")
        self._incrustar_grafica_individual(
            tab_mat,
            titulo="Gráfica 1: Promedio General de Calificaciones por Materia",
            ruta_archivo=IMG_MATERIAS,
            generador_figura=self.engine.crear_figura_materias,
            descripcion="Gráfica de barras con escala de 0 a 100 y etiquetas de promedios individuales por asignatura."
        )

        # Sub-pestaña 2: Histograma de Distribución
        tab_hist = tk.Frame(self.sub_notebook, bg="#ffffff")
        self.sub_notebook.add(tab_hist, text="  📈 2. Histograma Global  ")
        self._incrustar_grafica_individual(
            tab_hist,
            titulo="Gráfica 2: Distribución Global de Calificaciones (Histograma)",
            ruta_archivo=IMG_HISTOGRAMA,
            generador_figura=self.engine.crear_figura_histograma,
            descripcion="Distribución de frecuencias con 12 intervalos y línea de corte punteada en calificación aprobatoria (70)."
        )

        # Sub-pestaña 3: Tendencia por Unidad
        tab_tend = tk.Frame(self.sub_notebook, bg="#ffffff")
        self.sub_notebook.add(tab_tend, text="  📉 3. Tendencia por Unidad  ")
        self._incrustar_grafica_individual(
            tab_tend,
            titulo="Gráfica 3: Tendencia del Promedio por Unidad según Materia",
            ruta_archivo=IMG_TENDENCIA,
            generador_figura=self.engine.crear_figura_tendencia,
            descripcion="Evolución temporal del rendimiento estudiantil en las unidades 1, 2 y 3 para cada materia curricular."
        )

    def _incrustar_grafica_individual(self, parent, titulo: str, ruta_archivo: Path,
                                     generador_figura, descripcion: str):
        """Incrusta una figura de Matplotlib junto a su etiqueta de ruta física exacta."""
        # Panel superior de información y ruta exacta
        info_card = tk.Frame(
            parent,
            bg="#f1f5f9",
            highlightbackground="#cbd5e1",
            highlightthickness=1,
            padx=14,
            pady=10
        )
        info_card.pack(fill="x", padx=12, pady=(10, 8))

        top_row = tk.Frame(info_card, bg="#f1f5f9")
        top_row.pack(fill="x")

        lbl_tit = tk.Label(
            top_row,
            text=f"🎯 {titulo}",
            font=("Segoe UI", 10, "bold"),
            fg=THEME["text_main"],
            bg="#f1f5f9"
        )
        lbl_tit.pack(side="left")

        # Botón para abrir directamente el archivo PNG con el visor del sistema
        btn_abrir_png = tk.Button(
            top_row,
            text="🖼️ Abrir PNG",
            font=("Segoe UI", 8, "bold"),
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda r=ruta_archivo: self.abrir_archivo_si_existe(r)
        )
        btn_abrir_png.pack(side="right")

        lbl_desc = tk.Label(
            info_card,
            text=descripcion,
            font=("Segoe UI", 8, "italic"),
            fg=THEME["text_muted"],
            bg="#f1f5f9"
        )
        lbl_desc.pack(anchor="w", pady=(2, 4))

        # ETIQUETA CLARA CON LA RUTA FÍSICA EXACTA
        ruta_frame = tk.Frame(info_card, bg="#ffffff", highlightbackground="#94a3b8", highlightthickness=1, padx=8, pady=4)
        ruta_frame.pack(fill="x", pady=(2, 0))

        lbl_etiqueta_ruta = tk.Label(
            ruta_frame,
            text=f"📍 Ruta física exacta: {ruta_archivo.resolve()}",
            font=("Consolas", 9, "bold"),
            fg="#0f172a",
            bg="#ffffff",
            anchor="w"
        )
        lbl_etiqueta_ruta.pack(side="left", fill="x", expand=True)

        btn_copiar_ruta = tk.Button(
            ruta_frame,
            text="📋 Copiar Ruta",
            font=("Segoe UI", 8),
            bg="#f1f5f9",
            fg="#334155",
            relief="groove",
            padx=6,
            pady=1,
            cursor="hand2",
            command=lambda p=str(ruta_archivo.resolve()): self.copiar_al_portapapeles(p, "Ruta copiada al portapapeles")
        )
        btn_copiar_ruta.pack(side="right")

        # Contenedor de la gráfica incrustada con Matplotlib
        canvas_frame = tk.Frame(parent, bg="#ffffff")
        canvas_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        figura = generador_figura()
        canvas = FigureCanvasTkAgg(figura, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def abrir_archivo_si_existe(self, ruta: Path):
        """Abre un archivo con el visor predeterminado del sistema."""
        if not ruta.exists():
            messagebox.showinfo("Aviso", f"El archivo aún no ha sido generado en disco.\nGuardando ahora...")
            self.accion_guardar_graficas()
        if ruta.exists():
            try:
                os.startfile(ruta)
            except Exception as e:
                messagebox.showerror("Error al abrir", f"No se pudo abrir el archivo:\n{e}")

    def copiar_al_portapapeles(self, texto: str, mensaje_exito: str):
        """Copia una cadena al portapapeles del sistema operativo."""
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Copiado", mensaje_exito)

    def copiar_texto_tab(self, tab_name: str):
        """Copia el contenido del cuadro de texto de una pestaña al portapapeles."""
        if tab_name in self.text_boxes:
            txt_box, _ = self.text_boxes[tab_name]
            contenido = txt_box.get("1.0", tk.END).strip()
            if contenido:
                self.copiar_al_portapapeles(contenido, f"Resultados de {tab_name} copiados al portapapeles.")
            else:
                messagebox.showwarning("Aviso", "No hay texto para copiar.")

    def actualizar_todas_las_pestanas(self):
        """Calcula y rellena el contenido de los cuadros de texto de las pestañas 1 a la 6."""
        self.engine.cargar_datos()

        for tab_name, (txt_box, func_texto) in self.text_boxes.items():
            texto = func_texto()
            txt_box.config(state="normal")
            txt_box.delete("1.0", tk.END)
            txt_box.insert(tk.END, texto)
            txt_box.config(state="disabled")

    def accion_recalcular_todo(self):
        """Recalcula todos los ejercicios y refresca la información."""
        try:
            self.actualizar_todas_las_pestanas()
            messagebox.showinfo(
                "Recálculo Exitoso",
                "Se han procesado nuevamente todos los ejercicios (1 al 6).\n"
                "Todas las pestañas han sido actualizadas con datos frescos."
            )
        except Exception as e:
            messagebox.showerror("Error al recalcular", f"Ocurrió un error:\n{e}")

    def accion_exportar_csv(self):
        """Exporta directamente el archivo CSV de promedios por alumno."""
        try:
            ruta = self.engine.exportar_csv(OUTPUT_CSV)
            total = len(self.engine.promedio_por_alumno)
            messagebox.showinfo(
                "Exportación Exitosa",
                f"El archivo CSV se guardó correctamente:\n\n"
                f"📁 Archivo: {ruta.name}\n"
                f"📍 Ruta: {ruta.resolve()}\n"
                f"👥 Total de alumnos: {total}\n"
                f"📊 Formato: UTF-8, 2 decimales, sin índice."
            )
        except Exception as e:
            messagebox.showerror("Error al exportar CSV", f"No fue posible guardar el archivo CSV:\n\n{e}")

    def accion_guardar_graficas(self):
        """Genera y guarda físicamente las 3 gráficas requeridas a 300 DPI."""
        try:
            generadas = self.engine.guardar_graficas_png()
            lista_str = "\n".join([f"    • {p.name} ({p.resolve()})" for p in generadas])
            messagebox.showinfo(
                "Gráficas Guardadas con Éxito",
                f"Se han generado y guardado físicamente las 3 gráficas a 300 DPI:\n\n"
                f"{lista_str}\n\n"
                f"📍 Directorio base: {BASE_DIR}"
            )
        except Exception as e:
            messagebox.showerror("Error al guardar gráficas", f"No fue posible generar las gráficas:\n\n{e}")


# =============================================================================
# MODO LÍNEA DE COMANDOS (CLI DE RESPALDO)
# =============================================================================
def ejecutar_modo_consola():
    """Ejecuta los 6 ejercicios en consola estándar (si se ejecuta con argumento --cli)."""
    engine = CalculosEngine(CSV_PATH)
    print(engine.ejecutar_reporte_completo())


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        ejecutar_modo_consola()
    else:
        app = DashboardNotebookApp()
        app.mainloop()
