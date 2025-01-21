import pytest
import requests
import os
from app import app
from datetime import datetime

BASE_URL = "http://localhost:5000"  # Updated port to match the Flask app.


def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y%m%d%H%M%S')
        return True
    except ValueError:
        return False








def test_get_unknown_success():
    response = requests.get(f"{BASE_URL}/unknown")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # The response should be a list

def test_get_weight_success():
    response = requests.get(f"{BASE_URL}/weight?from=20250101000000&to=20250120000000&filter=in,out,none")
    assert response.status_code in [200, 201]  # Accept both 200 and 201
    data = response.json()
    assert isinstance(data, list)  # The response should be a list
    if data:  # If there is data, validate structure
        assert "id" in data[0]
        assert "direction" in data[0]
        assert "bruto" in data[0]
        assert "neto" in data[0]
        assert "produce" in data[0]
        assert "containers" in data[0]

def test_get_item_success():
    item_id = "c1001" 
    response = requests.get(f"{BASE_URL}/item/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] == item_id
    assert "tara" in data
    assert "sessions" in data
    assert isinstance(data["sessions"], list)



def test_post_weight_success():
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    response = requests.post(f"{BASE_URL}/weight", json=payload)
    assert response.status_code == 201  # עדכון ל-201 במקום 200
    assert "id" in response.json()
    assert response.json()["truck"] == "12345"


def test_get_session_success():
    session_id = "abc123"  # Replace with a valid session ID from your setup
    response = requests.get(f"{BASE_URL}/session/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert data["id"] == session_id
        assert "truck" in data
        assert "bruto" in data
        assert "neto" in data
    else:
        print(f"Session ID {session_id} not found, received status code {response.status_code}")
        assert response.status_code == 404  # במקרה שאין סשן, יש להחזיר 404

def test_get_item_not_found():
    item_id = "nonexistent_id"
    response = requests.get(f"{BASE_URL}/item/{item_id}")
    assert response.status_code == 404

def test_post_weight_invalid_direction():
    payload = {
        "direction": "invalid",  # invalid direction
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    response = requests.post(f"{BASE_URL}/weight", json=payload)
    assert response.status_code == 400

def test_post_weight_force():
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "kg",
        "force": "true",
        "produce": "orange"
    }
    response = requests.post(f"{BASE_URL}/weight", json=payload)
    assert response.status_code == 201 
    assert "id" in response.json()
    assert response.json()["truck"] == "12345"


def test_post_weight_missing_parameters():
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "unit": "kg",
        "force": "false",
        "produce": "orange"
    }
    response = requests.post(f"{BASE_URL}/weight", json=payload)
    assert response.status_code == 400  


def test_post_weight_invalid_unit():
    payload = {
        "direction": "in",
        "truck": "12345",
        "containers": "cont1,cont2",
        "weight": 1000,
        "unit": "g", 
        "force": "false",
        "produce": "orange"
    }
    response = requests.post(f"{BASE_URL}/weight", json=payload)
    assert response.status_code == 400  


def test_post_batch_weight_invalid_file():
    payload = {'file': 'invalid_file.csv'}
    response = requests.post(f"{BASE_URL}/batch-weight", files=payload)
    assert response.status_code == 400  




