from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Inicializamos la app y la base de datos
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'  # Configuración de la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Opcional para evitar advertencias

# Inicializamos SQLAlchemy y Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importa las rutas de la aplicación
from app import routes  # Asegúrate de que esto esté aquí
