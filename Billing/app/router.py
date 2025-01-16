from flask import Blueprint, jsonify, request
from app.controller import db,update_provider_controller, Provider  # Import models

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
