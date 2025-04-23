from flask import Flask, render_template, request
from app.scheduler import generar_horario

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        materias = request.form.get("materias", "").split(",")
        prioridades_str = request.form.get("prioridades", "")
        evitar_temprano = "evitar_temprano" in request.form
        evitar_viernes = "evitar_viernes" in request.form

        # Procesar las prioridades en formato diccionario
        prioridades = {}
        if prioridades_str:
            for item in prioridades_str.split(","):
                materia, prioridad = item.split(":")
                prioridades[materia.strip()] = int(prioridad.strip())
                
        resultado = generar_horario(materias, prioridades, evitar_temprano, evitar_viernes)

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
