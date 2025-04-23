from flask_sqlalchemy import SQLAlchemy

# Inicialización de la base de datos
db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    preferencias = db.Column(db.JSON, nullable=True)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    prioridad = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', back_populates='materias')

    def __repr__(self):
        return f'<Materia {self.nombre}>'

Usuario.materias = db.relationship('Materia', order_by=Materia.id, back_populates='usuario')

class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.String(50), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    materia = db.relationship('Materia', back_populates='horarios')

    def __repr__(self):
        return f'<Horario {self.dia} {self.hora}>'

Materia.horarios = db.relationship('Horario', order_by=Horario.id, back_populates='materia')
