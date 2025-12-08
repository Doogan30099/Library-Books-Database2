from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.members import members_bp


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')



    #initialize extentions
    ma.init_app(app)
    db.init_app(app) #adding our db extension to our app
    limiter.init_app(app)
    cache.init_app(app)

    #register blueprints
    app.register_blueprint(members_bp, url_prefix='/members')

    return app
