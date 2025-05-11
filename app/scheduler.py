import random
from datetime import datetime
from collections import defaultdict

# --- Utilidades de tiempo ---
def parse_time(hhmm):
    # Si el formato es solo 'HH:MM', agregar los segundos '00'
    if len(hhmm) == 5:
        hhmm = hhmm + ":00"
    return datetime.strptime(hhmm, "%H:%M:%S")


def duracion(a):
    return (parse_time(a["end_time"]) - parse_time(a["start_time"])).seconds / 3600

def overlap(a, b):
    if a["day"] != b["day"]:
        return False
    start_a, end_a = parse_time(a["start_time"]), parse_time(a["end_time"])
    start_b, end_b = parse_time(b["start_time"]), parse_time(b["end_time"])
    return max(start_a, start_b) < min(end_a, end_b)

def bloqueado(a, bloqueos):
    for b in bloqueos:
        if a["day"] != b["day"]:
            continue
        if max(parse_time(a["start_time"]), parse_time(b["start"])) < min(parse_time(a["end_time"]), parse_time(b["end"])):
            return True
    return False

# --- Preparación de datos por curso ---
def agrupar_por_curso(asignaciones):
    cursos = defaultdict(list)
    for a in asignaciones:
        cursos[a["course_id"]].append(a)
    return cursos

# --- Evaluación de un individuo ---
def evaluar_individuo(individuo, preferencias):
    score = 0
    horario = []
    horas_por_dia = defaultdict(float)
    dias_activos = set()

    for a in individuo:
        # Primero, comprobamos si la clase está bloqueada
        if bloqueado(a, preferencias.get("blocked_hours", [])):
            score -= 100
            continue

        # Verificación de días evitados
        if a["day"] in preferencias.get("avoid_days", []):
            score -= 5
            continue

        # Verificación de la hora de inicio evitada
        if a["start_time"].startswith(preferencias.get("avoid_start_hour", "")):
            score -= 3
            continue

        # Verificación de si el profesor está en las preferencias
        if any(p in a["professor_name"] for p in preferencias.get("preferred_teachers", [])):
            score += 5

        # Verificación de la modalidad preferida
        if a.get("modalidad", "In-person") in preferencias.get("preferred_modalities", []):
            score += 3

        # Verificación de las horas por día
        dur = duracion(a)
        if horas_por_dia[a["day"]] + dur > preferencias.get("max_hours_per_day", 6):
            score -= 50
        else:
            horas_por_dia[a["day"]] += dur

        # Verificación de superposición con otras clases ya asignadas
        if any(overlap(a, h) for h in horario):
            score -= 50
        else:
            horario.append(a)
            dias_activos.add(a["day"])

    # Verificación de días activos por semana
    if len(dias_activos) < preferencias.get("min_days_per_week", 1):
        score -= 30
    if len(dias_activos) > preferencias.get("max_days_per_week", 7):
        score -= 30

    return score

# --- Crear un individuo válido --- 
def crear_individuo(cursos):
    individuo = []
    for opciones in cursos.values():
        # Agrupar clases por profesor
        clases_por_profesor = defaultdict(list)
        for clase in opciones:
            clases_por_profesor[clase["professor_name"]].append(clase)
        
        # Buscar profesores con ambas clases (T y P)
        candidatos = []
        for profe, clases in clases_por_profesor.items():
            tipos = {c["class_type"] for c in clases}
            if "T" in tipos and "P" in tipos:
                candidatos.append((profe, clases))
        
        if candidatos:
            profe_elegido, clases = random.choice(candidatos)
            teorica = random.choice([c for c in clases if c["class_type"] == "T"])
            practica = random.choice([c for c in clases if c["class_type"] == "P"])
            individuo.extend([teorica, practica])
        else:
            # Fallback: si ningún profesor tiene ambas, elige lo que haya
            individuo.append(random.choice(opciones))
    return individuo

# --- Mutación ---
def mutar(individuo, cursos):
    nuevo = individuo.copy()
    curso_indices = list(range(0, len(individuo), 2))
    i = random.choice(curso_indices)
    curso = individuo[i]["course_id"]
    opciones = cursos[curso]

    clases_por_profesor = defaultdict(list)
    for clase in opciones:
        clases_por_profesor[clase["professor_name"]].append(clase)
    
    candidatos = []
    for profe, clases in clases_por_profesor.items():
        tipos = {c["class_type"] for c in clases}
        if "T" in tipos and "P" in tipos:
            candidatos.append((profe, clases))
    
    if candidatos:
        profe_elegido, clases = random.choice(candidatos)
        teorica = random.choice([c for c in clases if c["class_type"] == "T"])
        practica = random.choice([c for c in clases if c["class_type"] == "P"])
        nuevo[i] = teorica
        nuevo[i + 1] = practica
    return nuevo

