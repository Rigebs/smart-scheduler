# app/models.py
from app import db

# Definimos un modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    preferencias = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

# Definimos un modelo de Materia
class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    prioridad = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Materia {self.nombre}>'
