from flask import Flask, request, Response, jsonify
from datetime import datetime
import mysql.connector
import json

"""
Weight Station API
-----------------
This Flask application manages a weighing station system that handles:
1. Truck weighing (entry and exit)
2. Container management
3. Weight calculations and unit conversions
4. Transaction history
5. Data validation and error handling

Database Schema:
- transactions: Stores weight records
- containers_registered: Container reference data
"""

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'nati',
    'password': 'bashisthebest',
    'database': 'weight',
    'port': 3306
}

def get_db_connection():
    """Establishes and returns a MySQL database connection"""
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/weight', methods=['GET'])
def get_weight():
    """
    Retrieves weight records based on time range and direction filters.
    
    Query Parameters:
    - t1 (str): Start time in YYYYMMDDHHMMSS format (default: start of today)
    - t2 (str): End time in YYYYMMDDHHMMSS format (default: current time)
    - filter (str): Comma-separated list of directions (in,out,none)
    
    Returns:
        JSON array of weight records containing:
        - id: Transaction ID
        - direction: Movement direction (in/out/none)
        - bruto: Gross weight in kg
        - neto: Net weight in kg (or "na")
        - produce: Type of produce
        - containers: List of container IDs
    """
    # Merge JSON body and query parameters
    data = request.get_json(silent=True) or {}
    data = {**data, **request.args}

    # Extract parameters with defaults
    from_param = data.get('t1', datetime.now().strftime('%Y%m%d000000'))
    to_param = data.get('t2', datetime.now().strftime('%Y%m%d%H%M%S'))
    filter_param = data.get('filter', 'in,out,none')

    # Convert date parameters to datetime
    try:
        from_param = datetime.strptime(from_param, '%Y%m%d%H%M%S')
        to_param = datetime.strptime(to_param, '%Y%m%d%H%M%S')
    except ValueError:
        response_json = json.dumps({"error": "Invalid date format. Use YYYYMMDDHHMMSS."}, indent=4)
        return Response(response_json, status=400, mimetype='application/json')

    # Prepare filters for SQL IN clause
    filter_values = filter_param.split(',')
    placeholders = ', '.join(['%s'] * len(filter_values))
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = f"""
            SELECT * FROM transactions 
            WHERE datetime BETWEEN %s AND %s 
            AND direction IN ({placeholders})
        """
        cursor.execute(query, (from_param, to_param, *filter_values))
        results = cursor.fetchall()

        # Format results according to API specification
        formatted_results = []
        for row in results:
            formatted_results.append({
                "id": row["id"],
                "direction": row["direction"],
                "bruto": row["bruto"],  # in kg
                "neto": row["neto"] if row["neto"] is not None else "na",
                "produce": row["produce"],
                "containers": f"[{','.join(row['containers'].split(','))}]" if row["containers"] else "[]"
            })

        response_json = json.dumps(formatted_results, separators=(',', ':'))
        return Response(response_json, mimetype='application/json'), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/health', methods=['GET'])
