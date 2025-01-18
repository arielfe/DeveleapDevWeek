from flask import Flask, request, jsonify
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# MySQL Configuration
DB_CONFIG = {
    'host': '172.17.0.2',
    'user': 'nati',
    'password': 'bashisthebest',
    'database': 'weight',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/weight', methods=['GET'])
def get_weight():
    from_param = request.args.get('from', datetime.now().strftime('%Y0101000000'))  # Default: start of current year
    to_param = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))  # Default: now
    filter_param = request.args.get('filter', 'in,out,none')

    # Convert parameters to proper formats
    try:
        from_param = datetime.strptime(from_param, '%Y%m%d%H%M%S')
        to_param = datetime.strptime(to_param, '%Y%m%d%H%M%S')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYYMMDDHHMMSS."}), 400

    filter_values = filter_param.split(',')
    placeholders = ', '.join(['%s'] * len(filter_values))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch data
        query = f"""
            SELECT id, direction, bruto, COALESCE(neto, 'na') as neto, produce, 
                   IF(containers IS NULL OR containers = '', '[]', 
                      CONCAT('[', GROUP_CONCAT(containers), ']')) as containers
            FROM transactions
            WHERE datetime BETWEEN %s AND %s
              AND direction IN ({placeholders})
            GROUP BY id, direction, bruto, neto, produce
        """

        cursor.execute(query, [from_param, to_param] + filter_values)
        results = cursor.fetchall()

        # Format results
        formatted_results = [
            {
                "id": row["id"],
                "direction": row["direction"],
                "bruto": row["bruto"],
                "neto": row["neto"],
                "produce": row["produce"],
                "containers": row["containers"]
            }
            for row in results
        ]

        return jsonify(formatted_results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
