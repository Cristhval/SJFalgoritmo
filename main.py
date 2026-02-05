import tkinter as tk
from tkinter import ttk, messagebox
from SJF import simular_sjf
from gantt import dibujar_gantt, dibujar_cpl, dibujar_oes


class SJFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador SJF Apropiativo - Planificación de Procesos")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)  # Tamaño mínimo

        # Configurar colores modernos
        self.color_bg = "#ecf0f1"
        self.color_frame = "#ffffff"
        self.color_btn = "#3498db"
        self.color_btn_hover = "#2980b9"
        self.color_danger = "#e74c3c"

        self.root.configure(bg=self.color_bg)

        # Configurar grid para que sea responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Estilo personalizado
        self.configurar_estilos()

        # ===== CONTENEDOR PRINCIPAL CON GRID =====
        main_container = tk.Frame(root, bg=self.color_bg)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Canvas con scrollbar
        self.canvas = tk.Canvas(main_container, bg=self.color_bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=self.color_bg)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        #  FIX: Hacer que el canvas se expanda horizontalmente
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Scroll con rueda del mouse
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        # =================================
        self.procesos = []

        self.crear_encabezado()
        self.crear_formulario()
        self.crear_tabla()
        self.crear_botones()
        self.crear_resultados()

    def on_canvas_configure(self, event):
        """Ajustar el ancho del frame interno al ancho del canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def configurar_estilos(self):
        """Configurar estilos personalizados para los widgets"""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para LabelFrame
        style.configure('Custom.TLabelframe', background=self.color_frame,
                        borderwidth=2, relief='solid')
        style.configure('Custom.TLabelframe.Label', font=('Arial', 10, 'bold'),
                        background=self.color_frame, foreground='#2c3e50')

        # Estilo para Treeview
        style.configure('Treeview', rowheight=28, font=('Arial', 9))
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'),
                        background='#34495e', foreground='white')
        style.map('Treeview', background=[('selected', '#3498db')])

    def crear_encabezado(self):
        """Crear encabezado con título principal"""
        header_frame = tk.Frame(self.scrollable_frame, bg='#2c3e50')
        header_frame.pack(fill="x", padx=0, pady=0)

        titulo = tk.Label(
            header_frame,
            text="🖥️ SIMULADOR SJF APROPIATIVO",
            font=("Arial", 20, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        titulo.pack(pady=15)

        subtitulo = tk.Label(
            header_frame,
            text="Shortest Job First - Planificación de Procesos con Operaciones E/S",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitulo.pack(pady=(0, 10))

    # =========================
    # FORMULARIO RESPONSIVE
    # =========================
    def crear_formulario(self):
        frame_container = tk.Frame(self.scrollable_frame, bg=self.color_bg)
        frame_container.pack(fill="x", padx=15, pady=(15, 5))

        frame = tk.LabelFrame(
            frame_container,
            text="  📝 Ingreso de Proceso  ",
            font=("Arial", 11, "bold"),
            bg=self.color_frame,
            fg='#2c3e50',
            padx=15,
            pady=15
        )
        frame.pack(fill="x")

        #  FIX: Usar grid con columnas que se expanden
        frame.grid_columnconfigure(0, weight=1)

        # Frame principal para organizar inputs
        inputs_frame = tk.Frame(frame, bg=self.color_frame)
        inputs_frame.pack(fill="x", expand=True)

        # Configurar grid para que sea responsive
        for i in range(5):
            inputs_frame.grid_columnconfigure(i, weight=1, uniform="inputs")

        labels = ["Proceso", "Llegada (ms)", "Ráfaga (ms)",
                  "Inicio E/S (ms)", "Duración E/S (ms)"]

        # Etiquetas
        for i, texto in enumerate(labels):
            label = tk.Label(
                inputs_frame,
                text=texto,
                font=("Arial", 9, "bold"),
                bg=self.color_frame,
                fg='#34495e'
            )
            label.grid(row=0, column=i, padx=5, pady=(0, 5), sticky="ew")

        # Estilo para entries
        entry_config = {
            'font': ('Arial', 10),
            'relief': 'solid',
            'borderwidth': 1,
            'justify': 'center'
        }



        validar_num = self.root.register(self.validar_solo_numeros)
        self.id_entry = tk.Entry(
            inputs_frame,
            validate="key",
            validatecommand=(validar_num, "%P"),
            **entry_config
        )
        self.llegada_entry = tk.Entry(inputs_frame, **entry_config)
        self.rafaga_entry = tk.Entry(inputs_frame, **entry_config)
        self.io_inicio_entry = tk.Entry(inputs_frame, **entry_config)
        self.io_duracion_entry = tk.Entry(inputs_frame, **entry_config)

        # Colocar entries en grid
        self.id_entry.grid(row=1, column=0, padx=5, sticky="ew")
        self.llegada_entry.grid(row=1, column=1, padx=5, sticky="ew")
        self.rafaga_entry.grid(row=1, column=2, padx=5, sticky="ew")

        self.io_inicio_entry.grid(row=1, column=3, padx=5, sticky="ew")
        self.io_duracion_entry.grid(row=1, column=4, padx=5, sticky="ew")

        # Botón agregar dentro del formulario
        btn_agregar = tk.Button(
            frame,
            text="➕ Agregar Proceso",
            command=self.agregar_proceso,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=8
        )
        btn_agregar.pack(pady=(15, 5))

        # Efectos hover
        btn_agregar.bind('<Enter>', lambda e: e.widget.config(bg='#229954'))
        btn_agregar.bind('<Leave>', lambda e: e.widget.config(bg='#27ae60'))

    # =========================
    # TABLA RESPONSIVE
    # =========================
    def crear_tabla(self):
        frame_container = tk.Frame(self.scrollable_frame, bg=self.color_bg)
        frame_container.pack(fill="both", expand=True, padx=15, pady=5)

        frame = tk.LabelFrame(
            frame_container,
            text="  📋 Tabla de Procesos Ingresados  ",
            font=("Arial", 11, "bold"),
            bg=self.color_frame,
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        frame.pack(fill="both", expand=True)

        # Frame para la tabla con scrollbar
        tabla_frame = tk.Frame(frame, bg=self.color_frame)
        tabla_frame.pack(fill="both", expand=True)

        #  FIX: Hacer que la tabla se expanda
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=("id", "llegada", "rafaga", "io_inicio", "dur"),
            show="headings",
            height=8
        )

        # Scrollbars
        tabla_scroll_y = ttk.Scrollbar(tabla_frame, orient="vertical",
                                       command=self.tabla.yview)
        tabla_scroll_x = ttk.Scrollbar(tabla_frame, orient="horizontal",
                                       command=self.tabla.xview)

        self.tabla.configure(
            yscrollcommand=tabla_scroll_y.set,
            xscrollcommand=tabla_scroll_x.set
        )

        columnas = {
            "id": "Proceso",
            "llegada": "Llegada (ms)",
            "rafaga": "Ráfaga CPU (ms)",
            "io_inicio": "Inicio E/S (ms)",
            "dur": "Duración E/S (ms)"
        }

        for col, texto in columnas.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, anchor="center", minwidth=100, stretch=True)

        # Grid layout para tabla
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        tabla_scroll_y.grid(row=0, column=1, sticky="ns")
        tabla_scroll_x.grid(row=1, column=0, sticky="ew", padx=(5, 0))

        # Etiqueta de contador
        self.label_contador = tk.Label(
            frame,
            text="Total de procesos: 0",
            font=("Arial", 9, "italic"),
            bg=self.color_frame,
            fg='#7f8c8d'
        )
        self.label_contador.pack(pady=(5, 0))

    # =========================
    # BOTONES
    # =========================
    def crear_botones(self):
        frame = tk.Frame(self.scrollable_frame, bg=self.color_bg)
        frame.pack(pady=15)

        # Botón Simular
        self.btn_simular = tk.Button(
            frame,
            text="▶️ Simular SJF",
            command=self.simular,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12,
            width=20
        )
        self.btn_simular.pack(side="left", padx=10)

        # Efectos hover
        self.btn_simular.bind('<Enter>', lambda e: e.widget.config(bg='#2980b9'))
        self.btn_simular.bind('<Leave>', lambda e: e.widget.config(bg='#3498db'))

        # Botón Limpiar
        btn_limpiar = tk.Button(
            frame,
            text="🗑️ Nuevo Ejercicio",
            command=self.limpiar_todo,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12,
            width=20
        )
        btn_limpiar.pack(side="left", padx=10)

        # Efectos hover
        btn_limpiar.bind('<Enter>', lambda e: e.widget.config(bg='#c0392b'))
        btn_limpiar.bind('<Leave>', lambda e: e.widget.config(bg='#e74c3c'))

    # =========================
    # RESULTADOS RESPONSIVE
    # =========================
    def crear_resultados(self):
        frame_container = tk.Frame(self.scrollable_frame, bg=self.color_bg)
        frame_container.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        frame = tk.LabelFrame(
            frame_container,
            text="  📊 Resultados de la Simulación  ",
            font=("Arial", 12, "bold"),
            bg=self.color_frame,
            fg='#2c3e50',
            padx=10,
            pady=10
        )
        frame.pack(fill="both", expand=True)

        # Frame para resultados numéricos
        resultado_frame = tk.Frame(frame, bg=self.color_frame)
        resultado_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.resultado = tk.Text(
            resultado_frame,
            height=10,
            font=("Courier New", 10),
            bg='#f8f9fa',
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=10,
            wrap=tk.WORD  # 🔧 FIX: Wrap de texto
        )
        self.resultado.pack(fill="both", expand=True)

        # Separador visual
        separator1 = ttk.Separator(frame, orient='horizontal')
        separator1.pack(fill='x', padx=5, pady=15)

        # Frame para CPL
        self.frame_cpl = tk.LabelFrame(
            frame,
            text="  🔄 CPL – Cola de Procesos Listos  ",
            font=("Arial", 11, "bold"),
            bg=self.color_frame,
            fg='#2c3e50',
            padx=5,
            pady=5
        )
        self.frame_cpl.pack(fill="both", expand=True, padx=5, pady=5)

        # Separador
        separator2 = ttk.Separator(frame, orient='horizontal')
        separator2.pack(fill='x', padx=5, pady=15)

        # Frame para O E/S
        self.frame_io = tk.LabelFrame(
            frame,
            text="  💾 O E/S – Operaciones de Entrada/Salida  ",
            font=("Arial", 11, "bold"),
            bg=self.color_frame,
            fg='#2c3e50',
            padx=5,
            pady=5
        )
        self.frame_io.pack(fill="both", expand=True, padx=5, pady=5)

        # Separador
        separator3 = ttk.Separator(frame, orient='horizontal')
        separator3.pack(fill='x', padx=5, pady=15)

        # Frame para Gantt
        self.frame_gantt = tk.LabelFrame(
            frame,
            text="  📈 CPU – Diagrama de Gantt  ",
            font=("Arial", 11, "bold"),
            bg=self.color_frame,
            fg='#2c3e50',
            padx=5,
            pady=5
        )
        self.frame_gantt.pack(fill="both", expand=True, padx=5, pady=5)

    # =========================
    # AGREGAR PROCESO
    # =========================
    def agregar_proceso(self):
        try:
            # Validar que los campos necesarios no estén vacíos
            if not self.id_entry.get().strip():
                messagebox.showwarning("⚠️ Campo vacío",
                                       "Por favor ingrese el nombre del proceso")
                self.id_entry.focus()
                return

            if not self.llegada_entry.get().strip():
                messagebox.showwarning("⚠️ Campo vacío",
                                       "Por favor ingrese el tiempo de llegada")
                self.llegada_entry.focus()
                return
            if not self.id_entry.get().strip().isdigit():
                messagebox.showerror(
                    "❌ Error",
                    "El identificador del proceso debe ser numérico"
                )
                self.id_entry.focus()
                return

            if not self.rafaga_entry.get().strip():
                messagebox.showwarning("⚠️ Campo vacío",
                                       "Por favor ingrese la ráfaga de CPU")
                self.rafaga_entry.focus()
                return

            llegada = int(self.llegada_entry.get())
            rafaga = int(self.rafaga_entry.get())

            # Validar valores positivos
            if llegada < 0 or rafaga <= 0:
                messagebox.showerror("❌ Error",
                                     "Los tiempos deben ser valores positivos\n" +
                                     "La ráfaga debe ser mayor a 0")
                return

            proceso_id = f"P{self.id_entry.get().strip()}"
            if any(p["id"] == proceso_id for p in self.procesos):
                messagebox.showerror(
                    "❌ Error",
                    f"El proceso '{proceso_id}' ya existe y no se puede duplicar"
                )
                self.id_entry.focus()
                return
            proceso = {
                "id": proceso_id,
                "llegada": llegada,
                "rafaga": rafaga,
                "restante": rafaga,
                "io": [],  #  lista de E/S
                "io_actual": 0,  #  índice de E/S actual
                "io_retorno": None,
                "ejecutado": 0,
                "fin": None
            }

            io_inicio_txt = self.io_inicio_entry.get().strip()
            io_duracion_txt = self.io_duracion_entry.get().strip()

            if io_inicio_txt or io_duracion_txt:
                inicios = io_inicio_txt.split()
                duraciones = io_duracion_txt.split()

                if len(inicios) != len(duraciones):
                    messagebox.showerror(
                        "❌ Error",
                        "La cantidad de inicios y duraciones de E/S no coincide"
                    )
                    return

                if len(inicios) > 3:
                    messagebox.showerror(
                        "❌ Error",
                        "Un proceso puede tener como máximo 3 operaciones de E/S"
                    )
                    return

                io_list = []

                for i, d in zip(inicios, duraciones):
                    inicio = int(i)
                    dur = int(d)

                    if inicio < 0 or dur <= 0:
                        messagebox.showerror(
                            "❌ Error",
                            "Los tiempos de E/S deben ser positivos"
                        )
                        return

                    if inicio >= rafaga:
                        messagebox.showerror(
                            "❌ Error",
                            "El inicio de E/S debe ser menor que la ráfaga"
                        )
                        return

                    io_list.append({
                        "inicio": inicio,
                        "duracion": dur
                    })

                # Ordenar por inicio (seguridad)
                io_list.sort(key=lambda x: x["inicio"])

                proceso["io"] = io_list

            self.procesos.append(proceso)

            self.tabla.insert("", "end", values=(
                proceso_id,
                proceso["llegada"],
                proceso["rafaga"],
                " ".join(str(io["inicio"]) for io in proceso["io"]) or "-",
                " ".join(str(io["duracion"]) for io in proceso["io"]) or "-"
            ))

            # Actualizar contador
            self.label_contador.config(
                text=f"Total de procesos: {len(self.procesos)}"
            )

            # Limpiar campos
            for e in (
                    self.id_entry, self.llegada_entry, self.rafaga_entry,
                    self.io_inicio_entry, self.io_duracion_entry
            ):
                e.delete(0, tk.END)

            self.id_entry.focus()

            # Mensaje de éxito
            messagebox.showinfo("✅ Éxito",
                                f"Proceso '{proceso_id}' agregado correctamente")

        except ValueError:
            messagebox.showerror("❌ Error",
                                 "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al agregar proceso:\n{str(e)}")

    def validar_solo_numeros(self, valor):
        return valor.isdigit() or valor == ""

    # =========================
    # SIMULACIÓN
    # =========================
    def simular(self):
        self.btn_simular.config(state="disabled")

        if not self.procesos:
            messagebox.showwarning("⚠️ Aviso",
                                   "Debe ingresar al menos un proceso antes de simular")
            return

        try:
            gantt, cpl_hist, io_hist, procesos = simular_sjf(self.procesos)

            # =========================
            # MOSTRAR RESULTADOS
            # =========================
            self.resultado.delete(1.0, tk.END)

            total_te = 0
            total_teje = 0

            # Encabezado con formato mejorado
            self.resultado.insert(tk.END, "=" * 70 + "\n")
            self.resultado.insert(
                tk.END,
                "RESULTADOS DE LA SIMULACIÓN SJF\n"
            )
            self.resultado.insert(tk.END, "=" * 70 + "\n\n")

            self.resultado.insert(
                tk.END,
                f"{'Proceso':<10} {'Llegada':<10} {'Ráfaga':<10} {'Fin':<10} "
                f"{'TEP':<10} {'TEjeP':<10}\n"
            )
            self.resultado.insert(tk.END, "-" * 70 + "\n")

            for p in procesos:
                te = p["fin"] - p["rafaga"] - p["llegada"]

                # Restar TODAS las duraciones de E/S
                total_io = sum(io["duracion"] for io in p["io"])
                te -= total_io

                teje = p["fin"] - p["llegada"]

                total_te += te
                total_teje += teje

                self.resultado.insert(
                    tk.END,
                    f"{p['id']:<10} {p['llegada']:<10} {p['rafaga']:<10} "
                    f"{p['fin']:<10} {te:<10} {teje:<10}\n"
                )

            self.resultado.insert(tk.END, "-" * 70 + "\n\n")

            # Promedios con formato destacado
            self.resultado.insert(tk.END, "PROMEDIOS:\n")
            self.resultado.insert(tk.END, "-" * 70 + "\n")
            self.resultado.insert(
                tk.END,
                f"  ⏱️  TEP (Tiempo de Espera Promedio)      = {total_te / len(procesos):.2f} ms\n"
            )
            self.resultado.insert(
                tk.END,
                f"  ⌛ TEjeP (Tiempo de Ejecución Promedio) = {total_teje / len(procesos):.2f} ms\n"
            )
            self.resultado.insert(tk.END, "=" * 70 + "\n")

            # =========================
            # DIBUJOS
            # =========================
            dibujar_cpl(self.frame_cpl, cpl_hist)
            dibujar_oes(self.frame_io, io_hist)
            dibujar_gantt(self.frame_gantt, gantt)

            messagebox.showinfo("✅ Simulación completada",
                                "La simulación se ejecutó correctamente")

        except Exception as e:
            messagebox.showerror("❌ Error en simulación",
                                 f"Ocurrió un error durante la simulación:\n{str(e)}")

    # =========================
    # LIMPIAR
    # =========================
    def limpiar_todo(self):
        if self.procesos:
            respuesta = messagebox.askyesno(
                "⚠️ Confirmar",
                "¿Está seguro de que desea limpiar todos los datos?\n" +
                "Esta acción no se puede deshacer."
            )
            if not respuesta:
                return

        self.procesos.clear()

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.label_contador.config(text="Total de procesos: 0")

        self.resultado.delete(1.0, tk.END)

        for frame in (self.frame_cpl, self.frame_io, self.frame_gantt):
            for widget in frame.winfo_children():
                widget.destroy()

        # Limpiar campos del formulario
        for e in (
                self.id_entry, self.llegada_entry, self.rafaga_entry,
                self.io_inicio_entry, self.io_duracion_entry
        ):
            e.delete(0, tk.END)

        self.id_entry.focus()

        messagebox.showinfo("✅ Limpieza completada",
                            "Se han eliminado todos los datos")
        self.btn_simular.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = SJFApp(root)
    root.mainloop()