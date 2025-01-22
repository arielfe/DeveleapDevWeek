import pytest
from app import app
from datetime import datetime
from unittest.mock import patch

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y%m%d%H%M%S')
        return True
    except ValueError:
        return False

def test_get_unknown_success(client):
    response = client.get("/unknown")
    assert response.status_code == 200
    response_text = response.data.decode("utf-8")  # Decode the response text
    assert response_text.startswith("[") and response_text.endswith("]")  # Ensure it's a list-like format

    # Parse the string as a list of strings
    try:
        unknown_containers = eval(response_text)  # Convert the text to a Python list
        assert isinstance(unknown_containers, list)  # Validate it's a list
        for item in unknown_containers:
            assert isinstance(item, str)  # Ensure all items are strings
    except Exception as e:
        assert False, f"Parsing response failed: {e}"

def test_get_weight_success(client):
    response = client.get("/weight?from=20250101000000&to=20250120000000&filter=in,out,none")
    assert response.status_code in [200, 201]  # Accept both 200 and 201
    data = response.get_json()
    assert isinstance(data, list)  # The response should be a list
    if data:  # If there is data, validate structure
        assert "id" in data[0]
        assert "direction" in data[0]
        assert "bruto" in data[0]
        assert "neto" in data[0]
        assert "produce" in data[0]
        assert "containers" in data[0]

def test_get_item_success(client):
    item_id = "c1001"
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert "id" in data
    assert data["id"] == item_id
    assert "tara" in data
    assert "sessions" in data
    assert isinstance(data["sessions"], list)

def test_post_weight_success(client):
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    response = client.post("/weight", json=payload)
    assert response.status_code == 201
    assert "id" in response.get_json()
    assert response.get_json()["truck"] == "12345"

def test_get_session_success(client):
    session_id = "abc123"  # Replace with a valid session ID from your setup
    response = client.get(f"/session/{session_id}")

    if response.status_code == 200:
        data = response.get_json()
        assert "id" in data
        assert data["id"] == session_id
        assert "truck" in data
        assert "bruto" in data
        assert "neto" in data
    else:
        print(f"Session ID {session_id} not found, received status code {response.status_code}")
        assert response.status_code == 404

def test_get_item_not_found(client):
    item_id = "nonexistent_id"
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 404

def test_post_weight_invalid_direction(client):
    payload = {
        "direction": "invalid",  # invalid direction
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    response = client.post("/weight", json=payload)
    assert response.status_code == 400

def test_post_weight_force(client):
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }
    response = client.post("/weight", json=payload)
    assert response.status_code == 201
    assert "id" in response.get_json()
    assert response.get_json()["truck"] == "12345"

def test_post_weight_missing_parameters(client):
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    response = client.post("/weight", json=payload)
    assert response.status_code == 400

def test_post_weight_invalid_unit(client):
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "g",
        "force": "false",
        "produce": "orange"
    }
    response = client.post("/weight", json=payload)
    assert response.status_code == 400

def test_post_batch_weight_invalid_file(client):
    payload = {'file': 'invalid_file.csv'}
    response = client.post("/batch-weight", data=payload)
    assert response.status_code == 400

def test_get_health_failure(client):
    # Mock get_db_connection in the app module
    with patch('app.get_db_connection') as mock_get_db_connection:
        # Simulate a database connection error
        mock_get_db_connection.side_effect = Exception("Database connection failed")

        # Perform the test
        response = client.get("/health")

        # Validate the response
        assert response.status_code == 500
        json_response = response.get_json()
        assert json_response["status"] == "Failure"
        assert "Database connection failed" in json_response["message"]

def test_get_health_success(client):
    response = client.get("/health")
    assert response.status_code == 200  # Status should be 200
    assert response.is_json, "Response is not JSON"  # Ensure response is JSON
    data = response.get_json()
    assert data == {"status": "200 OK"}, f"Unexpected response: {data}"
