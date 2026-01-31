from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def limpiar(frame):
    """Elimina todos los widgets de un frame"""
    for widget in frame.winfo_children():
        widget.destroy()


def obtener_ancho_frame(frame):
    """Obtiene el ancho actual del frame en pulgadas para matplotlib"""
    frame.update_idletasks()
    width_pixels = frame.winfo_width()
    # Convertir pixels a pulgadas (asumiendo 100 DPI)
    # Si el frame aún no tiene tamaño, usar un valor por defecto
    if width_pixels <= 1:
        return 10
    return max(width_pixels / 100, 8)  # Mínimo 8 pulgadas


# =========================
# CPU – DIAGRAMA DE GANTT
# =========================
def dibujar_gantt(frame, gantt):
    limpiar(frame)

    if not gantt:
        return

    # 🔧 FIX: Ancho dinámico basado en el frame
    fig_width = obtener_ancho_frame(frame)
    fig = Figure(figsize=(fig_width, 2.5), dpi=100)
    ax = fig.add_subplot(111)

    # Colores más atractivos para los procesos
    colores = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
               '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']
    proceso_color = {}
    color_idx = 0

    inicio = 0
    actual = gantt[0]
    marcas = [0]

    for t in range(1, len(gantt) + 1):
        if t == len(gantt) or gantt[t] != actual:
            dur = t - inicio
            if actual != "—":
                # Asignar color único a cada proceso
                if actual not in proceso_color:
                    proceso_color[actual] = colores[color_idx % len(colores)]
                    color_idx += 1

                ax.barh(0, dur, left=inicio, height=0.5,
                        color=proceso_color[actual],
                        edgecolor='white', linewidth=2)
                ax.text(
                    inicio + dur / 2,
                    0,
                    actual,
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                    fontsize=11
                )
            else:
                # CPU inactiva con color gris claro
                ax.barh(0, dur, left=inicio, height=0.5,
                        color='#ecf0f1', edgecolor='#bdc3c7',
                        linewidth=1, linestyle='--')

            marcas.append(t)
            inicio = t
            if t < len(gantt):
                actual = gantt[t]

    ax.set_yticks([])
    ax.set_xticks(marcas)
    ax.set_xticklabels(marcas, fontsize=9)
    ax.set_xlabel("Tiempo (ms)", fontsize=10, fontweight='bold')
    ax.set_title("CPU – Diagrama de Gantt", fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.set_xlim(0, len(gantt))

    # Ajustar márgenes
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    # 🔧 FIX: Pack con fill y expand para que se adapte
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


# =========================
# CPL – COLA DE LISTOS
# =========================
def dibujar_cpl(frame, lista):
    limpiar(frame)

    if not lista:
        # Mostrar mensaje si no hay datos
        try:
            import tkinter as tk
            mensaje = tk.Label(
                frame,
                text="No hay procesos en la cola de listos aún",
                font=("Arial", 10, "italic"),
                fg='#7f8c8d',
                bg='white'
            )
            mensaje.pack(pady=20)
        except:
            pass
        return

    # 🔧 FIX: NO eliminar duplicados - queremos ver todas las veces que un proceso entra a CPL
    # Esto incluye cuando retornan de E/S
    cpl = lista.copy()

    if not cpl:
        return

    # 🔧 FIX: Ancho dinámico
    fig_width = obtener_ancho_frame(frame)
    # Altura dinámica según cantidad de procesos
    fig_height = min(3.0, max(1.8, len(cpl) * 0.15))
    fig = Figure(figsize=(fig_width, fig_height), dpi=100)
    ax = fig.add_subplot(111)

    # Colores por proceso (no por posición)
    colores_proceso = {}
    colores_base = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
                    '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']

    # Asignar color único a cada proceso
    procesos_unicos = []
    for p in cpl:
        if p not in procesos_unicos:
            procesos_unicos.append(p)
            colores_proceso[p] = colores_base[len(procesos_unicos) - 1 % len(colores_base)]

    # 🔧 FIX: Calcular ancho de barras dinámicamente
    num_items = len(cpl)
    ancho_barra = min(1.0, fig_width / (num_items * 1.2))

    # Contar apariciones para detectar retornos de E/S
    contador = {}
    for i, pid in enumerate(cpl):
        contador[pid] = contador.get(pid, 0) + 1
        aparicion = contador[pid]

        color = colores_proceso[pid]

        # Si es una reaparición (retorno de E/S), usar borde más grueso
        if aparicion > 1:
            edgecolor = '#e74c3c'  # Rojo para indicar retorno de E/S
            linewidth = 3
        else:
            edgecolor = 'white'
            linewidth = 2

        ax.barh(0, ancho_barra, left=i * ancho_barra, height=0.5,
                color=color, edgecolor=edgecolor, linewidth=linewidth)

        # Nombre del proceso
        ax.text(
            i * ancho_barra + ancho_barra / 2,
            0,
            pid,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            fontsize=10
        )

        # Indicar si es retorno de E/S
        if aparicion > 1:
            ax.text(
                i * ancho_barra + ancho_barra / 2,
                0.35,
                "↩",  # Flecha de retorno
                ha="center",
                va="center",
                fontsize=9,
                color='#e74c3c',
                fontweight='bold'
            )

        # Agregar número de orden debajo
        ax.text(
            i * ancho_barra + ancho_barra / 2,
            -0.4,
            str(i + 1),
            ha="center",
            va="center",
            fontsize=8,
            color='#7f8c8d'
        )

    ax.set_xlim(-0.2, num_items * ancho_barra + 0.2)
    ax.set_ylim(-0.8, 0.8)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("CPL – Historial Completo de Cola de Listos (↩ = retorno de E/S)",
                 fontsize=11, fontweight='bold', pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    # 🔧 FIX: Pack con fill y expand
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


# =========================
# O E/S – ENTRADA / SALIDA
# =========================
def dibujar_oes(frame, lista):
    limpiar(frame)

    if not lista:
        # Mostrar mensaje si no hay datos
        try:
            import tkinter as tk
            mensaje = tk.Label(
                frame,
                text="No hay operaciones de E/S en este ejercicio",
                font=("Arial", 10, "italic"),
                fg='#7f8c8d',
                bg='white'
            )
            mensaje.pack(pady=20)
        except:
            pass
        return

    procesos = []
    vistos = set()

    for item in lista:
        if "(" in item and ")" in item:
            try:
                pid, tiempo = item.replace(")", "").split("(")
                if pid not in vistos:
                    procesos.append((pid, int(tiempo)))
                    vistos.add(pid)
            except:
                continue

    if not procesos:
        return

    # 🔧 FIX: Ancho dinámico
    fig_width = obtener_ancho_frame(frame)
    fig = Figure(figsize=(fig_width, 2.2), dpi=100)
    ax = fig.add_subplot(111)

    # Color para E/S
    color_io = '#e67e22'

    # 🔧 FIX: Calcular ancho de barras dinámicamente
    num_procesos = len(procesos)
    ancho_barra = min(1.0, fig_width / (num_procesos * 1.5))

    for i, (pid, tiempo) in enumerate(procesos):
        ax.barh(0, ancho_barra, left=i * ancho_barra, height=0.5, color=color_io,
                edgecolor='white', linewidth=2)

        # Nombre del proceso
        ax.text(
            i * ancho_barra + ancho_barra / 2,
            0,
            pid,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            fontsize=11
        )

        # Tiempo de retorno
        ax.text(
            i * ancho_barra + ancho_barra / 2,
            -0.55,
            f"{tiempo} ms",
            ha="center",
            va="center",
            fontsize=10,
            fontweight='bold',
            color='#2c3e50'
        )

        # Etiqueta "retorna en:"
        ax.text(
            i * ancho_barra + ancho_barra / 2,
            -0.85,
            "retorna en:",
            ha="center",
            va="center",
            fontsize=8,
            color='#7f8c8d',
            style='italic'
        )

    ax.set_xlim(-0.2, num_procesos * ancho_barra + 0.2)
    ax.set_ylim(-1.2, 0.8)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("O E/S – Procesos en Entrada/Salida",
                 fontsize=11, fontweight='bold', pad=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    # 🔧 FIX: Pack con fill y expand
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


# Importar tkinter para los mensajes
try:
    import tkinter as tk
except:
    pass