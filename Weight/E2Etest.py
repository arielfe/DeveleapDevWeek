import pytest
from flask import Flask
from app.app import app, get_db_connection


@pytest.fixture(autouse=True)
def clear_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM containers_registered")
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    cursor.close()
    conn.close()


@pytest.fixture
def client():
    """
    Pytest fixture to create a test client for the Flask app.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    """
    Test the /health endpoint.
    """
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "200 OK"}


def test_get_weight_no_params(client):
    """
    Test the /weight GET endpoint with no parameters.
    """
    response = client.get('/weight', query_string={"t1": "20250101000000", "t2": "20250120000000"})
    assert response.status_code == 200
    assert isinstance(response.json, list)  # Should return a list of weight records


def test_get_weight_invalid_date(client):
    """
    Test the /weight GET endpoint with invalid date format.
    """
    response = client.get('/weight?t1=invalid&t2=invalid')
    assert response.status_code == 400
    assert "Invalid date format" in response.json["error"]


def test_post_weight_in(client):
    """
    Test the /weight POST endpoint with a valid 'in' request.
    """
    payload = {
        "direction": "in",
        "truck": "1234567",
        "containers": "container1,container2",
        "weight": 10000,
        "unit": "kg",
        "produce": "oranges"
    }
    response = client.post('/weight', json=payload)
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["truck"] == "1234567"


def test_post_weight_out_without_in(client):
    """
    Test the /weight POST endpoint with an 'out' request without a prior 'in' request.
    """
    payload = {
        "direction": "out",
        "truck": "1234567",
        "weight": 9000,
        "unit": "kg"
    }
    response = client.post('/weight', json=payload)
    assert response.status_code == 400
    assert "No 'in' transaction found" in response.json["message"]


def test_get_unknown_containers(client):
    """
    Test the /unknown endpoint to retrieve containers with unknown weight.
    """
    response = client.get('/unknown')
    assert response.status_code == 200
    assert isinstance(response.data, bytes)  # Plain text response
    assert response.data.decode() == "[]"  # No unknown containers by default


def test_batch_weight_invalid_file(client):
    """
    Test the /batch-weight endpoint with an invalid file.
    """
    response = client.post('/batch-weight', query_string={"file": "invalid.txt"})
    assert response.status_code == 400
    assert "Invalid file type" in response.json["error"]


def test_post_weight_invalid_direction(client):
    """
    Test the /weight POST endpoint with an invalid direction.
    """
    payload = {
        "direction": "invalid",
        "truck": "1234567",
        "weight": 10000,
        "unit": "kg"
    }
    response = client.post('/weight', json=payload)
    assert response.status_code == 400
    assert "Direction must be 'in', 'out' or 'none'" in response.json["message"]


def test_post_weight_out_with_in(client):
    """
    Test the /weight POST endpoint with a valid 'in' followed by 'out' request.
    """
    # Step 1: Create 'in' session
    payload_in = {
        "direction": "in",
        "truck": "1234567",
        "weight": 15000,
        "unit": "kg"
    }
    client.post('/weight', json=payload_in)

    # Step 2: Create 'out' session
    payload_out = {
        "direction": "out",
        "truck": "1234567",
        "weight": 9000,
        "unit": "kg"
    }
    response = client.post('/weight', json=payload_out)
    assert response.status_code == 201
    assert "truckTara" in response.json
    assert response.json["neto"] == 6000