# --- Cruce ---
def cruzar(p1, p2):
    punto = random.randint(1, len(p1) // 2 - 1) * 2  # Multiplo de 2
    hijo1 = p1[:punto] + p2[punto:]
    hijo2 = p2[:punto] + p1[punto:]

    def agrupar_por_curso_parejas(ind):
        cursos_vistos = set()
        nuevo = []
        for i in range(0, len(ind), 2):
            c1, c2 = ind[i], ind[i+1]
            cid = c1["course_id"]
            if cid not in cursos_vistos:
                nuevo.extend([c1, c2])
                cursos_vistos.add(cid)
        return nuevo

    return agrupar_por_curso_parejas(hijo1), agrupar_por_curso_parejas(hijo2)

# --- Algoritmo Genético Principal ---
def algoritmo_genetico(assignments, preferences, generaciones=50, poblacion_size=30, elite=0.2, mutacion_prob=0.1):
    cursos = agrupar_por_curso(assignments)
    poblacion = [crear_individuo(cursos) for _ in range(poblacion_size)]

    for _ in range(generaciones):
        puntuados = [(evaluar_individuo(i, preferences), i) for i in poblacion]
        puntuados.sort(key=lambda x: x[0], reverse=True)
        poblacion = [i for (_, i) in puntuados[:int(elite * poblacion_size)]]

        while len(poblacion) < poblacion_size:
            padres = random.sample(poblacion, 2)
            hijo1, hijo2 = cruzar(padres[0], padres[1])
            if random.random() < mutacion_prob:
                hijo1 = mutar(hijo1, cursos)
            if random.random() < mutacion_prob:
                hijo2 = mutar(hijo2, cursos)
            poblacion.extend([hijo1, hijo2])

    mejor = max(poblacion, key=lambda i: evaluar_individuo(i, preferences))

    # Crear la nueva variable mejor_paralelo
    mejor_paralelo = []
    for asignacion in mejor:
        # Evaluar si la asignación cumple con las preferencias
        cumple = True
        mensaje = "Success: Preferences met."

        # Evaluar bloqueos y otras condiciones
        if bloqueado(asignacion, preferences.get("blocked_hours", [])):
            cumple = False
            mensaje = f"Reason: Blocked time on {asignacion['day']} from {asignacion['start_time']} to {asignacion['end_time']}."
        elif asignacion["day"] in preferences.get("avoid_days", []):
            cumple = False
            mensaje = f"Reason: Scheduled on avoided day ({asignacion['day']})."
        elif asignacion["start_time"].startswith(preferences.get("avoid_start_hour", "")):
            cumple = False
            mensaje = f"Reason: Starts at {asignacion['start_time']}, which matches avoided hour prefix ({preferences.get('avoid_start_hour')})."
        elif preferences.get("preferred_teachers") and not any(p in asignacion["professor_name"] for p in preferences["preferred_teachers"]):
            cumple = False
            mensaje = f"Reason: Assigned professor '{asignacion['professor_name']}' is not in preferred list."
        elif preferences.get("preferred_modalities") and asignacion.get("modalidad", "In-person") not in preferences["preferred_modalities"]:
            cumple = False
            mensaje = f"Reason: Modality '{asignacion.get('modalidad', 'In-person')}' is not in preferred modalities."


        # Clonar la asignación e insertar los nuevos campos adentro
        asignacion_con_info = dict(asignacion)  # evitar mutar el original
        asignacion_con_info["value"] = cumple
        asignacion_con_info["message"] = mensaje

        # Agregar al resultado
        mejor_paralelo.append(asignacion_con_info)

    # Imprimir mejor_paralelo
    for item in mejor_paralelo:
        
        # print(f"Class: {item['course_name']}, Professor: {item['professor_name']}")
        #print(f"Complies: {item['value']}, Message: {item['message']}, Classtype: {item['class_type']}")
        #print(f"---------------------------------------------------------------")

        print(f"Id: {item['assignment_detail_id']}")
    
    # Retornar la mejor asignación encontrada
    return mejor_paralelo