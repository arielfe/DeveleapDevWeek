from flask import Blueprint, jsonify, request
from app.controller import db,update_provider_controller,add_provider, Provider  # Import models

# Create a blueprint for provider-related routes
provider_routes = Blueprint("provider_routes", __name__)


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



