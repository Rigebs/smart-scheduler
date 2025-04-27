# app/models.py
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# ------------------ Usuario ------------------
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    materias = db.relationship('Materia', backref='usuario', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ------------------ Profesor ------------------
class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    disponibilidad = db.Column(db.Text)  # JSON: {"lunes":["08:00-12:00"], ...}

    grupos = db.relationship('Grupo', backref='profesor', lazy=True)
    preferencias = db.relationship('Preferencia', backref='profesor', lazy=True)
    restricciones = db.relationship('Restriccion', backref='profesor', lazy=True)

# ------------------ Estudiante ------------------
class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    carrera = db.Column(db.String(100), nullable=False)

    materias = db.relationship('MateriaEstudiante', back_populates='estudiante')
    restricciones = db.relationship('Restriccion', backref='estudiante', lazy=True)

# ------------------ Materia ------------------
class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    creditos = db.Column(db.Integer, nullable=False)
    duracion_por_sesion = db.Column(db.Integer, nullable=False)  # en minutos

    grupos = db.relationship('Grupo', backref='materia', lazy=True)
    estudiantes = db.relationship('MateriaEstudiante', back_populates='materia')

# ------------------ Relación Muchos a Muchos (Materia - Estudiante) ------------------
class MateriaEstudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)

    estudiante = db.relationship('Estudiante', back_populates='materias')
    materia = db.relationship('Materia', back_populates='estudiantes')

# ------------------ Grupo/Sección ------------------
class Grupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'), nullable=False)
    cupo_maximo = db.Column(db.Integer, nullable=False)

    horarios = db.relationship('HorarioTentativo', backref='grupo', lazy=True)
    historicos = db.relationship('HistoricoCambio', backref='grupo', lazy=True)

# ------------------ Horario Tentativo ------------------
class HorarioTentativo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    dia_semana = db.Column(db.String(20), nullable=False)  # 'lunes', 'martes', etc.
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    aula_id = db.Column(db.Integer, db.ForeignKey('aula.id'), nullable=False)

# ------------------ Aula ------------------
class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_aula = db.Column(db.String(120), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    recursos_especiales = db.Column(db.String(200))  # ejemplo: 'proyector,laboratorio'

    horarios = db.relationship('HorarioTentativo', backref='aula', lazy=True)
    restricciones = db.relationship('Restriccion', backref='aula', lazy=True)

# ------------------ Restricción ------------------
class Restriccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'prohibido' o 'preferido'
    detalle = db.Column(db.Text)

    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'), nullable=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=True)
    aula_id = db.Column(db.Integer, db.ForeignKey('aula.id'), nullable=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=True)

# ------------------ Preferencia ------------------
class Preferencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profesor_id = db.Column(db.Integer, db.ForeignKey('profesor.id'), nullable=False)
    dia_preferido = db.Column(db.String(20))
    hora_preferida = db.Column(db.Time)
    peso = db.Column(db.Integer, default=1)  # 1 a 5, donde 5 es "muy importante"

# ------------------ Histórico de Cambios ------------------
class HistoricoCambio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupo.id'), nullable=False)
    cambio_realizado = db.Column(db.Text)
    fecha_cambio = db.Column(db.DateTime, nullable=False)
    usuario_responsable = db.Column(db.String(120))
