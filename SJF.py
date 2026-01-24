# =====================================================
# Simulador SJF Apropiativo (SRTF) - VALIDADO
# FIFO en empates + prioridad llegada tabla + validación
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
        self.orden_llegada_cpl = None  # FIFO

    def __str__(self):
        return f"P{self.pid}"


# =========================
# INGRESO SEGURO DE DATOS
# =========================

def leer_entero(mensaje, minimo=0):
    while True:
        try:
            v = int(input(mensaje))
            if v < minimo:
                raise ValueError
            return v
        except ValueError:
            print("❌ Valor inválido. Intente nuevamente.")


while True:
    n = leer_entero("Ingrese el número de procesos: ", 1)
    procesos = []
    error = False

    for i in range(n):
        print(f"\nProceso P{i}")
        try:
            llegada = leer_entero("Tiempo de llegada: ", 0)
            rafaga = leer_entero("Ráfaga de CPU: ", 1)

            tiene_io = input("¿Tiene O E/S? (s/n): ").lower()
            if tiene_io not in ('s', 'n'):
                raise ValueError

            instante_io = 0
            duracion_io = 0
            if tiene_io == 's':
                instante_io = leer_entero(
                    "¿Después de cuántos ms ejecutados va a O E/S?: ", 1)
                duracion_io = leer_entero(
                    "Duración de O E/S: ", 1)

            procesos.append(
                Proceso(i, llegada, rafaga,
                        tiene_io == 's', instante_io, duracion_io)
            )
        except:
            print("❌ Error en los datos. Se reinicia el ingreso.")
            error = True
            break

    if not error:
        break


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

contador_fifo = 0

while True:
    # 1️⃣ Llegadas desde TABLA (prioridad)
    for p in procesos:
        if p.llegada == tiempo:
            p.orden_llegada_cpl = contador_fifo
            contador_fifo += 1
            cpl.append(p)
            cpl_final.append(str(p))

    # 2️⃣ Regreso de O E/S
    for p in io[:]:
        if tiempo == p.io_fin:
            p.orden_llegada_cpl = contador_fifo
            contador_fifo += 1
            cpl.append(p)
            cpl_final.append(str(p))
            io.remove(p)

    # Ordenar CPL → SJF + FIFO
    cpl.sort(key=lambda x: (x.rafaga_restante, x.orden_llegada_cpl))

    # Apropiación
    if cpu and cpl and (
        cpl[0].rafaga_restante < cpu.rafaga_restante):
        cpu.orden_llegada_cpl = contador_fifo
        contador_fifo += 1
        cpl.append(cpu)
        cpl_final.append(str(cpu))
        cpu = None

    # Asignar CPU
    if cpu is None and cpl:
        cpu = cpl.pop(0)

    gantt_cpu.append(str(cpu) if cpu else "Idle")

    # Ejecutar CPU
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
            cpu = None

    tiempo += 1

    if all(p.rafaga_restante == 0 for p in procesos) and not io and cpu is None:
        break


# =========================
# SALIDAS
# =========================

print("\nGANTT CPU")
print("".join(f"|{p:^4}" for p in gantt_cpu) + "|")
print("".join(f"{i:^5}" for i in range(len(gantt_cpu))))

print("\nCPL FINAL")
print("".join(f"|{p:^4}" for p in cpl_final) + "|")

print("\nO E/S FINAL")
if io_final:
    print("".join(f"|{p:^4}" for p, _ in io_final) + "|")
    print("".join(f"|{fin:^4}" for _, fin in io_final) + "|")
else:
    print("|   SIN O E/S   |")
