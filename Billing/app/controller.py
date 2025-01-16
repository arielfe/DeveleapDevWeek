from flask import jsonify, request
from Billing import app
from Billing.app import db
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

# def create_provide@app.route('/provider', methods=['POST'])
@app.route('/provider', methods=['POST'])
def add_provider():
    data = request.get_json()  # מקבל את הנתונים בפורמט JSON מהבקשה
    if not data or 'name' not in data:
        return jsonify({'message': 'No name provided'}), 400
    if Provider.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Provider already exists'}), 400

    new_provider = Provider(name=data['name'])
    db.session.add(new_provider)
    db.session.commit()

    return jsonify({'id': new_provider.id, 'name': new_provider.name}), 201


# def add_provider():
#     data = request.get_json()  # מקבל את הנתונים בפורמט JSON מהבקשה
#     if not data or 'name' not in data:
#         return jsonify({'message': 'No name provided'}), 400
#     if Provider.query.filter_by(name=data['name']).first():
#         return jsonify({'message': 'Provider already exists'}), 400
#
#     new_provider = Provider(name=data['name'])
#     db.session.add(new_provider)
#     db.session.commit()
#
#     return jsonify({'id': new_provider.id, 'name': new_provider.name}), 201r(provider_name):
#     """
#     Controller function to create a new provider.
#     """
#     try:
#         # Check if the provider already exists
#         existing_provider = Provider.query.filter_by(name=provider_name).first()
#         if existing_provider:
#             return jsonify({"error": "Provider already exists"}), 400
        
#         # Create and save the new provider
#         new_provider = Provider(name=provider_name)
#         db.session.add(new_provider)
#         db.session.commit()
        
#         return jsonify({"id": new_provider.id, "name": new_provider.name}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": f"Failed to create provider: {str(e)}"}), 500
