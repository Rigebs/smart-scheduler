import random

def generar_horario(materias, prioridades=None, evitar_temprano=False, evitar_viernes=False):
    """
    Genera un horario inteligente.
    
    :param materias: Lista de materias a incluir en el horario
    :param prioridades: Diccionario de prioridades por materia (opcional)
    :param evitar_temprano: True si se quiere evitar clases temprano (opcional)
    :param evitar_viernes: True si se quiere evitar clases los viernes (opcional)
    :return: Diccionario con el horario generado
    """

    # Definir los días y horarios disponibles
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    horas = ["08:00", "10:00", "12:00", "14:00", "16:00"]

    # Si no hay prioridades, asignarlas a las materias de forma aleatoria
    if not prioridades:
        prioridades = {materia: random.randint(1, 10) for materia in materias}

    # Ordenar las materias por prioridad (de mayor a menor)
    materias_ordenadas = sorted(materias, key=lambda x: prioridades.get(x, 5), reverse=True)

    # Inicializar un diccionario de horarios vacío
    horario = {}
    
    # Para llevar un control de los días y horas ya ocupados
    dia_asignado = {dia: 0 for dia in dias}  # Para evitar sobrecargar un día
    hora_asignada = {hora: 0 for hora in horas}  # Para evitar horarios repetidos

    # Recorremos las materias en orden de prioridad
    ocupado = set()

    for materia in materias_ordenadas:
        asignado = False
        for dia in dias:
            if evitar_viernes and dia == "Viernes":
                continue

            for hora in horas:
                if evitar_temprano and hora == "08:00":
                    continue

                if (dia, hora) not in ocupado:
                    horario[materia] = {"dia": dia, "hora": hora}
                    ocupado.add((dia, hora))
                    asignado = True
                    break

            if asignado:
                break

    return horario
