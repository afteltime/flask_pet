from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
import os

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'your db pass+route+name of db'
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['WTF_CSRF_ENABLED'] = True

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    #Talisman(app)  Flask https sert (ВКЛЮЧИТЬ НА ПРОДЕ, ПОФИКСИТЬ ЕГО ВСТАВКУ В csrf токен на html доках )


    from .routes import api_routes
    from .adminpanel import admin_routes

    app.register_blueprint(admin_routes, url_prefix='/')
    app.register_blueprint(api_routes, url_prefix='/')

    with app.app_context():
        db.create_all()

    return app

