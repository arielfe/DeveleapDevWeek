import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app import app
import json

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
    assert response.data.decode() == "OK"

def test_health_check_failure(client):
    """Test health check endpoint when database connection fails"""
    with patch('app.get_db_connection', side_effect=Exception("Connection failed")):
        response = client.get('/health')
        assert response.status_code == 500
        assert response.data.decode() == "Failure"

def test_post_weight_in_after_in_with_force(client, mock_db):
    """Test POST /weight with 'in' direction after previous 'in' with force=true"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, 'in')
    
    response = client.post('/weight', json={
        "direction": "in",
        "truck": "123-456",
        "weight": 1000,
        "unit": "kg",
        "force": True
    })
    
    assert response.status_code == 200

def test_post_weight_in_after_in_without_force(client, mock_db):
    """Test POST /weight with 'in' direction after previous 'in' without force"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, 'in')
    
    response = client.post('/weight', json={
        "direction": "in",
        "truck": "123-456",
        "weight": 1000,
        "unit": "kg",
        "force": False
    })
    
    assert response.status_code == 409
    assert "already has an active 'in' session" in response.json["error"].lower()

def test_post_weight_out_after_out_without_force(client, mock_db):
    """Test POST /weight with 'out' direction after previous 'out' without force"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, 'out')
    
    response = client.post('/weight', json={
        "direction": "out",
        "truck": "123-456",
        "weight": 800,
        "unit": "kg",
        "force": False
    })
    
    assert response.status_code == 409
    assert "already has an 'out' session" in response.json["error"].lower()

def test_post_weight_out_after_out_with_force(client, mock_db):
    """Test POST /weight with 'out' direction after previous 'out' with force=true"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1, 'out')
    
    response = client.post('/weight', json={
        "direction": "out",
        "truck": "123-456",
        "weight": 800,
        "unit": "kg",
        "force": True
    })
    
    assert response.status_code == 200

def test_post_weight_out_without_in(client, mock_db):
    """Test POST /weight with 'out' direction without previous 'in'"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None
    
    response = client.post('/weight', json={
        "direction": "out",
        "truck": "123-456",
        "weight": 800,
        "unit": "kg"
    })
    
    assert response.status_code == 400
    assert "no 'in' transaction found" in response.json["error"].lower()

def test_post_weight_complete_flow(client, mock_db):
    """Test complete flow: in -> out"""
    mock_conn, mock_cursor = mock_db
    
    # First 'in' transaction
    mock_cursor.fetchone.return_value = None
    response_in = client.post('/weight', json={
        "direction": "in",
        "truck": "123-456",
        "weight": 1000,
        "unit": "kg"
    })
    assert response_in.status_code == 200
    
    # Then 'out' transaction
    mock_cursor.fetchone.return_value = (1, 'in')
    response_out = client.post('/weight', json={
        "direction": "out",
        "truck": "123-456",
        "weight": 800,
        "unit": "kg"
    })
    assert response_out.status_code == 200

def test_post_weight_missing_required_fields(client, mock_db):
    """Test POST /weight with missing required fields"""
    response = client.post('/weight', json={
        "direction": "in"
        # Missing weight and truck
    })
    
    assert response.status_code == 400
    assert "missing required fields" in response.json["error"].lower()

def test_post_weight_none_without_in(client, mock_db):
    """Test POST /weight with 'none' direction without previous 'in'"""
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None
    
    response = client.post('/weight', json={
        "direction": "none",
        "containers": "C-1",
        "weight": 500,
        "unit": "kg"
    })
    
    assert response.status_code == 200

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
    assert "cannot record 'none' direction after 'in'" in response.json["error"].lower()
