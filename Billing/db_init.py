import os  # For environment variable handling and checking file existence
import subprocess  # For executing shell commands (e.g., running MySQL dump)
import time  # For retry logic with sleep
from sqlalchemy import text  # For handling raw SQL queries
from sqlalchemy.exc import OperationalError  # For catching database connection errors
from flask_sqlalchemy import SQLAlchemy  # For SQLAlchemy integration with Flask
def initialize_database(app, db, dump_file="billingdb.sql", max_retries=5):
    retry_count = 0
    db_name = os.getenv("DB_NAME", "billdb")  # Default to 'billdb'
    
    while retry_count < max_retries:
        try:
            with app.app_context():
                # Switch to the correct database
                db.session.execute(text(f"USE {db_name};"))  
                
                # Check if tables exist
                result = db.session.execute(text("SHOW TABLES;"))
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
                                db_name  # Use 'billdb'
                            ],
                            stdin=open(dump_file),
                            check=True,
                        )
                        print(f"Database initialized successfully using {dump_file}.")
                    else:
                        print(f"Error: {dump_file} not found.")
                else:
                    print("Database already initialized.")
                break
        except OperationalError as e:
            retry_count += 1
            print(f"Error connecting to the database: {e}")
            print(f"Retrying... ({retry_count}/{max_retries})")
            time.sleep(5)  # Retry after 5 seconds

    if retry_count == max_retries:
        raise Exception("Failed to connect to the database after multiple retries.")
