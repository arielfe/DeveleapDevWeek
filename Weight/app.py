from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
DB_CONFIG = {
    'host': 'localhost',  # Use the Docker container's network if needed
    'user': 'nati',
    'password': 'bashisthebest',
    'database': 'weight',
    'port': 3306
}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)