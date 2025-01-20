from flask import Flask, request, Response, jsonify
from datetime import datetime
import mysql.connector
import json
import os
import csv
from mysql.connector import Error
import time

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
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'nati'),
    'password': os.getenv('DB_PASSWORD', 'bashisthebest'),
    'database': os.getenv('DB_NAME', 'weight'),
    'port': int(os.getenv('DB_PORT', 3306))
}
def wait_for_db(max_retries=30, delay_seconds=2):
    """Wait for database to become available"""
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            conn.close()
            print("Database connection successful!")
            return True
        except Error as err:
            print(f"Attempt {i + 1}/{max_retries}: Database not ready yet... {err}")
            time.sleep(delay_seconds)
    raise Exception("Could not connect to database after maximum retries")


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
        if containers_weight and type(containers_weight) is list:
            return int(bruto) - int(truckTara) - sum(containers_weight)
        elif containers_weight and type(containers_weight) is int:
            return int(bruto) - int(truckTara) - containers_weight
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
            if not containers_weight:
                containers_weight = None
            else:
                containers_weight = sum(cont_weight(containers, lb_to_kg))
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
            result = {"id": session_id, "container": ','.join(containers), "bruto": bruto, "containerTara": containers_weight, "neto": neto}

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

@app.route('/batch-weight', methods=['POST'])
def weight_batch_post():
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'csv', 'json'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def process_csv(csv_file):
        """Process CSV file and extract container weight"""
        containers = []
        containers_check = []
        with open(csv_file, 'r') as file:
            reader = list(csv.reader(file))
            headers = reader[0]
        
        is_unit = False
        
        for unit in headers: # checks if there is 'unit' in file
            if unit.lower() in ['lbs', 'kg']:
                unit = unit.lower()
                is_unit = True
        if not is_unit:
            raise Exception("Invalid CSV format or data")
        
        try:
            for row in reader[1:]:
                container_id = row[0].capitalize()
                containers_check.append(container_id)
                weight = row[1]
                containers.append({"id": container_id, "weight": int(weight), "unit": unit})
        except Exception:
            raise Exception("Invalid CSV format or data")

        return containers, containers_check

    def process_json(json_file):
        """Process JSON file and extract container weight"""
        try:
            with open(json_file, 'r') as json_file:
                data = json.load(json_file)
                containers = []
                containers_check = []
                for item in data:
                    weight = item["weight"]
                    unit = item['unit'].lower()
                    container_id = item['id'].capitalize()
                    if unit not in ['kg', 'lbs']:
                         raise Exception("Invalid JSON format or data")
                    containers.append({"id": container_id, "weight": int(weight), "unit": unit})
                    containers_check.append(container_id)
                return containers, containers_check
        except Exception as e:
            raise Exception("Invalid JSON format or data")

    # Process the file based on its extension
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Get the absolute path of the current script
    file_name = request.args.get('file')
    file = f"{BASE_DIR}/in/{file_name}"
    
    if 'file' not in request.args:
        return jsonify({"error": "No file part in the request"}), 400

    if file_name == '': # checks if the uploaded file has a name (i.e., the user actually selected a file to upload)
        return jsonify({"error": "No file selected for uploading"}), 400

    if not allowed_file(file_name): # checks if the uploaded file is allowed
        return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    conn = None
    cursor = None

    try:
        if file_name.endswith('.csv'):
            containers, containers_check = process_csv(file)
        elif file_name.endswith('.json'):
            containers, containers_check = process_json(file)
        else:
            return jsonify({"error": "Unsupported file format."}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Writing data into database
        for cont in containers:
            sql = "INSERT INTO containers_registered (container_id, weight, unit) VALUES (%s, %s, %s)"
            values = (cont["id"], cont["weight"], cont["unit"])
            cursor.execute(sql, values)
            conn.commit()
        
        # Fetching containers data from 'transactions' db to check for 'neto' nulls due to lack of container info
        sql_select = """SELECT containers, bruto, truckTara
                        FROM transactions 
                        WHERE neto IS NULL 
                        AND direction IN ('out', 'none')"""
        
        cursor.execute(sql_select)
        fetched_transactions = cursor.fetchall()

        for transaction in fetched_transactions:
            containers_str, bruto, truckTara = transaction
            container_ids = containers_str.split(",")  # Splitting string into containers list
            total_weight = 0

            for container_id in container_ids:
                if container_id in containers_check:
                    # Getting container's weight from 'containers_registered'
                    sql_select = """
                        SELECT weight, unit
                        FROM containers_registered 
                        WHERE container_id = %s
                    """
                    cursor.execute(sql_select, (container_id,))
                    fetched_data = cursor.fetchall()
                    if fetched_data:
                        weight, unit = fetched_data[0]
                        if unit == "lbs":
                            lb_to_kg = 0.454  # Converting into kg
                            weight = round(weight * lb_to_kg)
                        total_weight += weight

                    # Counting 'neto' for 'transactions'
                    if total_weight > 0:
                        if truckTara:
                            neto = bruto - truckTara - total_weight
                        else:
                            neto = bruto - total_weight

                        # Updating 'transactions'
                        sql_update = """
                            UPDATE transactions 
                            SET neto = %s 
                            WHERE containers = %s
                        """
                        cursor.execute(sql_update, (neto, containers_str))
                        conn.commit()

        return jsonify({"message": "File processed successfully", "data": containers}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        # Ensure database connections are properly closed
        if conn:
            conn.close()
        if cursor:
            cursor.close()

@app.route('/unknown', methods=['GET'])
def get_unknown_containers():
    """
    Returns a list of all recorded containers that have unknown weight
    
    Returns:
        List of container IDs: ["id1","id2",...]
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all unique containers from transactions
        cursor.execute("""
            SELECT DISTINCT 
                TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(t.containers, ',', numbers.n), ',', -1)) as container_id
            FROM transactions t
            CROSS JOIN (
                SELECT 1 + numbers.n AS n
                FROM (
                    SELECT 0 AS n UNION ALL
                    SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
                    SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
                    SELECT 9
                ) numbers
            ) numbers
            WHERE numbers.n <= LENGTH(t.containers) - LENGTH(REPLACE(t.containers, ',', '')) + 1
            AND t.containers IS NOT NULL 
            AND t.containers != ''
            HAVING container_id != ''
        """)
        transaction_containers = cursor.fetchall()
        
        # Get all known containers
        cursor.execute("SELECT container_id FROM containers_registered")
        registered_containers = cursor.fetchall()
        
        # Create sets for comparison
        transaction_set = {row['container_id'] for row in transaction_containers}
        registered_set = {row['container_id'] for row in registered_containers}
        
        # Find unknown containers (in transactions but not registered)
        unknown_containers = sorted(list(transaction_set - registered_set))
        
        # Format response as plain text
        response = '[' + ','.join(f'"{x}"' for x in unknown_containers) + ']'
        return Response(response, mimetype='text/plain'), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@app.route('/item/<id>', methods=['GET'])
def get_item_details(id):
    # Parse query parameters
    from_param = request.args.get('from', datetime.now().replace(day=1).strftime('%Y%m%d000000'))
    to_param = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))

    conn = None
    cursor = None
    try:
        # Convert date parameters to datetime
        try:
            from_datetime = datetime.strptime(from_param, '%Y%m%d%H%M%S')
            to_datetime = datetime.strptime(to_param, '%Y%m%d%H%M%S')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYYMMDDHHMMSS."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if item exists as truck
        cursor.execute("SELECT COUNT(*) as truck_count FROM transactions WHERE truck = %s", (id,))
        truck_exists = cursor.fetchone()['truck_count'] > 0

        # Check if item exists as container
        cursor.execute("SELECT COUNT(*) as container_count FROM transactions WHERE FIND_IN_SET(%s, containers) > 0", (id,))
        container_exists = cursor.fetchone()['container_count'] > 0

        if not (truck_exists or container_exists):
            return jsonify({"error": "Item not found"}), 404

        # Fetch sessions for the item
        if truck_exists:
            # For trucks, fetch transaction sessions with 'in' direction
            cursor.execute("""
                SELECT id FROM transactions 
                WHERE truck = %s 
                AND datetime BETWEEN %s AND %s
                AND direction = 'in'
                ORDER BY datetime
            """, (id, from_datetime, to_datetime))
            sessions = [row['id'] for row in cursor.fetchall()]

            # Get last known tara (truck empty weight)
            cursor.execute("""
                SELECT truckTara FROM transactions 
                WHERE truck = %s AND truckTara IS NOT NULL
                ORDER BY datetime DESC
                LIMIT 1
            """, (id,))
            last_tara = cursor.fetchone()
            tara = last_tara['truckTara'] if last_tara else "na"

        else:  # container
            # For containers, fetch transaction sessions with 'none' or 'in' direction
            cursor.execute("""
                SELECT id FROM transactions 
                WHERE FIND_IN_SET(%s, containers) > 0
                AND datetime BETWEEN %s AND %s
                AND direction IN ('none', 'in')
                ORDER BY datetime
            """, (id, from_datetime, to_datetime))
            sessions = [row['id'] for row in cursor.fetchall()]

            # For containers, tara is the container's registered weight
            cursor.execute("""
                SELECT weight, unit FROM containers_registered 
                WHERE container_id = %s
            """, (id,))
            container_weight = cursor.fetchone()

            if container_weight:
                # Convert to kg if in lbs
                tara = round(container_weight['weight'] * 0.454) if container_weight['unit'] == 'lbs' else container_weight['weight']
            else:
                tara = "na"

        # Prepare response
        response = {
            "id": id,
            "tara": tara,
            "sessions": sessions
        }

        response_json = json.dumps(response, separators=(',', ':'))
        return Response(response_json, mimetype='application/json')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/session/<id>', methods=['GET'])
def get_session_details(id):
    """
    Fetch details for a specific weighing session based on the 'in' or 'none' direction.

    Args:
        id (str): ID of the transaction.

    Returns:
        JSON object with details of the session:
        For 'in':
        - id: Transaction ID
        - truck: Truck ID or "na"
        - bruto: Gross weight
        - truckTara (if 'out'): Truck empty weight
        - neto (if 'out'): Net weight or "na" if containers are unknown
        For 'none':
        - id: Transaction ID
        - container: Container ID or "na"
        - bruto: Gross weight
        - containerTara: Container weight in kg
        - neto: Net weight or "na"
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch the transaction details
        cursor.execute("SELECT * FROM transactions WHERE id = %s", (id,))
        transaction = cursor.fetchone()

        if not transaction:
            return jsonify({"error": "Session not found"}), 404

        # Check the direction and handle accordingly
        if transaction["direction"] == "in":
            # Handle 'in' direction
            session_details = {
                "id": transaction["id"],
                "truck": transaction["truck"] if transaction["truck"] else "na",
                "bruto": transaction["bruto"]
            }

            # Fetch the corresponding 'out' transaction for the same truck after the 'in' transaction
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE truck = %s AND direction = 'out' AND datetime > %s
                ORDER BY datetime ASC
                LIMIT 1
            """, (transaction["truck"], transaction["datetime"]))

            out_transaction = cursor.fetchone()

            if out_transaction:
                session_details["truckTara"] = out_transaction["truckTara"]
                session_details["neto"] = out_transaction["neto"] if out_transaction["neto"] is not None else "na"

            response_json = json.dumps(session_details, separators=(',', ':'))
            return Response(response_json, mimetype='application/json')

        elif transaction["direction"] == "none":
            # Handle 'none' direction
            containers = transaction["containers"].split(",") if transaction["containers"] else []
            container_id = containers[0] if containers else "na"

            # Fetch container details from containers_registered
            if container_id != "na":
                cursor.execute("""
                    SELECT weight, unit FROM containers_registered WHERE container_id = %s
                """, (container_id,))
                container_details = cursor.fetchone()

                if container_details:
                    weight = container_details["weight"]
                    unit = container_details["unit"]
                    container_tara = round(weight * 0.454) if unit == "lbs" else weight
                else:
                    container_tara = "na"
            else:
                container_tara = "na"

            session_details = {
                "id": transaction["id"],
                "container": container_id,
                "bruto": transaction["bruto"],
                "containerTara": container_tara,
                "neto": transaction["neto"] if transaction["neto"] is not None else "na"
            }

            response_json = json.dumps(session_details, separators=(',', ':'))
            return Response(response_json, mimetype='application/json')

        else:
            return jsonify({"error": "Unsupported direction for this session"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

            
if __name__ == '__main__':
    """
    Main entry point for the application.
    Starts the Flask development server on port 5000.
    
    Note:
    - debug=True enables debug mode for development
    - host='0.0.0.0' makes the server publicly available
    """
    wait_for_db()  # Wait for database before starting
    app.run(debug=True, host='0.0.0.0', port=5000)
