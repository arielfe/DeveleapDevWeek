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
    response_text = response.data.decode("utf-8")
    assert response_text.startswith("[") and response_text.endswith("]")

    if response_text != "[]":
        try:
            unknown_containers = eval(response_text)
            assert isinstance(unknown_containers, list)
            for item in unknown_containers:
                assert isinstance(item, str)
        except Exception as e:
            assert False, f"Parsing response failed: {e}"

def test_get_weight_success(client):
    response = client.get("/weight?from=20250101000000&to=20250120000000&filter=in,out,none")
    assert response.status_code in [200, 201]
    data = response.get_json()
    assert isinstance(data, list)
    if data:
        assert all(isinstance(item, dict) for item in data)

def test_get_item_success(client):
    item_id = "45646686"
    response = client.get(f"/item/{item_id}")
    assert response.status_code in [200, 404] 
    if response.status_code == 200:
        data = response.get_json()
        assert data  
        assert "id" in data
        assert data["id"] == item_id


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
    data = response.get_json()
    assert data
    assert "id" in data
    assert data["truck"] == "12345"

def test_get_session_success(client):
    session_id = "abc123"
    response = client.get(f"/session/{session_id}")

    if response.status_code == 200:
        data = response.get_json()
        assert data
        assert "id" in data
        assert data["id"] == session_id
    else:
        assert response.status_code == 404

def test_get_item_not_found(client):
    item_id = "nonexistent_id"
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 404

def test_post_weight_invalid_direction(client):
    payload = {
        "direction": "invalid",
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
    data = response.get_json()
    assert data
    assert "id" in data
    assert data["truck"] == "12345"

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
    with patch('app.get_db_connection') as mock_get_db_connection:
        mock_get_db_connection.side_effect = Exception("Database connection failed")
        response = client.get("/health")
        assert response.status_code == 500
        json_response = response.get_json()
        assert json_response["status"] == "Failure"
        assert "Database connection failed" in json_response["message"]

def test_get_health_success(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data == {"status": "200 OK"}
