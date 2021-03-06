from flask import Flask, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import json, codecs, logging

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# Configure logging
logging.basicConfig(filename='log.txt', level=logging.DEBUG)

# Load config file with necessary information
def config_load():
    with codecs.open('config.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

config = config_load()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = config['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = config['database']

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    @app.before_request
    def restrict_ip_addresses():
        if not request.remote_addr in config['trusted_ips']:
            abort(403) # Forbidden

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app