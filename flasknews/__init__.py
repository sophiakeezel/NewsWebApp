from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from os import environ as env

# Initialize the database and OAuth
db = SQLAlchemy()
oauth = OAuth()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load the appropriate configuration
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory SQLite for testing
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
    else:
        app.secret_key = env.get("APP_SECRET_KEY")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Initialize Auth0
        oauth.register(
            "auth0",
            client_id=env.get("AUTH0_CLIENT_ID"),
            client_secret=env.get("AUTH0_CLIENT_SECRET"),
            client_kwargs={"scope": "openid profile email"},
            server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
        )

    # Initialize extensions
    db.init_app(app)
    oauth.init_app(app)

    # Import routes after app instance is created
    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    return app

