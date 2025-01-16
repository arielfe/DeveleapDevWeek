from flask import jsonify
from app import db  # Import the database instance

# Define a Provider model
class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

class Rate(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    rate = db.Column(db.Integer, default=0)
    scope = db.Column(db.Integer, db.ForeignKey('Provider.id'))  # Relates to Provider.id

class Truck(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('Provider.id'))  # Relates to Provider.id

def update_provider_controller(provider_id, new_name):
    """
    Controller function to update an existing provider's name.
    """
    try:
        # Check if the provider exists
        provider = Provider.query.get(provider_id)
        if not provider:
            return f"Provider with ID {provider_id} not found", 404
        
        # Check if the new name already exists for a different provider
        existing_provider = Provider.query.filter(Provider.name == new_name, Provider.id != provider_id).first()
        if existing_provider:
            return f"Provider name '{new_name}' already exists", 400

        # Update the provider's name
        provider.name = new_name
        db.session.commit()

        return f"Provider {provider_id} updated to '{new_name}'", 200
    except Exception as e:
        # Roll back in case of any errors
        db.session.rollback()
        return f"Failed to update provider: {str(e)}", 500
