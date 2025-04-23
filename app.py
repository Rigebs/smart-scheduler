from flask import Flask, render_template, request
from app.scheduler import generar_horario

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        materias = request.form.get("materias", "")
        materias = [m.strip() for m in materias.split(",") if m.strip()]
        resultado = generar_horario(materias)
    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)