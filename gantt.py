from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================
# DIAGRAMA DE GANTT CPU
# =========================
def dibujar_gantt(frame, gantt):
    for widget in frame.winfo_children():
        widget.destroy()

    if not gantt:
        return

    fig = Figure(figsize=(8, 2.5))
    ax = fig.add_subplot(111)

    inicio = 0
    proceso_actual = gantt[0]
    marcas = [0]

    for t in range(1, len(gantt) + 1):
        if t == len(gantt) or gantt[t] != proceso_actual:
            duracion = t - inicio

            if proceso_actual != "—":
                ax.barh(0, duracion, left=inicio, height=0.5)
                ax.text(
                    inicio + duracion / 2,
                    0,
                    proceso_actual,
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold"
                )

            marcas.append(t)
            inicio = t
            if t < len(gantt):
                proceso_actual = gantt[t]

    ax.set_yticks([])
    ax.set_xticks(marcas)
    ax.set_xlabel("Tiempo (ms)")
    ax.set_title("CPU – Diagrama de Gantt")
    ax.grid(axis="x")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# =========================
# CPL (LISTA DE LISTOS)
# =========================
def dibujar_cpl(frame, lista):
    for widget in frame.winfo_children():
        widget.destroy()

    if not lista:
        return

    # Eliminar duplicados manteniendo orden
    vistos = []
    for p in lista:
        if p not in vistos:
            vistos.append(p)

    fig = Figure(figsize=(6, 1.5))
    ax = fig.add_subplot(111)

    for i, pid in enumerate(vistos):
        ax.barh(0, 1, left=i, height=0.5)
        ax.text(
            i + 0.5,
            0,
            pid,
            ha="center",
            va="center",
            color="white",
            fontweight="bold"
        )

    ax.set_xlim(0, len(vistos))
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("CPL (Cola de Listos)")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# =========================
# O E/S (ENTRADA / SALIDA)
# =========================
def dibujar_oes(frame, lista):
    for widget in frame.winfo_children():
        widget.destroy()

    if not lista:
        return

    procesos = []

    # Extraer solo procesos con O E/S
    for item in lista:
        if "(" in item:
            pid, tiempo = item.replace(")", "").split("(")
            procesos.append((pid, int(tiempo)))

    if not procesos:
        return

    fig = Figure(figsize=(6, 1.8))
    ax = fig.add_subplot(111)

    for i, (pid, tiempo) in enumerate(procesos):
        # Bloque del proceso
        ax.barh(0, 1, left=i, height=0.5)

        # ID del proceso
        ax.text(
            i + 0.5,
            0,
            pid,
            ha="center",
            va="center",
            color="white",
            fontweight="bold"
        )

        # Milisegundo de retorno
        ax.text(
            i + 0.5,
            -0.6,
            str(tiempo),
            ha="center",
            va="center",
            fontsize=9
        )

    ax.set_xlim(0, len(procesos))
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("O E/S (retorno a CPL)")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
