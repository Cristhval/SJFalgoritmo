
# =========================
# INGRESO DE PROCESOS
# =========================
def ingresar_procesos():
    while True:
        try:
            n = int(input("Ingrese el número de procesos: "))
            if n <= 0:
                raise ValueError
            break
        except ValueError:
            print("❌ Ingrese un número válido.")

    procesos = []

    i = 1
    while i <= n:
        print(f"\nProceso P{i}")
        try:
            llegada = int(input("Tiempo de llegada: "))
            rafaga = int(input("Ráfaga de CPU: "))

            tiene_io = input("¿Tiene O E/S? (s/n): ").lower()
            io_inicio = None
            io_duracion = None

            if tiene_io == "s":
                io_inicio = int(input("Milisegundo de ejecución en que va a O E/S: "))
                io_duracion = int(input("Duración de O E/S: "))

            procesos.append({
                "id": f"P{i}",
                "llegada": llegada,
                "rafaga": rafaga,
                "restante": rafaga,
                "io_inicio": io_inicio,
                "io_duracion": io_duracion,
                "io_retorno": None,
                "ejecutado": 0,
                "fin": None
            })
            i += 1
        except:
            print("❌ Error en datos. Reingrese el proceso.")

    return procesos


# =========================
# SIMULACIÓN SJF APROPIATIVO
# =========================
def simular_sjf(procesos):
    tiempo = 0
    cpu = None
    cpl = []
    io = []
    gantt = []

    historial_cpl = []
    historial_io = []

    procesos_tabla = procesos.copy()
    procesos_io = []

    while True:
        # 🔧 FIX: Registrar solo cuando procesos ENTRAN a CPL

        # Llegadas desde tabla
        llegados = [p for p in procesos_tabla if p["llegada"] == tiempo]
        for p in llegados:
            cpl.append(p)
            procesos_tabla.remove(p)
            historial_cpl.append(p["id"])  # ✅ Registrar llegada nueva

        # Retornos de O E/S
        retornos = [p for p in procesos_io if p["io_retorno"] == tiempo]
        for p in retornos:
            cpl.append(p)
            procesos_io.remove(p)
            historial_cpl.append(p["id"])  # ✅ Registrar retorno de E/S

        # Orden CPL (SJF + FIFO + prioridad tabla)
        cpl.sort(key=lambda x: (x["restante"], x["llegada"]))

        # Selección CPU
        if cpu and cpu["restante"] > 0:
            if cpl and cpl[0]["restante"] < cpu["restante"]:
                cpl.append(cpu)
                cpl.sort(key=lambda x: (x["restante"], x["llegada"]))
                cpu = cpl.pop(0)
        elif cpl:
            cpu = cpl.pop(0)

        # Ejecutar CPU
        if cpu:
            gantt.append(cpu["id"])
            cpu["restante"] -= 1
            cpu["ejecutado"] += 1

            # Ir a O E/S
            if cpu["io_inicio"] is not None and cpu["ejecutado"] == cpu["io_inicio"]:
                cpu["io_retorno"] = tiempo + cpu["io_duracion"] + 1
                cpu["rafaga_restante_io"] = cpu["restante"]
                procesos_io.append(cpu)
                cpu = None

            # Termina proceso
            elif cpu and cpu["restante"] == 0:
                cpu["fin"] = tiempo + 1
                cpu = None
        else:
            gantt.append("—")

        # Registrar estado de O E/S
        if procesos_io:
            historial_io.extend([
                f"{p['id']}({p['io_retorno']})|{p['rafaga_restante_io']}"
                for p in procesos_io
            ])

        tiempo += 1

        if not (procesos_tabla or cpl or cpu or procesos_io):
            break

    return gantt, historial_cpl, historial_io, procesos


# =========================
# TABLAS Y MÉTRICAS
# =========================
def imprimir_tablas(procesos, gantt, cpl_hist, io_hist):
    print("\n📋 TABLA DE PROCESOS")
    print("Proceso | Llegada | Ráfaga | O E/S | Duración")
    for p in procesos:
        print(f"{p['id']:7} | {p['llegada']:7} | {p['rafaga']:6} | "
              f"{'Sí' if p['io_inicio'] else 'No':5} | "
              f"{p['io_duracion'] if p['io_duracion'] else '-'}")

    print("\n📊 DIAGRAMA DE GANTT (CPU)")
    print("|" + "|".join(gantt) + "|")

    print("\n📥 CPL FINAL")
    print("|" + "|".join(cpl_hist) + "|")

    print("\n🔄 O E/S FINAL")
    print("|", end="")
    for item in io_hist:
        base, raf = item.split("|")
        pid, ret = base.replace(")", "").split("(")
        print(f"{pid}: ráfaga {raf} [{ret}] | ", end="")
    print()


    print("\n📈 TABLA FINAL (TE y TEje)")
    total_te = 0
    total_teje = 0

    print("Proceso | TE | TEje")
    for p in procesos:
        te = p["fin"] - p["rafaga"] - p["llegada"]
        if p["io_duracion"]:
            te -= p["io_duracion"]

        teje = p["fin"] - p["llegada"]

        total_te += te
        total_teje += teje

        print(f"{p['id']:7} | {te:2} | {teje:4}")

    print("\n📌 TEP =", total_te / len(procesos))
    print("📌 TEjeP =", total_teje / len(procesos))