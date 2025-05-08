from flask import Flask
from .extensions import db, jwt, mail, migrate
from .blueprints.auth import auth_bp
from .blueprints.profiles import profiles_bp
from .blueprints.rides import rides_bp
from .blueprints.reservations import reservations_bp
from .blueprints.notifications import notifications_bp
from .blueprints.admin import admin_bp
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profiles_bp, url_prefix='/profiles')
    app.register_blueprint(rides_bp, url_prefix='/rides')
    app.register_blueprint(reservations_bp, url_prefix='/reservations')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
