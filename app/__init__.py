from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "routes.login_view"


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scheduler.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "mi_clave_secreta"

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # 👇 Importar y registrar el blueprint
    from app.routes import routes
    app.register_blueprint(routes)

    return app
