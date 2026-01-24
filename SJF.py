# =====================================================
# Simulador SJF Apropiativo (SRTF)
# Con O E/S, Gantt, CPL, métricas
# =====================================================

class Proceso:
    def __init__(self, pid, llegada, rafaga, tiene_io,
                 instante_io, duracion_io):
        self.pid = pid
        self.llegada = llegada
        self.rafaga_total = rafaga
        self.rafaga_restante = rafaga

        self.tiene_io = tiene_io
        self.instante_io = instante_io
        self.duracion_io = duracion_io

        self.ejecutado_cpu = 0
        self.io_realizado = False
        self.io_fin = None

        self.orden_llegada_cpl = None
        self.tiempo_fin = None  # ⬅ NUEVO

    def __str__(self):
        return f"P{self.pid}"


# =========================
# INGRESO DE DATOS
# =========================

def leer_entero(msg, minimo=0):
    while True:
        try:
            v = int(input(msg))
            if v < minimo:
                raise ValueError
            return v
        except ValueError:
            print("❌ Valor inválido.")

while True:
    n = leer_entero("Número de procesos: ", 1)
    procesos = []
    error = False

    for i in range(n):
        print(f"\nProceso P{i}")
        try:
            llegada = leer_entero("Tiempo de llegada: ")
            rafaga = leer_entero("Ráfaga CPU: ", 1)

            tiene_io = input("¿Tiene O E/S? (s/n): ").lower()
            if tiene_io not in ("s", "n"):
                raise ValueError

            instante_io = 0
            duracion_io = 0
            if tiene_io == "s":
                instante_io = leer_entero(
                    "Milisegundo en que va a O E/S: ", 1)
                duracion_io = leer_entero(
                    "Duración de O E/S: ", 1)

            procesos.append(
                Proceso(i, llegada, rafaga,
                        tiene_io == "s",
                        instante_io, duracion_io)
            )
        except:
            print("❌ Error en los datos. Reingrese todo.")
            error = True
            break

    if not error:
        break


# =========================
# TABLA DE PROCESOS
# =========================

print("\nTABLA DE PROCESOS")
print("-" * 65)
print("Proceso | Llegada | Ráfaga | O E/S | Instante | Duración")
print("-" * 65)

for p in procesos:
    print(f"P{p.pid:^7}|{p.llegada:^9}|{p.rafaga_total:^8}|"
          f"{'Sí' if p.tiene_io else 'No':^6}|"
          f"{p.instante_io if p.tiene_io else '-':^9}|"
          f"{p.duracion_io if p.tiene_io else '-':^9}")
print("-" * 65)


# =========================
# SIMULACIÓN
# =========================

tiempo = 0
cpu = None
cpl = []
io = []

gantt_cpu = []
cpl_final = []
io_final = []

fifo = 0

while True:
    # Llegadas desde tabla
    for p in procesos:
        if p.llegada == tiempo:
            p.orden_llegada_cpl = fifo
            fifo += 1
            cpl.append(p)
            cpl_final.append(str(p))

    # Regresos de O E/S
    for p in io[:]:
        if tiempo == p.io_fin:
            p.orden_llegada_cpl = fifo
            fifo += 1
            cpl.append(p)
            cpl_final.append(str(p))
            io.remove(p)

    # Ordenar CPL (SJF + FIFO)
    cpl.sort(key=lambda x: (x.rafaga_restante, x.orden_llegada_cpl))

    # Apropiación
    if cpu and cpl and cpl[0].rafaga_restante < cpu.rafaga_restante:
        cpu.orden_llegada_cpl = fifo
        fifo += 1
        cpl.append(cpu)
        cpl_final.append(str(cpu))
        cpu = None

    # Asignar CPU
    if cpu is None and cpl:
        cpu = cpl.pop(0)

    gantt_cpu.append(str(cpu) if cpu else "Idle")

    # Ejecutar
    if cpu:
        cpu.rafaga_restante -= 1
        cpu.ejecutado_cpu += 1

        if (cpu.tiene_io and not cpu.io_realizado and
                cpu.ejecutado_cpu == cpu.instante_io):
            cpu.io_realizado = True
            cpu.io_fin = tiempo + cpu.duracion_io
            io.append(cpu)
            io_final.append((str(cpu), cpu.io_fin))
            cpu = None

        elif cpu.rafaga_restante == 0:
            cpu.tiempo_fin = tiempo + 1  # ⬅ IMPORTANTE
            cpu = None

    tiempo += 1

    if all(p.rafaga_restante == 0 for p in procesos) and not io and not cpu:
        break


# =========================
# MÉTRICAS
# =========================

total_te = 0
total_teje = 0

for p in procesos:
    te = (p.tiempo_fin
          - p.rafaga_total
          - p.llegada)

    if p.tiene_io:
        te -= p.duracion_io

    total_te += te
    total_teje += (p.tiempo_fin - p.llegada)

tep = total_te / n
teje_p = total_teje / n


# =========================
# SALIDAS
# =========================

print("\nGANTT CPU")
print("".join(f"|{x:^4}" for x in gantt_cpu) + "|")

print("\nCPL FINAL")
print("".join(f"|{x:^4}" for x in cpl_final) + "|")

print("\nO E/S FINAL")
if io_final:
    print("".join(f"|{p:^4}" for p, _ in io_final) + "|")
    print("".join(f"|{t:^4}" for _, t in io_final) + "|")
else:
    print("|   SIN O E/S   |")

print("\n📊 MÉTRICAS")
print(f"TEP  (Tiempo de Espera Promedio): {tep:.2f} ms")
print(f"TEjeP (Tiempo de Ejecución Promedio): {teje_p:.2f} ms")
