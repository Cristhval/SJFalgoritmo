from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================
# CPU – DIAGRAMA DE GANTT
# =========================
def dibujar_gantt(frame, gantt):
    for widget in frame.winfo_children():
        widget.destroy()

    if not gantt:
        return

    fig = Figure(figsize=(8, 2.5))
    ax = fig.add_subplot(111)

    inicio = 0
    actual = gantt[0]
    marcas = [0]

    for t in range(1, len(gantt) + 1):
        if t == len(gantt) or gantt[t] != actual:
            dur = t - inicio

            if actual != "—":
                ax.barh(0, dur, left=inicio, height=0.45)
                ax.text(
                    inicio + dur / 2,
                    0,
                    actual,
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                    fontsize=9
                )

            marcas.append(t)
            inicio = t
            if t < len(gantt):
                actual = gantt[t]

    ax.set_yticks([])
    ax.set_xticks(marcas)
    ax.set_xlabel("Tiempo (ms)")
    ax.set_title("CPU – Diagrama de Gantt")
    ax.grid(axis="x")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# =========================
# CPL – COLA DE LISTOS (HISTÓRICA)
# =========================
def dibujar_cpl(frame, lista):
    for widget in frame.winfo_children():
        widget.destroy()

    if not lista:
        return

    fig = Figure(figsize=(8, 1.5))
    ax = fig.add_subplot(111)

    for i, pid in enumerate(lista):
        ax.barh(0, 1, left=i, height=0.45)
        ax.text(
            i + 0.5,
            0,
            pid,
            ha="center",
            va="center",
            color="white",
            fontweight="bold",
            fontsize=9
        )

    ax.set_xlim(0, len(lista))
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("CPL – Cola de Procesos Listos")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="x", expand=True)


# =========================
# O E/S – ENTRADA / SALIDA
# =========================
def dibujar_oes(frame, lista):
    for widget in frame.winfo_children():
        widget.destroy()

    if not lista:
        return

    procesos = []
    for item in lista:
        if "(" in item and ")" in item:
            pid, tiempo = item.replace(")", "").split("(")
            procesos.append((pid, int(tiempo)))

    if not procesos:
        return

    fig = Figure(figsize=(6, 1.8))
    ax = fig.add_subplot(111)

    for i, (pid, tiempo) in enumerate(procesos):
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
    ax.set_title("O E/S – Retorno a CPL (ms)")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
