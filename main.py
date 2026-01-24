import tkinter as tk
from tkinter import ttk, messagebox

from SJF import simular_sjf
from gantt import dibujar_gantt


class SJFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación SJF Apropiativo")
        self.root.geometry("900x600")

        self.procesos = []

        self.crear_formulario()
        self.crear_tabla()
        self.crear_botones()
        self.crear_resultados()

    # =========================
    # FORMULARIO
    # =========================
    def crear_formulario(self):
        frame = tk.LabelFrame(self.root, text="Ingreso de Proceso")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Proceso").grid(row=0, column=0)
        tk.Label(frame, text="Llegada").grid(row=0, column=1)
        tk.Label(frame, text="Ráfaga").grid(row=0, column=2)
        tk.Label(frame, text="O E/S").grid(row=0, column=3)
        tk.Label(frame, text="Inicio O E/S").grid(row=0, column=4)
        tk.Label(frame, text="Duración").grid(row=0, column=5)

        self.id_entry = tk.Entry(frame, width=8)
        self.llegada_entry = tk.Entry(frame, width=8)
        self.rafaga_entry = tk.Entry(frame, width=8)
        self.io_var = tk.StringVar(value="No")
        self.io_inicio_entry = tk.Entry(frame, width=8)
        self.io_duracion_entry = tk.Entry(frame, width=8)

        self.id_entry.grid(row=1, column=0)
        self.llegada_entry.grid(row=1, column=1)
        self.rafaga_entry.grid(row=1, column=2)
        ttk.Combobox(frame, values=["No", "Sí"], textvariable=self.io_var, width=6).grid(row=1, column=3)
        self.io_inicio_entry.grid(row=1, column=4)
        self.io_duracion_entry.grid(row=1, column=5)

    # =========================
    # TABLA DE PROCESOS
    # =========================
    def crear_tabla(self):
        frame = tk.LabelFrame(self.root, text="Tabla de Procesos")
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
            self.tabla.column(col, anchor="center", width=110)

        self.tabla.pack(fill="x", padx=5, pady=5)

    # =========================
    # BOTONES
    # =========================
    def crear_botones(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Button(frame, text="Agregar Proceso", command=self.agregar_proceso).pack(side="left", padx=5)
        tk.Button(frame, text="Simular SJF", command=self.simular).pack(side="left", padx=5)

    # =========================
    # RESULTADOS
    # =========================
    def crear_resultados(self):
        frame = tk.LabelFrame(self.root, text="Resultados")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.resultado = tk.Text(frame, height=8)
        self.resultado.pack(fill="x", padx=5, pady=5)

        self.cpl_label = tk.Label(frame, text="CPL: | |", font=("Consolas", 11))
        self.cpl_label.pack(anchor="w", padx=5)

        self.io_label = tk.Label(frame, text="O E/S: | |", font=("Consolas", 11))
        self.io_label.pack(anchor="w", padx=5)

        self.frame_gantt = tk.LabelFrame(frame, text="CPU – Diagrama de Gantt")
        self.frame_gantt.pack(fill="both", expand=True, padx=5, pady=5)

    # =========================
    # FUNCIONES
    # =========================
    def agregar_proceso(self):
        try:
            # Validaciones básicas
            if not self.id_entry.get():
                raise ValueError("ID vacío")

            llegada = int(self.llegada_entry.get())
            rafaga = int(self.rafaga_entry.get())

            if llegada < 0 or rafaga <= 0:
                raise ValueError("Valores negativos")

            proceso = {
                "id": self.id_entry.get(),
                "llegada": llegada,
                "rafaga": rafaga,
                "restante": rafaga,
                "io_inicio": None,
                "io_duracion": None,
                "io_retorno": None,
                "ejecutado": 0,
                "fin": None
            }

            # Datos de Entrada / Salida
            if self.io_var.get() == "Sí":
                io_inicio = int(self.io_inicio_entry.get())
                io_duracion = int(self.io_duracion_entry.get())

                if io_inicio <= 0 or io_duracion <= 0 or io_inicio > rafaga:
                    raise ValueError("Datos O E/S inválidos")

                proceso["io_inicio"] = io_inicio
                proceso["io_duracion"] = io_duracion

            # Guardar proceso
            self.procesos.append(proceso)

            # Insertar en tabla
            self.tabla.insert("", "end", values=(
                proceso["id"],
                proceso["llegada"],
                proceso["rafaga"],
                self.io_var.get(),
                proceso["io_inicio"] if proceso["io_inicio"] is not None else "-",
                proceso["io_duracion"] if proceso["io_duracion"] else "-"
            ))

            # Limpiar entradas
            self.id_entry.delete(0, tk.END)
            self.llegada_entry.delete(0, tk.END)
            self.rafaga_entry.delete(0, tk.END)
            self.io_inicio_entry.delete(0, tk.END)
            self.io_duracion_entry.delete(0, tk.END)
            self.io_var.set("No")

        except Exception:
            messagebox.showerror(
                "Error",
                "Verifique los datos:\n"
                "- Llegada ≥ 0\n"
                "- Ráfaga > 0\n"
                "- Inicio O E/S ≤ ráfaga\n"
                "- Duración O E/S > 0"
            )

    def simular(self):
        if not self.procesos:
            messagebox.showwarning("Aviso", "Ingrese procesos primero")
            return

        gantt, cpl_hist, io_hist, procesos = simular_sjf(self.procesos)

        self.resultado.delete(1.0, tk.END)
        self.resultado.insert(tk.END, "RESULTADOS\n\n")

        total_te = 0
        total_teje = 0

        for p in procesos:
            te = p["fin"] - p["rafaga"] - p["llegada"]
            if p["io_duracion"]:
                te -= p["io_duracion"]

            teje = p["fin"] - p["llegada"]

            total_te += te
            total_teje += teje

            self.resultado.insert(
                tk.END, f"{p['id']} → TE={te} | TEje={teje}\n"
            )

        self.resultado.insert(
            tk.END,
            f"\nTEP = {total_te / len(procesos):.2f}"
            f"\nTEjeP = {total_teje / len(procesos):.2f}"
        )

        # 👇 NUEVO: mostrar CPL y O E/S
        self.cpl_label.config(
            text="CPL: | " + " | ".join(cpl_hist) + " |"
        )

        if io_hist:
            self.io_label.config(
                text="O E/S: | " + " | ".join(io_hist) + " |"
            )
        else:
            self.io_label.config(text="O E/S: No hubo operaciones")

        dibujar_gantt(self.frame_gantt, gantt)


# =========================
# EJECUCIÓN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = SJFApp(root)
    root.mainloop()
