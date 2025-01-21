import os  # For environment variables
from flask import Flask  # Flask application
from app import create_app  # Import the factory function
from db_init import initialize_database  # Database initialization function

# Environment variables for database configuration
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "billdb")

if __name__ == "__main__":
    # Create the Flask app using the factory function
    app = create_app(
        db_uri=f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    
    # Initialize the database
    with app.app_context():
        initialize_database(app, app.extensions["sqlalchemy"].db)


    # Start the Flask development server
    app.run(host="0.0.0.0", port=5001, debug=True)