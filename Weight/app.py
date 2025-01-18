from flask import Flask, request, Response
from collections import OrderedDict
from datetime import datetime
import mysql.connector
import json

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

def clean_container_string(container):
    # Remove any extra quotes and escape characters
    return container.strip().strip('"').strip("'").replace('\\"', '').replace('"', '')

def format_json_response(data):
    # First convert to JSON string with indentation
    json_str = json.dumps(data, indent=4)
    
    # Split into lines
    lines = json_str.splitlines()
    
    # Process lines to keep containers on one line
    result = []
    skip_next = 0
    for i, line in enumerate(lines):
        if skip_next > 0:
            skip_next -= 1
            continue
            
        if '"containers": [' in line:
            # Get the containers array content
            containers = []
            j = i + 1
            while ']' not in lines[j]:
                containers.append(clean_container_string(lines[j].strip().strip(',')))
                j += 1
            # Handle the last line properly without including the closing bracket
            last_item = clean_container_string(lines[j].strip().strip(',').strip(']'))
            if last_item:  # Only add if it's not empty
                containers.append(last_item)
            
            # Format containers on one line
            containers_str = line.rstrip('[') + '[' + ', '.join(f'"{c}"' for c in containers if c) + ']'
            result.append(containers_str)
            skip_next = j - i
        else:
            result.append(line)
            
    return '\n'.join(result)

@app.route('/weight', methods=['GET'])
def get_weight():
    from_param = request.args.get('from', datetime.now().strftime('%Y%m%d000000'))  # Default: start of today
    to_param = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))  # Default: now
    filter_param = request.args.get('filter', 'in,out,none')

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

        # SQL query
        query = f"""
            SELECT 
                id, 
                direction, 
                bruto, 
                COALESCE(neto, 'na') as neto, 
                produce, 
                IF(containers IS NULL OR containers = '', '[]', CONCAT('[', GROUP_CONCAT(containers), ']')) as containers
            FROM 
                transactions
            WHERE 
                datetime BETWEEN %s AND %s
                AND direction IN ({placeholders})
            GROUP BY 
                id, direction, bruto, neto, produce
        """
        cursor.execute(query, [from_param, to_param] + filter_values)
        results = cursor.fetchall()

        # Format results with the correct field order
        formatted_results = sorted([
            OrderedDict([
                ("id", row["id"]),
                ("direction", row["direction"]),
                ("bruto", row["bruto"]),
                ("neto", row["neto"] if row["neto"] != "NULL" and row["neto"] is not None else "na"),
                ("produce", row["produce"]),
                ("containers", [clean_container_string(c) for c in row["containers"].strip('[]').split(',') if c] if row["containers"] else [])
            ])
            for row in results
        ], key=lambda x: x["id"])

        # Use custom formatting function
        response_json = format_json_response(formatted_results)
        return Response(response_json, mimetype='application/json')

    except Exception as e:
        response_json = json.dumps({"error": str(e)}, indent=4)
        return Response(response_json, status=500, mimetype='application/json')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)