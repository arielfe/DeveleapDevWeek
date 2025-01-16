import os  # For environment variable handling and checking file existence
import subprocess  # For executing shell commands (e.g., running MySQL dump)
import time  # For retry logic with sleep
from sqlalchemy.exc import OperationalError  # For catching database connection errors
from flask_sqlalchemy import SQLAlchemy  # For SQLAlchemy integration with Flask

def initialize_database(app, db, dump_file="billingdb.sql"):
    """
    Initializes the database. If tables don't exist, it populates the database using the provided SQL dump file.
    
    Args:
        app: Flask app instance.
        db: SQLAlchemy database instance.
        dump_file: Path to the SQL dump file.
    """
    with app.app_context():
        try:
            # Check if tables exist
            result = db.session.execute("SHOW TABLES;")
            tables = result.fetchall()
            
            if not tables:  # No tables exist
                print("No tables found. Initializing database...")
                
                if os.path.exists(dump_file):
                    # Execute the SQL dump file
                    subprocess.run(
                        [
                            "mysql",
                            f"-u{os.getenv('DB_USER', 'root')}",
                            f"-p{os.getenv('DB_PASSWORD', 'password')}",
                            f"-h{os.getenv('DB_HOST', 'db')}",
                            os.getenv("DB_NAME", "billing_db")
                        ],
                        stdin=open(dump_file),
                        check=True,
                    )
                    print(f"Database initialized successfully using {dump_file}.")
                else:
                    print(f"Error: {dump_file} not found.")
            else:
                print("Database already initialized.")
        except OperationalError as e:
            print(f"Error connecting to the database: {e}")
            time.sleep(5)  # Retry after 5 seconds
            initialize_database(app, db, dump_file)
