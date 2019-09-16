import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_mail import Mail
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf.csrf import CSRFProtect
from config import Config
from sqlalchemy import MetaData

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

migrate = Migrate()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
login = LoginManager()
csrf = CSRFProtect()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'

schedules = UploadSet('schedules', ['pdf'])
scoresheets = UploadSet('scoresheets', IMAGES)

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login.init_app(app)
    csrf.init_app(app)

    configure_uploads(app, (schedules, scoresheets))

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models