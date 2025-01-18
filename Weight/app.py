from flask import Flask, request, Response, jsonify
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

@app.route('/weight', methods=['GET'])
def get_weight():
    # Merge JSON body and query parameters
    data = request.get_json(silent=True) or {}
    data = {**data, **request.args}

    # Extract parameters with defaults
    from_param = data.get('t1', datetime.now().strftime('%Y%m%d000000'))  # Default: start of today
    to_param = data.get('t2', datetime.now().strftime('%Y%m%d%H%M%S'))  # Default: now
    filter_param = data.get('filter', 'in,out,none')

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

@app.route('/health', methods=['GET'])
def check_mysql():
    """Route to check if Database Server is available Connecting to Database"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn.is_connected():
            conn.close()
            return jsonify({"status": "200 OK"}), 200

    except Exception as e:
        return jsonify({"status": "Failure", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()
    

@app.route('/weight', methods=['POST'])
def weight_post():
    lb_to_kg = 0.454 # for converting lbs into kg

    data = request.get_json(silent=True) or {}
    data = {**data, **request.args} # Gets json input as well as params input

    direction = data.get('direction', 'none')
    truck = data.get('truck', 'na')
    containers_input = data.get('containers', '').split(',')
    weight = data.get('weight')
    unit = data.get('unit')
    force = data.get('force')
    produce = data.get('produce', 'na')

    if containers_input[0]: # Converting 'containers' input into standard form
        containers = []
        for cont_input in containers_input:
            containers.append(cont_input.capitalize())
    else:
        containers = []


    try: # checking if 'direction' is provided
        direction = direction.lower()
        if direction not in ('in', 'out', 'none'):
            return jsonify({
                    "status": "Failure",
                    "message": "You need to provide 'direction': 'in', 'out' or 'none' for standalone container!"
                })
    except Exception:
        return jsonify({
                    "status": "Failure",
                    "message": "You need to provide 'direction': 'in', 'out' or 'none' for standalone container!"
                })
    
    try: # checking if 'weight' value is provided
        int(weight)
    except Exception:
        return jsonify({
                    "status": "Failure",
                    "message": "You need to provide 'weight'!"
                }) 

    try: # checking if 'unit' is provided
        unit = unit.lower()
        if unit not in ("lbs", "kg"):
            return jsonify({
                    "status": "Failure",
                    "message": "You need to provide 'unit': 'kg' or 'lbs'!"
                })
        if unit == "lbs": # if 'unit' in 'lbs' - converts into kg
            weight = round(int(weight) * lb_to_kg)
    except Exception:
        return jsonify({
                    "status": "Failure",
                    "message": "You need to provide 'unit': 'kg' or 'lbs'!"
                }) 
    
    def cont_weight(containers, lb_to_kg):
        """Counts containers weight"""
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
        """Counts neto"""
        if containers_weight:
            return int(bruto) - int(truckTara) - sum(containers_weight)
        else:
            return None
    
    try:
        conn = None
        cursor = None
        conn = get_db_connection()
        cursor = conn.cursor()

        if direction == 'in':
            sql_check = '''
                SELECT id, direction 
                FROM transactions 
                WHERE truck = %s 
                ORDER BY datetime DESC 
                LIMIT 1
            '''
            cursor.execute(sql_check, (truck,))
            last_record = cursor.fetchone()

            if last_record and last_record[1] == 'in' and not force:
                return jsonify({
                    "status": "Failure",
                    "message": f"Conflict: Last record for this truck (ID: {last_record[0]}) is already 'in'. Use force=true to overwrite."
                }), 400
            elif last_record and last_record[1] == 'in' and force:
                sql_delete = 'DELETE FROM transactions WHERE id = %s'
                cursor.execute(sql_delete, (last_record[0],))
                conn.commit()

            bruto = weight
            sql = "INSERT INTO transactions (datetime, direction, truck, containers, bruto, produce) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (datetime.now(), direction, truck, ','.join(containers), bruto, produce)
            cursor.execute(sql, values)
            conn.commit()

            sql_select = 'SELECT id FROM transactions WHERE truck = %s ORDER BY datetime DESC LIMIT 1'
            cursor.execute(sql_select, (truck,))
            session_id = cursor.fetchone()[0]
            result = {"id": session_id, "truck": truck, "bruto": bruto}

        elif direction == 'out':
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

            # checks 'containers' input
            if containers and ','.join(containers) != containers_in:
                return jsonify({
                    "status": "Failure",
                    "message": "Containers issue: a manual check is required."
                }), 400
            elif not containers:
                containers = containers_in.split(',') # if it's empty string - 'in' data for this truck is used

            # Check if the last transaction was 'out'
            if last_direction == 'out' and not force:
                return jsonify({
                    "status": "Failure",
                    "message": "Conflict: Last record for this truck is already 'out'. Use force=true to overwrite."
                }), 400
            elif last_direction == 'out' and force:
                # Delete the last 'out' transaction if force is true
                sql_delete = '''
                            DELETE FROM transactions 
                            WHERE id = %s
                        '''
                cursor.execute(sql_delete, (session_id,))
                conn.commit()

            # Process the 'out' transaction
            truckTara = weight  
            containers_weight = cont_weight(containers, lb_to_kg)
            neto = neto_weight(bruto, truckTara, containers_weight)
            print(bruto, truckTara, containers_weight, neto)

            # Update the previous 'in' transaction with truckTara and neto
            sql_update = 'UPDATE transactions SET truckTara = %s, neto = %s WHERE id = %s'
            cursor.execute(sql_update, (truckTara, neto, session_id))
            conn.commit()

            # Insert the new 'out' transaction
            sql_insert = '''
                        INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    '''
            cursor.execute(sql_insert,
                             (datetime.now(), direction, truck, ','.join(containers), bruto, truckTara, neto, produce))
            conn.commit()

            # Build the result
            result = {
                "id": session_id,
                "truck": truck,
                "bruto": bruto,
                "truckTara": truckTara,
                "neto": neto
            }

        elif direction == 'none':

            # Check the last transaction in the table
            sql_check = '''
                SELECT direction 
                FROM transactions 
                ORDER BY datetime DESC 
                LIMIT 1
            '''

            cursor.execute(sql_check)
            last_record = cursor.fetchone()

            # Check if the last transaction was 'in'
            if last_record and last_record[0] == 'in':
                return jsonify({
                    "status": "Failure",
                    "message": "Conflict: The last transaction in the table was 'in'. A 'none' transaction cannot follow an 'in' transaction."
                }), 400

            bruto = weight
            truckTara = 0
            containers_weight = cont_weight(containers, lb_to_kg)
            neto = neto_weight(bruto, truckTara, containers_weight)
            truck = None  # Explicitly set truck to None for direction='none'
            truckTara = None

            # Write the transaction into the database
            sql = "INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (datetime.now(), direction, truck, ','.join(containers), bruto, truckTara, neto, produce)
            cursor.execute(sql, values)
            conn.commit()

            # Fetch the transaction ID
            sql_select = 'SELECT id FROM transactions ORDER BY datetime DESC LIMIT 1'
            cursor.execute(sql_select)
            session_id = cursor.fetchone()[0]

            # Build the response
            # "containers": containers,  # Optional: Include container details
            result = {"id": session_id, "truck": "na", "bruto": bruto}

        response_json = json.dumps(result, indent=4, sort_keys=False)
        return Response(response_json, mimetype='application/json'), 201

    except Exception as e:
        return jsonify({"status": "Failure", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
