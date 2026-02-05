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

    for i in range(1, n + 1):
        print(f"\nProceso P{i}")
        try:
            llegada = int(input("Tiempo de llegada: "))
            rafaga = int(input("Ráfaga de CPU: "))

            io = []
            tiene_io = input("¿Tiene O E/S? (s/n): ").lower()

            if tiene_io == "s":
                inicios = input( # Permite maximo 3 O E/S
                    "Inicios de O E/S (ej: 2 3 4): "
                ).split()

                duraciones = input(
                    "Duraciones de O E/S (ej: 1 2 1): "
                ).split()

                if len(inicios) != len(duraciones): # Verifica cuantas E/S tiene un proceso
                    raise ValueError("Cantidad distinta de inicios y duraciones")

                if len(inicios) > 3:
                    raise ValueError("Máximo 3 E/S por proceso")

                for ini, dur in zip(inicios, duraciones):
                    ini = int(ini)
                    dur = int(dur)

                    if ini < 0 or dur <= 0 or ini >= rafaga:
                        raise ValueError("Valores inválidos de E/S")

                    io.append({ # Guarda todas las E/S
                        "inicio": ini,
                        "duracion": dur
                    })

                io.sort(key=lambda x: x["inicio"])

            procesos.append({
                "id": f"P{i}",
                "llegada": llegada,
                "rafaga": rafaga,
                "restante": rafaga,
                "io": io,
                "io_actual": 0,
                "io_retorno": None,
                "ejecutado": 0,
                "fin": None
            })

        except Exception as e:
            print("❌ Error:", e)
            return ingresar_procesos()

    return procesos


# =========================
# SIMULACIÓN SJF APROPIATIVO
# =========================
def simular_sjf(procesos):
    tiempo = 0
    cpu = None
    cpl = []
    gantt = []
    io_hist = []


    historial_cpl = []

    procesos_tabla = procesos.copy()
    procesos_io = []

    while True:
        #  FIX: Registrar solo cuando procesos ENTRAN a CPL

        # Llegadas desde tabla
        llegados = [p for p in procesos_tabla if p["llegada"] == tiempo]
        for p in llegados:
            cpl.append(p)
            procesos_tabla.remove(p)
            historial_cpl.append(p["id"])  #  Registrar llegada nueva

        # Retornos de O E/S
        retornos = [p for p in procesos_io if p["io_retorno"] == tiempo]
        for p in retornos:
            cpl.append(p)
            procesos_io.remove(p)
            historial_cpl.append(p["id"])  #  Registrar retorno de E/S

        # Orden CPL (SJF + FIFO + prioridad tabla)
        cpl.sort(key=lambda x: (x["restante"], x["llegada"]))

        # Selección CPU(APROPIACION)
        if cpu and cpu["restante"] > 0:
            if cpl and cpl[0]["restante"] < cpu["restante"]:
                cpl.append(cpu)
                cpl.sort(key=lambda x: (x["restante"], x["llegada"]))
                cpu = cpl.pop(0)
        elif cpl:
            cpu = cpl.pop(0)

        # Ejecutar CPU
        # Ir a O E/S
        if cpu:
            gantt.append(cpu["id"])
            cpu["restante"] -= 1  # simula 1 unidad de tiempo
            cpu["ejecutado"] += 1

            # 1️ Verificar E/S
            if cpu["io_actual"] < len(cpu["io"]):
                io_act = cpu["io"][cpu["io_actual"]]

                if cpu["ejecutado"] == io_act["inicio"]:
                    # Registrar evento de E/S (CLAVE)
                    io_hist.append({
                        "id": cpu["id"],
                        "inicio": tiempo,
                        "duracion": io_act["duracion"]
                    })

                    cpu["io_retorno"] = tiempo + io_act["duracion"] + 1
                    cpu["io_actual"] += 1
                    procesos_io.append(cpu)
                    cpu = None


            # 2️ Verificar finalización (SIEMPRE)
            if cpu and cpu["restante"] == 0:
                cpu["fin"] = tiempo + 1
                cpu = None

        else:
            gantt.append("—") # CPU ociosa


        tiempo += 1

        if not (procesos_tabla or cpl or cpu or procesos_io):
            break

    return gantt, historial_cpl, io_hist, procesos


# =========================
# TABLAS Y MÉTRICAS
# =========================
def imprimir_tablas(procesos, gantt, cpl_hist, io_hist):
    print("\n📋 TABLA DE PROCESOS")
    print("Proceso | Llegada | Ráfaga | Inicios E/S | Duraciones")
    for p in procesos:
        inicios = " ".join(str(io["inicio"]) for io in p["io"]) or "-"
        dur = " ".join(str(io["duracion"]) for io in p["io"]) or "-"

        print(f"{p['id']:7} | {p['llegada']:7} | {p['rafaga']:6} | "
            f"{inicios:11} | {dur}")

    print("\n📊 DIAGRAMA DE GANTT (CPU)")
    print("|" + "|".join(gantt) + "|")

    print("\n📥 CPL FINAL")
    print("|" + "|".join(cpl_hist) + "|")

    print("\n🔄 O E/S FINAL")
    if io_hist:
        eventos = [
            f"{e['id']}@{e['inicio']}({e['duracion']})"
            for e in io_hist
        ]
        print("| " + " | ".join(eventos) + " |")
    else:
        print("| — |")




    print("\n📈 TABLA FINAL (TE y TEje)")
    total_te = 0
    total_teje = 0

    print("Proceso | TE | TEje")
    for p in procesos:
        te = p["fin"] - p["rafaga"] - p["llegada"]
        if p["io"]:
            te -= sum(io["duracion"] for io in p["io"])

        teje = p["fin"] - p["llegada"]

        total_te += te
        total_teje += teje

        print(f"{p['id']:7} | {te:2} | {teje:4}")

    print("\n📌 TEP =", total_te / len(procesos))
    print("📌 TEjeP =", total_teje / len(procesos))