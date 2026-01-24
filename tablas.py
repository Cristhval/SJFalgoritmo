def imprimir_tablas(procesos, gantt, cpl_hist, io_hist):

    # =========================
    # TABLA DE PROCESOS
    # =========================
    print("\n" + "=" * 60)
    print("📋 TABLA DE PROCESOS")
    print("=" * 60)
    print(f"{'Proceso':^10}|{'Llegada':^10}|{'Ráfaga':^10}|{'O E/S':^10}|{'Duración':^10}")
    print("-" * 60)

    for p in procesos:
        print(f"{p['id']:^10}|"
              f"{p['llegada']:^10}|"
              f"{p['rafaga']:^10}|"
              f"{'Sí' if p['io_inicio'] is not None else 'No':^10}|"
              f"{p['io_duracion'] if p['io_duracion'] else '-':^10}")

    # =========================
    # DIAGRAMA DE GANTT (TEXTO)
    # =========================
    print("\n" + "=" * 60)
    print("📊 DIAGRAMA DE GANTT – CPU")
    print("=" * 60)

    tiempo = "".join(f"{i:^4}" for i in range(len(gantt)))
    procesos_g = "".join(f"{p:^4}" for p in gantt)

    print("Tiempo :", tiempo)
    print("CPU    :", procesos_g)

    # =========================
    # CPL FINAL
    # =========================
    print("\n" + "=" * 60)
    print("📥 COLA DE PROCESOS LISTOS (CPL) – HISTORIAL")
    print("=" * 60)
    print("| " + " | ".join(cpl_hist) + " |")

    # =========================
    # O E/S FINAL
    # =========================
    print("\n" + "=" * 60)
    print("🔄 LISTA DE O E/S – HISTORIAL")
    print("=" * 60)

    if io_hist:
        print("| " + " | ".join(io_hist) + " |")
    else:
        print("No hubo operaciones de Entrada / Salida")

    # =========================
    # TABLA FINAL TE y TEje
    # =========================
    print("\n" + "=" * 60)
    print("📈 TABLA FINAL – TIEMPOS")
    print("=" * 60)
    print(f"{'Proceso':^10}|{'TE':^10}|{'TEje':^10}")
    print("-" * 60)

    total_te = 0
    total_teje = 0

    for p in procesos:
        te = p["fin"] - p["rafaga"] - p["llegada"]
        if p["io_duracion"]:
            te -= p["io_duracion"]

        teje = p["fin"] - p["llegada"]

        total_te += te
        total_teje += teje

        print(f"{p['id']:^10}|{te:^10}|{teje:^10}")

    # =========================
    # PROMEDIOS
    # =========================
    print("=" * 60)
    print(f"📌 Tiempo de Espera Promedio (TEP)   : {round(total_te / len(procesos), 2)}")
    print(f"📌 Tiempo de Ejecución Promedio (TEjeP): {round(total_teje / len(procesos), 2)}")
    print("=" * 60)
