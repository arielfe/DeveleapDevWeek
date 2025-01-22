import pytest
import requests
import responses
import json
import os
from io import BytesIO
from openpyxl import Workbook
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:5002"

@pytest.fixture
def api_url():
    return BASE_URL

@pytest.fixture
def temp_upload_dir(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    return upload_dir

def test_hello(api_url):
    response = requests.get(f"{api_url}/")
    assert response.status_code == 200
    assert "Hello from server" in response.text

def test_health_check(api_url):
    response = requests.get(f"{api_url}/health")
    data = response.json()
    assert data['status'] == {"status": "OK"}
    assert response.status_code == 200

def test_create_provider(api_url):
    unique_name = f'Test Provider {datetime.now().timestamp()}'
    response = requests.post(
        f"{api_url}/provider",
        json={'name': unique_name}
    )
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert 'name' in data
    assert data['name'] == unique_name

def test_create_duplicate_provider(api_url):
    provider_name = f'Duplicate Test Provider {datetime.now().timestamp()}'
    first_response = requests.post(f"{api_url}/provider", json={'name': provider_name})
    assert first_response.status_code == 201
    
    response = requests.post(
        f"{api_url}/provider",
        json={'name': provider_name}
    )
    assert response.status_code == 409
    data = response.json()
    assert 'error' in data

def test_update_provider(api_url):
    unique_name = f'Original Name {datetime.now().timestamp()}'
    create_response = requests.post(
        f"{api_url}/provider",
        json={'name': unique_name}
    )
    assert create_response.status_code == 201
    data = create_response.json()
    provider_id = data['id']
    
    new_unique_name = f'Updated Name {datetime.now().timestamp()}'
    response = requests.put(
        f"{api_url}/provider/{provider_id}",
        json={'name': new_unique_name}
    )
    assert response.status_code == 200
def test_add_truck(api_url):
    # First create a provider
    unique_name = f'Truck Provider {datetime.now().timestamp()}'
    create_response = requests.post(
        f"{api_url}/provider",
        json={'name': unique_name}
    )
    assert create_response.status_code == 201
    provider_id = create_response.json()['id']

    # Add truck - using a string ID to match db.String(10)
    truck_id = str(int(datetime.now().timestamp()))[-10:]  # Last 10 chars to match db column
    response = requests.post(
        f"{api_url}/truck",
        json={
            'id': truck_id,
            'provider_id': provider_id
        }
    )
    assert response.status_code == 201

def test_update_truck_provider(api_url):
    # Create first provider
    first_provider_name = f'First Provider {datetime.now().timestamp()}'
    provider_response = requests.post(
        f"{api_url}/provider",
        json={'name': first_provider_name}
    )
    assert provider_response.status_code == 201
    first_provider_id = provider_response.json()['id']
    
    # Create truck with microsecond precision for uniqueness
    timestamp = datetime.now().timestamp()
    microseconds = str(int(timestamp * 1000000))  # Include microseconds for more uniqueness
    truck_id = microseconds[-10:]  # Take last 10 digits
    truck_response = requests.post(
        f"{api_url}/truck",
        json={
            'id': truck_id,
            'provider_id': first_provider_id
        }
    )
    assert truck_response.status_code == 201
    
    # Create second provider
    second_provider_name = f'Second Provider {datetime.now().timestamp()}'
    new_provider_response = requests.post(
        f"{api_url}/provider",
        json={'name': second_provider_name}
    )
    assert new_provider_response.status_code == 201
    second_provider_id = new_provider_response.json()['id']
    
    # Update truck's provider
    response = requests.put(
        f"{api_url}/truck/{truck_id}",
        json={
            'provider_id': second_provider_id
        }
    )
    assert response.status_code == 200

def test_upload_rates(api_url, temp_upload_dir):
    wb = Workbook()
    ws = wb.active
    ws.append(['Product', 'Rate', 'Scope'])
    ws.append(['Apple', 100, 'ALL'])
    
    temp_file = temp_upload_dir / "rates.xlsx"
    wb.save(temp_file)
    
    with open(temp_file, 'rb') as f:
        files = {
            'file': ('rates.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        response = requests.post(f"{api_url}/rates", files=files)
    
    assert response.status_code == 201

def test_get_rates(api_url, temp_upload_dir):
    test_upload_rates(api_url, temp_upload_dir)
    
    response = requests.get(f"{api_url}/rates")
    assert response.status_code == 200
    
    if response.status_code == 200:
        temp_download = temp_upload_dir / "downloaded_rates.xlsx"
        with open(temp_download, 'wb') as f:
            f.write(response.content)

@responses.activate
def test_get_truck_details(api_url):
    mock_response = {
        "id": "ABC123",
        "tara": 1000,
        "sessions": [1234, 5678]
    }
    
    responses.add(
        responses.GET,
        f"{api_url}/truck/ABC123",
        json=mock_response,
        status=200
    )
    
    response = requests.get(f"{api_url}/truck/ABC123")
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert 'tara' in data
    assert 'sessions' in data

    response = requests.get(
        f"{api_url}/truck/ABC123?from=20240101000000&to=20240131235959"
    )
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data

def test_create_provider_no_name(api_url):
    response = requests.post(f"{api_url}/provider", json={})
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data

def test_add_truck_invalid_provider(api_url):
    truck_id = f'TEST_TRUCK_{int(datetime.now().timestamp())}'
    response = requests.post(
        f"{api_url}/truck",
        json={'id': truck_id, 'provider_id': 999}
    )
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data

def test_update_nonexistent_truck(api_url):
    response = requests.put(
        f"{api_url}/truck/NONEXIST",
        json={'provider_id': 1}
    )
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data

if __name__ == '__main__':
    pytest.main(['-v'])