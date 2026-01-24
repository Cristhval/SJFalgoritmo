from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def dibujar_gantt(frame, gantt):
    # limpiar frame
    for widget in frame.winfo_children():
        widget.destroy()

    fig = Figure(figsize=(10, 3))
    ax = fig.add_subplot(111)

    inicio = 0
    proceso_actual = gantt[0]
    marcas = [0]

    for t in range(1, len(gantt) + 1):
        if t == len(gantt) or gantt[t] != proceso_actual:
            duracion = t - inicio

            if proceso_actual != "—":
                ax.barh(
                    y=0,
                    width=duracion,
                    left=inicio,
                    height=0.4
                )
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
    ax.set_title("Diagrama de Gantt – CPU (SJF Apropiativo)")
    ax.grid(axis="x")

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
