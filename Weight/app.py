from flask import Flask, request, Response
from datetime import datetime
import mysql.connector
import json

app = Flask(__name__)

DB_CONFIG = {
    'host': '172.17.0.2',
    'user': 'nati',
    'password': 'bashisthebest',
    'database': 'weight',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def format_json_response(data):
    for item in data:
        if isinstance(item.get("containers"), str):
            item["containers"] = [c.strip().strip('"') for c in item["containers"].strip('[]').split(',') if c.strip()]
    return json.dumps(data, indent=4)

@app.route('/weight', methods=['GET'])
def get_weight():
    from_param = request.args.get('from', datetime.now().strftime('%Y%m%d000000'))  # Default: start of today
    to_param = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))  # Default: now
    filter_param = request.args.get('filter', 'in,out,none')
    print(from_param)
    print(to_param)
    print(filter_param)

    # Convert date parameters to datetime
    try:
        from_param = datetime.strptime(from_param, '%Y%m%d%H%M%S')
        to_param = datetime.strptime(to_param, '%Y%m%d%H%M%S')
    except ValueError:
        response_json = json.dumps({"error": "Invalid date format. Use YYYYMMDDHHMMSS."}, indent=4)
        return Response(response_json, status=400, mimetype='application/json')

        # Prepare filters
    filter_values = filter_param.split(',')
    placeholders = ', '.join(['%s'] * len(filter_values))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch data from transactions table
        query = f"""
            SELECT * FROM transactions 
            WHERE datetime BETWEEN %s AND %s 
            AND direction IN ({placeholders})
        """
        cursor.execute(query, (from_param, to_param, *filter_values))
        results = cursor.fetchall()

        # Process the results to match the required format
        formatted_results = []
        for row in results:
            formatted_results.append({
                "id": row["id"],
                "direction": row["direction"],
                "bruto": row["bruto"],  # in kg
                "neto": row["neto"] if row["neto"] is not None else "na",  # Replace NULL with "na"
                "produce": row["produce"],
                "containers": f"[{','.join(row['containers'].split(','))}]" if row["containers"] else "[]"   # Split containers into a list
            })

        response_json = json.dumps(formatted_results, separators=(',', ':'))
        return Response(response_json, mimetype='application/json')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
