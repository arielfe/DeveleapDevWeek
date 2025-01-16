import os  # For environment variables
from flask import Flask  # Flask application
from flask_sqlalchemy import SQLAlchemy  # For database handling
from app.router import provider_routes  # Importing routes from the router
from db_init import initialize_database

# Flask application setup
app = Flask(__name__)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "billing_db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.register_blueprint(provider_routes)


if __name__ == "__main__":
    # Initialize the database
    initialize_database(app, db)
    
    # Start the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)