def check_mysql():
    """
    Health check endpoint to verify database connectivity.
    
    Returns:
        200 OK if database is accessible
        500 with error message if database connection fails
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn.is_connected():
            return jsonify({"status": "200 OK"}), 200
    except Exception as e:
        return jsonify({"status": "Failure", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/weight', methods=['POST'])
def weight_post():
    """
    Records weight measurements for trucks and containers.
    
    Handles three scenarios:
    1. Incoming trucks (direction='in'): Records initial bruto weight
    2. Outgoing trucks (direction='out'): Calculates neto weight based on previous 'in' record
    3. Standalone containers (direction='none'): Records container-only weights
    
    Required Parameters:
    - direction: Movement direction ('in'/'out'/'none')
    - weight: Weight value
    - unit: Weight unit ('kg'/'lbs')
    
    Optional Parameters:
    - truck: Truck identifier (required for 'in'/'out' directions)
    - containers: Comma-separated list of container IDs
    - force: Override validation checks if true
    - produce: Type of produce being transported
    
    Returns:
        JSON object containing transaction details:
        - id: Transaction ID
        - truck: Truck identifier
        - bruto: Gross weight
        - truckTara: Truck empty weight (for 'out' direction)
        - neto: Net weight (for 'out' direction)
    """
    # Constants
    lb_to_kg = 0.454  # Conversion factor for pounds to kilograms

    # Merge JSON and query parameters
    data = request.get_json(silent=True) or {}
    data = {**data, **request.args}

    # Extract and validate input parameters
    direction = data.get('direction', 'none')
    truck = data.get('truck', 'na')
    containers_input = data.get('containers', '').split(',')
    weight = data.get('weight')
    unit = data.get('unit')
    force = data.get('force')
    produce = data.get('produce', 'na')

    # Process container input
    if containers_input[0]:
        containers = [cont_input.capitalize() for cont_input in containers_input]
    else:
        containers = []

    # Validate direction
    try:
        direction = direction.lower()
        if direction not in ('in', 'out', 'none'):
            return jsonify({
                "status": "Failure",
                "message": "Direction must be 'in', 'out' or 'none'"
            })
    except Exception:
        return jsonify({
            "status": "Failure",
            "message": "Direction must be 'in', 'out' or 'none'"
        })

    # Validate weight
    try:
        int(weight)
    except Exception:
        return jsonify({
            "status": "Failure",
            "message": "Weight value is required"
        })

    # Validate and process unit
    try:
        unit = unit.lower()
        if unit not in ("lbs", "kg"):
            return jsonify({
                "status": "Failure",
                "message": "Unit must be 'kg' or 'lbs'"
            })
        if unit == "lbs":
            weight = round(int(weight) * lb_to_kg)
    except Exception:
        return jsonify({
            "status": "Failure",
            "message": "Unit must be 'kg' or 'lbs'"
        })

    def cont_weight(containers, lb_to_kg):
        """
        Calculate total weight of containers.
        
        Args:
            containers (list): List of container IDs
            lb_to_kg (float): Conversion factor for pounds to kilograms
            
        Returns:
            list: Weights of containers in kg
            0 if any container is not found
        """
        containers_weight = []
        sql_select = 'SELECT weight, unit FROM containers_registered WHERE container_id = %s'
        for cont in containers:
            cursor.execute(sql_select, (cont,))
            result = cursor.fetchone()
            if result:
                container_weight, unit = result
                if unit.lower() == 'lbs':
                    containers_weight.append(round(container_weight * lb_to_kg))
                elif unit.lower() == 'kg':
                    containers_weight.append(container_weight)
            else:
                return 0
        return containers_weight

    def neto_weight(bruto, truckTara, containers_weight):
        """
        Calculate net weight.
        
        Args:
            bruto (int): Gross weight
            truckTara (int): Truck empty weight
            containers_weight (list): List of container weights
            
        Returns:
            int: Net weight
            None: If container weights are not available
        """
        if containers_weight:
            return int(bruto) - int(truckTara) - sum(containers_weight)
        return None

    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        if direction == 'in':
            # Handle incoming truck
            sql_check = '''
                SELECT id, direction 
                FROM transactions 
                WHERE truck = %s 
                ORDER BY datetime DESC 
                LIMIT 1
            '''
            cursor.execute(sql_check, (truck,))
            last_record = cursor.fetchone()

            # Prevent double 'in' entries unless forced
            if last_record and last_record[1] == 'in' and not force:
                return jsonify({
                    "status": "Failure",
                    "message": f"Conflict: Last record for this truck (ID: {last_record[0]}) is already 'in'. Use force=true to overwrite."
                }), 400
            elif last_record and last_record[1] == 'in' and force:
                sql_delete = 'DELETE FROM transactions WHERE id = %s'
                cursor.execute(sql_delete, (last_record[0],))
                conn.commit()

            # Record entry weight
            bruto = weight
            sql = "INSERT INTO transactions (datetime, direction, truck, containers, bruto, produce) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (datetime.now(), direction, truck, ','.join(containers), bruto, produce)
            cursor.execute(sql, values)
            conn.commit()

            # Get session ID
            sql_select = 'SELECT id FROM transactions WHERE truck = %s ORDER BY datetime DESC LIMIT 1'
            cursor.execute(sql_select, (truck,))
            session_id = cursor.fetchone()[0]
            result = {"id": session_id, "truck": truck, "bruto": bruto}

        elif direction == 'out':
            # Handle outgoing truck
            sql_check = '''
                SELECT id, containers, bruto, produce, direction 
                FROM transactions 
                WHERE truck = %s 
                ORDER BY datetime DESC 
                LIMIT 1
            '''
            cursor.execute(sql_check, (truck,))
            last_record = cursor.fetchone()

            if not last_record:
                return jsonify({
                    "status": "Failure",
                    "message": "No 'in' transaction found for this truck."
                }), 400

            session_id, containers_in, bruto, produce, last_direction = last_record

            # Validate containers match
            if containers and ','.join(containers) != containers_in:
                return jsonify({
                    "status": "Failure",
                    "message": "Containers mismatch: manual check required."
                }), 400
            elif not containers:
                containers = containers_in.split(',')

            # Check for double 'out' entries
            if last_direction == 'out' and not force:
                return jsonify({
                    "status": "Failure",
                    "message": "Conflict: Last record is already 'out'. Use force=true to overwrite."
                }), 400
            elif last_direction == 'out' and force:
                sql_delete = 'DELETE FROM transactions WHERE id = %s'
                cursor.execute(sql_delete, (session_id,))
                conn.commit()

            # Calculate weights
            truckTara = weight
            containers_weight = cont_weight(containers, lb_to_kg)
            neto = neto_weight(bruto, truckTara, containers_weight)
            print(bruto, truckTara, containers_weight, neto)  # Debug print

            # Update previous 'in' transaction
            sql_update = 'UPDATE transactions SET truckTara = %s, neto = %s WHERE id = %s'
            cursor.execute(sql_update, (truckTara, neto, session_id))
            conn.commit()

            # Record exit transaction
            sql_insert = '''
                INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql_insert,
                         (datetime.now(), direction, truck, ','.join(containers), bruto, truckTara, neto, produce))
            conn.commit()

            result = {
                "id": session_id,
                "truck": truck,
                "bruto": bruto,
                "truckTara": truckTara,
                "neto": neto
            }

        elif direction == 'none':
            # Handle standalone container weighing
            sql_check = '''
                SELECT direction 
                FROM transactions 
                ORDER BY datetime DESC 
                LIMIT 1
            '''
            cursor.execute(sql_check)
            last_record = cursor.fetchone()

            # Prevent 'none' after 'in'
            if last_record and last_record[0] == 'in':
                return jsonify({
                    "status": "Failure",
                    "message": "Cannot record standalone weight after 'in' transaction."
                }), 400

            # Calculate weights
            bruto = weight
            truckTara = 0
            containers_weight = cont_weight(containers, lb_to_kg)
            neto = neto_weight(bruto, truckTara, containers_weight)

            # Record transaction
            sql = """
                INSERT INTO transactions 
                (datetime, direction, truck, containers, bruto, truckTara, neto, produce) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (datetime.now(), direction, None, ','.join(containers), bruto, None, neto, produce)
            cursor.execute(sql, values)
            conn.commit()

            # Get session ID
            sql_select = 'SELECT id FROM transactions ORDER BY datetime DESC LIMIT 1'
            cursor.execute(sql_select)
            session_id = cursor.fetchone()[0]

            result = {"id": session_id, "truck": "na", "bruto": bruto}

        response_json = json.dumps(result, indent=4, sort_keys=False)
        return Response(response_json, mimetype='application/json'), 201

    except Exception as e:
        # Handle any errors that occur during processing
        return jsonify({"status": "Failure", "message": str(e)}), 500
    finally:
        # Ensure database connections are properly closed
        if conn:
            conn.close()
        if cursor:
            cursor.close()


if __name__ == '__main__':
    """
    Main entry point for the application.
    Starts the Flask development server on port 5000.
    
    Note:
    - debug=True enables debug mode for development
    - host='0.0.0.0' makes the server publicly available
    """
    app.run(debug=True, host='0.0.0.0', port=5000)