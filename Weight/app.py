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

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# Route to check if Database Server is available Connecting to Database
@app.route('/health', methods=['GET'])
def check_mysql():
    try:
        mconn = get_db_connection()
        if mconn.is_connected():
            mconn.close()  # Closing connection
            return jsonify({"status": "OK", "message": "MySQL server is running"}), 200
        
    except Exception as e:
        return jsonify({"status": "Failure", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)