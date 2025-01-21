from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance
db = SQLAlchemy()

def create_app(db_uri=None):
    """
    Flask application factory function.
    
    Args:
        db_uri (str): The database URI string.

    Returns:
        Flask app: The Flask application instance.
    """
    app = Flask(__name__)
    
    # Configure the application
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize plugins
    db.init_app(app)

    # Register blueprints
    from app.router import provider_routes
    app.register_blueprint(provider_routes)

    return app