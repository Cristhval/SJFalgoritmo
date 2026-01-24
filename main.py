import tkinter as tk
from tkinter import ttk, messagebox

from SJF import simular_sjf
from gantt import dibujar_gantt, dibujar_cpl, dibujar_oes


class SJFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación SJF Apropiativo")
        self.root.geometry("1000x700")

        # ===== CONTENEDOR CON SCROLL =====
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Scroll con rueda del mouse
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        # =================================
        self.procesos = []

        self.crear_formulario()
        self.crear_tabla()
        self.crear_botones()
        self.crear_resultados()

    # =========================
    # FORMULARIO
    # =========================
    def crear_formulario(self):
        frame = tk.LabelFrame(self.scrollable_frame, text="Ingreso de Proceso")
        frame.pack(fill="x", padx=10, pady=5)

        labels = ["Proceso", "Llegada", "Ráfaga", "O E/S", "Inicio O E/S", "Duración"]
        for i, texto in enumerate(labels):
            tk.Label(frame, text=texto).grid(row=0, column=i, padx=3)

        self.id_entry = tk.Entry(frame, width=8)
        self.llegada_entry = tk.Entry(frame, width=8)
        self.rafaga_entry = tk.Entry(frame, width=8)
        self.io_var = tk.StringVar(value="No")
        self.io_inicio_entry = tk.Entry(frame, width=8)
        self.io_duracion_entry = tk.Entry(frame, width=8)

        self.id_entry.grid(row=1, column=0)
        self.llegada_entry.grid(row=1, column=1)
        self.rafaga_entry.grid(row=1, column=2)

        ttk.Combobox(
            frame,
            values=["No", "Sí"],
            textvariable=self.io_var,
            width=6,
            state="readonly"
        ).grid(row=1, column=3)

        self.io_inicio_entry.grid(row=1, column=4)
        self.io_duracion_entry.grid(row=1, column=5)

    # =========================
    # TABLA
    # =========================
    def crear_tabla(self):
        frame = tk.LabelFrame(self.scrollable_frame, text="Tabla de Procesos")
        frame.pack(fill="x", padx=10, pady=5)

        self.tabla = ttk.Treeview(
            frame,
            columns=("id", "llegada", "rafaga", "io", "io_inicio", "dur"),
            show="headings",
            height=6
        )

        columnas = {
            "id": "Proceso",
            "llegada": "Llegada",
            "rafaga": "Ráfaga CPU",
            "io": "O E/S",
            "io_inicio": "Inicio O E/S",
            "dur": "Duración O E/S"
        }

        for col, texto in columnas.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, anchor="center", width=120)

        self.tabla.pack(fill="x", padx=5, pady=5)

    # =========================
    # BOTONES
    # =========================
    def crear_botones(self):
        frame = tk.Frame(self.scrollable_frame)
        frame.pack(pady=5)

        tk.Button(frame, text="Agregar Proceso", command=self.agregar_proceso).pack(side="left", padx=5)
        tk.Button(frame, text="Simular SJF", command=self.simular).pack(side="left", padx=5)
        tk.Button(
            frame,
            text="Nuevo Ejercicio",
            command=self.limpiar_todo,
            bg="#c0392b",
            fg="white"
        ).pack(side="left", padx=5)

    # =========================
    # RESULTADOS
    # =========================
    def crear_resultados(self):
        frame = tk.LabelFrame(self.scrollable_frame, text="Resultados")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.resultado = tk.Text(frame, height=8)
        self.resultado.pack(fill="x", padx=5, pady=5)

        self.frame_cpl = tk.LabelFrame(frame, text="CPL – Cola de Procesos Listos")
        self.frame_cpl.pack(fill="x", padx=5, pady=5)

        self.frame_io = tk.LabelFrame(frame, text="O E/S – Entrada / Salida")
        self.frame_io.pack(fill="x", padx=5, pady=5)

        self.frame_gantt = tk.LabelFrame(frame, text="CPU – Diagrama de Gantt")
        self.frame_gantt.pack(fill="both", expand=True, padx=5, pady=5)

    # =========================
    # AGREGAR PROCESO
    # =========================
    def agregar_proceso(self):
        try:
            proceso = {
                "id": self.id_entry.get(),
                "llegada": int(self.llegada_entry.get()),
                "rafaga": int(self.rafaga_entry.get()),
                "restante": int(self.rafaga_entry.get()),
                "io_inicio": None,
                "io_duracion": None,
                "io_retorno": None,
                "ejecutado": 0,
                "fin": None
            }

            if self.io_var.get() == "Sí":
                proceso["io_inicio"] = int(self.io_inicio_entry.get())
                proceso["io_duracion"] = int(self.io_duracion_entry.get())

            self.procesos.append(proceso)

            self.tabla.insert("", "end", values=(
                proceso["id"],
                proceso["llegada"],
                proceso["rafaga"],
                self.io_var.get(),
                proceso["io_inicio"] if proceso["io_inicio"] is not None else "-",
                proceso["io_duracion"] if proceso["io_duracion"] is not None else "-"
            ))

            for e in (
                self.id_entry, self.llegada_entry, self.rafaga_entry,
                self.io_inicio_entry, self.io_duracion_entry
            ):
                e.delete(0, tk.END)

            self.io_var.set("No")

        except:
            messagebox.showerror("Error", "Datos inválidos")

    # =========================
    # SIMULACIÓN
    # =========================
    def simular(self):
        if not self.procesos:
            messagebox.showwarning("Aviso", "Ingrese procesos primero")
            return

        gantt, cpl_hist, io_hist, procesos = simular_sjf(self.procesos)

        # =========================
        # MOSTRAR RESULTADOS
        # =========================
        self.resultado.delete(1.0, tk.END)

        total_te = 0
        total_teje = 0

        self.resultado.insert(
            tk.END,
            "Proceso | Llegada | Ráfaga | Fin | TEP | TEjeP\n"
        )
        self.resultado.insert(
            tk.END,
            "-" * 45 + "\n"
        )

        for p in procesos:
            te = p["fin"] - p["rafaga"] - p["llegada"]
            if p["io_duracion"]:
                te -= p["io_duracion"]

            teje = p["fin"] - p["llegada"]

            total_te += te
            total_teje += teje

            self.resultado.insert(
                tk.END,
                f"{p['id']:7} | {p['llegada']:7} | {p['rafaga']:6} | "
                f"{p['fin']:3} | {te:2} | {teje:4}\n"
            )

        self.resultado.insert(tk.END, "\n")
        self.resultado.insert(
            tk.END,
            f"TEP   = {total_te / len(procesos):.2f} ms\n"
        )
        self.resultado.insert(
            tk.END,
            f"TEjeP = {total_teje / len(procesos):.2f} ms\n"
        )

        # =========================
        # DIBUJOS
        # =========================
        dibujar_cpl(self.frame_cpl, cpl_hist)
        dibujar_oes(self.frame_io, io_hist)
        dibujar_gantt(self.frame_gantt, gantt)

    # =========================
    # LIMPIAR
    # =========================
    def limpiar_todo(self):
        self.procesos.clear()
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for frame in (self.frame_cpl, self.frame_io, self.frame_gantt):
            for widget in frame.winfo_children():
                widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SJFApp(root)
    root.mainloop()
