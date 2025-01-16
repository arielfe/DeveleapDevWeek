from flask import Blueprint, request, jsonify
from app.controller import create_provider
# Create a blueprint for provider-related routes
provider_routes = Blueprint("provider_routes", __name__)

# @provider_routes.route("/provider", methods=["POST"])
# def post_provider():
#     """
#     Route to create a new provider.
#     """
#     # Parse JSON data from the request
#     data = request.json
#     if not data or "name" not in data:
#         return jsonify({"error": "Provider name is required"}), 400
    
#     # Call the controller function to handle business logic
#     provider_name = data["name"]
#     response = create_provider(provider_name)
#     return response
