from flask import Blueprint, jsonify, request
from app.controller import db,update_provider_controller,add_provider,health_check_controller,add_truck, Provider  # Import controllers
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
