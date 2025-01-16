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

# Route to fetch all data from a table
@app.route('/containers', methods=['GET'])
def get_containers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM containers_registered")
        result = cursor.fetchall()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Route to add data to the table
@app.route('/containers', methods=['POST'])
def add_container():
    data = request.get_json()
    container_id = data.get('container_id')
    weight = data.get('weight')
    unit = data.get('unit')

    if not all([container_id, weight, unit]):
        return jsonify({'error': 'Missing data'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO containers_registered (container_id, weight, unit) VALUES (%s, %s, %s)",
            (container_id, weight, unit)
        )
        conn.commit()
        return jsonify({'message': 'Container added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Route to check if Database Server is available 
@app.route('/health', methods=['GET'])
def check_mysql():
    try:
        # Connecting to Database
        conn = get_db_connection()
        if conn.is_connected():
            conn.close()  # Closing connection
            return jsonify({"status": "OK", "message": "MySQL server is running"}), 200
        
    except Exception as e:
        return jsonify({"status": "Failure", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
