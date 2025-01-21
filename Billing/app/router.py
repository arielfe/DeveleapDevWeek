from flask import Blueprint, jsonify, request, send_file
from app.controller import db,update_provider_controller,add_provider,health_check_controller,add_truck,update_truck_provider,upload_rates_from_excel, Provider, get_truck_details  # Import controllers
import os
from datetime import datetime

# Create a blueprint for provider-related routes
provider_routes = Blueprint("provider_routes", __name__)

@provider_routes.route("/", methods=["GET"])
def hello_from_server():
    return "Hello from server", 200

@provider_routes.route("/provider/<int:id>", methods=["PUT"])
def update_provider(id):
    """
    Route to update an existing provider.
    """
    data = request.json
    if not data:
        return "Provider name is required", 400
    
    new_name = data.get("name")
    response, status_code = update_provider_controller(id, new_name)
    return response, status_code


@provider_routes.route("/provider", methods=["POST"])
def post_provider():

    data = request.json
    if not data or "name" not in data:
        return jsonify({"error": "Provider name is required"}), 400

    provider_name = data["name"]
    response = add_provider(provider_name)
    return response

@provider_routes.route("/health", methods=["GET"])
def health_check():
    status, http_status=health_check_controller()
    return jsonify({"status": status}), http_status

@provider_routes.route("/truck", methods=["POST"])
def post_truck():
    # Get data from request body 
    data = request.json
    # Validate 
    if not data or "provider_id" not in data or "id" not in data:
        return jsonify({"error": "license id and provider id are required"}), 400
    # Extract license id and provider id from  request body
    license_id = data["id"]
    provider_id = data["provider_id"]
    response = add_truck(license_id, provider_id)
    return response

@provider_routes.route("/truck/<id>", methods=["PUT"])
def put_truck(id):
    data = request.json
    if not data or "provider_id" not in data:
        return jsonify({"error": "Provider ID is required"}), 400

    provider_id = data["provider_id"]
    response = update_truck_provider(id, provider_id)
    return response

@provider_routes.route('/rates', methods=['POST'])
def upload_rates():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Save the file to /app/in folder inside the container
    file_path = os.path.join('/app/in', file.filename)
    file.save(file_path)
    
    # Call function to process the uploaded file
    return upload_rates_from_excel(file_path)

@provider_routes.route("/rates", methods=["GET"])
def get_rate():
    try:
        # Excel file location
        file_path = f"/app/in/rates.xlsx"
        return send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'rates.xlsx'
        )
    except FileNotFoundError:
        return jsonify({"error": "Excel file not found"}), 404

@provider_routes.route('/truck/<id>', methods=['GET'])
def get_truck(id):
    from_param = request.args.get('from') or datetime.now().replace(day=1).strftime('%Y%m%d000000')
    to_param = request.args.get('to') or datetime.now().strftime('%Y%m%d%H%M%S')
    result = get_truck_details(id, from_param, to_param)
    if result is None:
        return jsonify({"error": "Truck not found"}), 404
    if result == "error_fetching_data":
        return jsonify({"error": "Failed to fetch truck data"}), 500
    return jsonify(result), 200
    # return jsonify({"message": "Success"}), 200 















