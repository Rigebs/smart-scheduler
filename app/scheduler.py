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
        if bloqueado(a, preferencias.get("blocked_hours", [])):
            score -= 100
            continue

        if a["day"] in preferencias.get("avoid_days", []):
            score -= 5
        if a["start_time"].startswith(preferencias.get("avoid_start_hour", "")):
            score -= 3
        if any(p in a["professor_name"] for p in preferencias.get("preferred_teachers", [])):
            score += 5
        if a.get("modalidad", "In-person") in preferencias.get("preferred_modalities", []):
            score += 3

        dur = duracion(a)
        if horas_por_dia[a["day"]] + dur > preferencias.get("max_hours_per_day", 6):
            score -= 50
        else:
            horas_por_dia[a["day"]] += dur

        if any(overlap(a, h) for h in horario):
            score -= 50
        else:
            horario.append(a)
            dias_activos.add(a["day"])

    if len(dias_activos) < preferencias.get("min_days_per_week", 1):
        score -= 30
    if len(dias_activos) > preferencias.get("max_days_per_week", 7):
        score -= 30

    return score

# --- Crear un individuo válido --- 
def crear_individuo(cursos):
    individuo = []
    for opciones in cursos.values():
        # Separar las opciones en T y P
        teoricas = [o for o in opciones if o["class_type"] == "T"]
        practicas = [o for o in opciones if o["class_type"] == "P"]
        
        # Asegurar que haya al menos una clase teórica (T) y una práctica (P) por curso
        if teoricas and practicas:
            # Elegir al menos una clase de cada tipo
            individuo.append(random.choice(teoricas))
            individuo.append(random.choice(practicas))
        elif teoricas:
            individuo.append(random.choice(teoricas))  # Solo teóricas si no hay prácticas
        elif practicas:
            individuo.append(random.choice(practicas))  # Solo prácticas si no hay teóricas
    return individuo

# --- Mutación ---
def mutar(individuo, cursos):
    nuevo = individuo.copy()
    i = random.randint(0, len(individuo) - 1)
    curso = individuo[i]["course_id"]
    nuevo[i] = random.choice(cursos[curso])  # Elegir aleatoriamente un nuevo detalle de clase
    return nuevo

# --- Cruce ---
def cruzar(p1, p2):
    punto = random.randint(1, len(p1) - 1)
    
    # Asegurar que el cruce mantenga al menos un T y un P por curso
    hijo1 = p1[:punto] + p2[punto:]
    hijo2 = p2[:punto] + p1[punto:]
    
    # Ajustar ambos hijos para asegurarse de que tengan tanto T como P
    for idx in range(len(hijo1)):
        if hijo1[idx]["class_type"] == "T":
            if not any(c["course_id"] == hijo1[idx]["course_id"] and c["class_type"] == "P" for c in hijo1):
                # Si no hay práctica para ese curso, agregar una práctica
                for c in p2:
                    if c["course_id"] == hijo1[idx]["course_id"] and c["class_type"] == "P":
                        hijo1.append(c)
                        break
        elif hijo1[idx]["class_type"] == "P":
            if not any(c["course_id"] == hijo1[idx]["course_id"] and c["class_type"] == "T" for c in hijo1):
                # Si no hay teoría para ese curso, agregar una teoría
                for c in p2:
                    if c["course_id"] == hijo1[idx]["course_id"] and c["class_type"] == "T":
                        hijo1.append(c)
                        break
                        
    for idx in range(len(hijo2)):
        if hijo2[idx]["class_type"] == "T":
            if not any(c["course_id"] == hijo2[idx]["course_id"] and c["class_type"] == "P" for c in hijo2):
                # Si no hay práctica para ese curso, agregar una práctica
                for c in p1:
                    if c["course_id"] == hijo2[idx]["course_id"] and c["class_type"] == "P":
                        hijo2.append(c)
                        break
        elif hijo2[idx]["class_type"] == "P":
            if not any(c["course_id"] == hijo2[idx]["course_id"] and c["class_type"] == "T" for c in hijo2):
                # Si no hay teoría para ese curso, agregar una teoría
                for c in p1:
                    if c["course_id"] == hijo2[idx]["course_id"] and c["class_type"] == "T":
                        hijo2.append(c)
                        break

    return hijo1, hijo2

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
    return mejor
