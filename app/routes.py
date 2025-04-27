# routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user

from app import db, login
from app.models import Usuario, Materia
from app.scheduler import generar_horario

routes = Blueprint("routes", __name__)

@routes.route("/")
def index():
    return render_template("index.html")

@routes.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        usuario = Usuario.query.filter_by(email=email).first()

        # Verifica las credenciales
        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for("routes.perfil"))
        else:
            flash("Correo electrónico o contraseña incorrectos", "danger")
    
    return render_template("auth/login.html")

@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]
        password_confirm = request.form["password_confirm"]

        if password != password_confirm:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("routes.register"))

        if Usuario.query.filter_by(email=email).first():
            flash("El correo electrónico ya está registrado", "danger")
            return redirect(url_for("routes.register"))

        nuevo_usuario = Usuario(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Cuenta creada exitosamente, por favor inicia sesión", "success")
        return redirect(url_for("routes.login_view"))

    return render_template("register.html")

@routes.route("/perfil")
@login_required
def perfil():
    return render_template("profile.html", usuario=current_user)

@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.login_view"))

@login.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@routes.route("/add_materia", methods=["POST"])
def add_materia():
    nombre = request.form["nombre"]
    prioridad = int(request.form["prioridad"])
    
    nueva_materia = Materia(nombre=nombre, prioridad=prioridad)
    db.session.add(nueva_materia)
    db.session.commit()
    
    return "Materia añadida"

@routes.route("/generar_horario", methods=["POST"])
def generar_horario_route():
    materias_input = request.form.get("materias", "").split(",")
    prioridades_input = request.form.get("prioridades", "").split(",")
    
    prioridades = {}
    for prioridad in prioridades_input:
        materia, valor = prioridad.split(":")
        prioridades[materia.strip()] = int(valor.strip())
    
    horario = generar_horario(materias_input, prioridades)
    
    return render_template("index.html", resultado=horario)
