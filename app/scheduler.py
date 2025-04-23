def generar_horario(materias):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    horas = ["08:00", "10:00", "12:00", "14:00", "16:00"]

    horario = {}
    i = 0
    for materia in materias:
        dia = dias[i % len(dias)]
        hora = horas[i % len(horas)]
        horario[materia] = {"dia": dia, "hora": hora}
        i += 1
    return horario
