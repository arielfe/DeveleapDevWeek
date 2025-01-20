import pytest
from datetime import datetime
from app import app
import json
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    """Create a test client for the app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    """Mock database connection and cursor"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.fetchall.return_value = []
    mock_conn.commit = MagicMock()
    
    with patch('app.get_db_connection', return_value=mock_conn):
        yield mock_conn, mock_cursor

def test_health_check_success(client, mock_db):
    """Test health check endpoint when database is connected"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "200 OK"}

def test_health_check_failure(client):
    """Test health check endpoint when database connection fails"""
    with patch('app.get_db_connection', side_effect=Exception("Connection failed")):
        response = client.get('/health')
        assert response.status_code == 500
        assert response.json == {"status": "500 Internal Server Error"}

def test_post_weight_invalid_direction(client):
    """Test POST /weight with invalid direction"""
    response = client.post('/weight', json={
        "direction": "invalid",
        "truck": "123-456",
        "containers": "C-1",
        "weight": 1000,
        "unit": "kg"
    })
    
    assert response.status_code == 400
    assert "direction must be" in response.json["message"].lower()

def test_post_weight_missing_truck(client):
    """Test POST /weight with missing truck for 'in' direction"""
    response = client.post('/weight', json={
        "direction": "in",
        "weight": 1000,
        "unit": "kg"
    })
    
    assert response.status_code == 400
    assert "truck id is required" in response.json["message"].lower()

def test_post_weight_invalid_container_format(client):
    """Test POST /weight with invalid container format"""
    response = client.post('/weight', json={
        "direction": "in",
        "truck": "123-456",
        "containers": "C 1, C-2",  # Invalid format with space
        "weight": 1000,
        "unit": "kg"
    })
    
    assert response.status_code == 409
    assert "conflict" in response.json["message"].lower()

def test_post_weight_invalid_unit(client):
    """Test POST /weight with invalid unit"""
    response = client.post('/weight', json={
        "direction": "in",
        "truck": "123-456",
        "containers": "C-1",
        "weight": 1000,
        "unit": "invalid"
    })
    
    assert response.status_code == 400
    assert "unit must be" in response.json["message"].lower()

def test_batch_weight_invalid_file(client):
    """Test POST /batch-weight with invalid file format"""
    response = client.post('/batch-weight', query_string={
        "file": "data.txt"
    })
    
    assert response.status_code == 400
    assert "invalid file type" in response.json["error"].lower()

def test_get_weight_invalid_date_format(client):
    """Test GET /weight with invalid date format"""
    response = client.get('/weight?from=abcdefghijkl&to=202401011200')  
    assert response.status_code == 400
    assert "invalid date format" in response.json["error"].lower()

def test_post_weight_in_after_in(client, mock_db):
    """Test POST /weight with 'in' direction after previous 'in' without force"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, 'in')
    
    response = client.post('/weight', json={
        "direction": "in",
        "truck": "123-456",
        "weight": 1000,
        "unit": "kg",
        "force": "false"
    })
    
    assert response.status_code == 409
    assert "conflict" in response.json["message"].lower()

def test_post_weight_out_without_in(client, mock_db):
    """Test POST /weight with 'out' direction without previous 'in' transaction"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None
    
    response = client.post('/weight', json={
        "direction": "out",
        "truck": "123-456",
        "weight": 800,
        "unit": "kg"
    })
    
    assert response.status_code == 400
    assert "no 'in' transaction found" in response.json["message"].lower()

def test_post_weight_none_after_in(client, mock_db):
    """Test POST /weight with 'none' direction after 'in' transaction"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, 'in')
    
    response = client.post('/weight', json={
        "direction": "none",
        "containers": "C-1",
        "weight": 500,
        "unit": "kg"
    })
    
    assert response.status_code == 400
    assert "cannot record standalone weight after 'in'" in response.json["message"].lower()

def test_get_item_not_found(client, mock_db):
    """Test GET /item/<id> with non-existent item"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {'truck_count': 0, 'container_count': 0}
    
    response = client.get('/item/nonexistent')
    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()

def test_get_session_not_found(client, mock_db):
    """Test GET /session/<id> with non-existent session"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None
    
    response = client.get('/session/999')
    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()