from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime  

app = Flask(__name__)

# MySQL Configuration
DB_CONFIG = {
    'host': 'localhost',  # use this first to check the ip : docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "docker cotainer name"
    'user': 'nati',
    'password': 'bashisthebest',
    'database': 'weight',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/weight', methods=['GET'])
def get_weight():
    from_param = request.args.get('from', '20230101000000')
    to_param = request.args.get('to', '20250101000000')
    filter_param = request.args.get('filter', 'in,out,none')

    # Convert from_param and to_param to datetime
    from_param = datetime.strptime(from_param, '%Y%m%d%H%M%S')
    to_param = datetime.strptime(to_param, '%Y%m%d%H%M%S')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch data from `transactions` table
        query = """
            SELECT * FROM transactions 
            WHERE datetime BETWEEN %s AND %s 
            AND direction IN (%s)
        """
        cursor.execute(query, (from_param, to_param, filter_param))
        result = cursor.fetchall()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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