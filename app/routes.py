## routes.py

from app import app, db
from flask import render_template, request
from app.models import Materia
from app.scheduler import generar_horario  # si tienes la lógica en otro archivo

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_materia", methods=["POST"])
def add_materia():
    nombre = request.form["nombre"]
    prioridad = int(request.form["prioridad"])
    
    nueva_materia = Materia(nombre=nombre, prioridad=prioridad)
    db.session.add(nueva_materia)
    db.session.commit()
    
    return "Materia añadida"

@app.route("/generar_horario", methods=["POST"])
def generar_horario_route():
    # Obtener las materias y las prioridades del formulario
    materias_input = request.form.get("materias", "").split(",")
    prioridades_input = request.form.get("prioridades", "").split(",")
    
    # Convertir el input de prioridades en un diccionario
    prioridades = {}
    for prioridad in prioridades_input:
        materia, valor = prioridad.split(":")
        prioridades[materia.strip()] = int(valor.strip())
    
    # Llamar a la función generar_horario con las materias y prioridades proporcionadas
    horario = generar_horario(materias_input, prioridades)
    
    return render_template("index.html", resultado=horario)
