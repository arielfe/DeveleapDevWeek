import pytest
from flask import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import os
import io
from werkzeug.datastructures import FileStorage
from app import app as flask_app

class MockDatabaseCursor:
    """
    Mock database cursor for testing database operations.
    Simulates MySQL cursor behavior with configurable results.
    """
    def __init__(self, dictionary=False):
        self.dictionary = dictionary
        self.connection = MagicMock()
        self.connection.is_connected.return_value = True
        self._results = []
        self._current_result = None
        self._sequence_index = 0
        self.lastrowid = 1
        self._executed_queries = []

    def execute(self, query, args=()):
        """Mock query execution with result tracking"""
        self._executed_queries.append((query, args))
        print(f"Mock executing query: {query}")
        print(f"With args: {args}")
        
        if self._results and self._sequence_index < len(self._results):
            self._current_result = self._results[self._sequence_index]
            self._sequence_index += 1
            
            if isinstance(self._current_result, dict) and "lastrowid" in self._current_result:
                self.lastrowid = self._current_result["lastrowid"]
        return self

    def fetchone(self):
        """Mock single row fetch"""
        print(f"Mock fetchone, returning: {self._current_result}")
        if self._current_result is None:
            return None
            
        if self.dictionary:
            if isinstance(self._current_result, (list, tuple)):
                return dict(zip(['id', 'direction'], self._current_result))
            return self._current_result
        
        if isinstance(self._current_result, dict):
            return tuple(self._current_result.values())
        return self._current_result

    def fetchall(self):
        """Mock multiple row fetch"""
        print(f"Mock fetchall, returning: {self._current_result}")
        if isinstance(self._current_result, list):
            return self._current_result
        elif self._current_result is None:
            return []
        elif isinstance(self._current_result, dict):
            return [self._current_result]
        return [self._current_result]

    def close(self):
        """Mock cursor close operation"""
        pass

    def get_executed_queries(self):
        """Get list of executed queries"""
        return self._executed_queries

    def set_result(self, result):
        """Set single result for next query"""
        self._results = [result]
        self._sequence_index = 0
        self._current_result = result

    def set_results(self, results):
        """Set sequence of results for multiple queries"""
        self._results = results
        self._sequence_index = 0
        self._current_result = results[0] if results else None

@pytest.fixture
def client():
    """Test client fixture"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture
def mock_db():
    """Mock database fixture"""
    cursor = MockDatabaseCursor()
    conn = MagicMock()
    
    def cursor_factory(**kwargs):
        cursor.dictionary = kwargs.get('dictionary', False)
        return cursor
        
    conn.cursor = cursor_factory
    conn.commit.return_value = None
    conn.close.return_value = None
    
    with patch('app.get_db_connection', return_value=conn):
        yield cursor

@pytest.fixture
def sample_weight_data():
    """Sample weight data fixture"""
    return {
        "direction": "in",
        "truck": "T-1234",
        "containers": "C-1,C-2",
        "weight": 1000,
        "unit": "kg",
        "force": False,
        "produce": "tomatoes"
    }

class TestWeightStationAPI:
    """Test suite for Weight Station API endpoints"""

    def test_weight_post_incoming_truck(self, client, mock_db, sample_weight_data):
        """Test incoming truck weight recording"""
        mock_db.dictionary = True
        mock_db.set_results([
            None,  # No existing transaction
            {"lastrowid": 1},  # Insert success
            {
                "id": 1,
                "truck": "T-1234",
                "bruto": 1000,
                "neto": None,
                "direction": "in",
                "containers": "C-1,C-2",
                "produce": "tomatoes"
            }
        ])
        
        mock_datetime = datetime(2025, 1, 21, 12, 0)
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response = client.post('/weight', json=sample_weight_data)
            
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["id"] == 1
        assert data["truck"] == "T-1234"
        assert data["bruto"] == 1000

    def test_complete_weighing_session(self, client, mock_db, sample_weight_data):
        """Test complete weighing cycle (in/out)"""
        mock_db.dictionary = True
        mock_datetime = datetime(2025, 1, 21, 12, 0)
        
        # First weigh-in
        mock_db.set_results([
            None,  # No existing transaction
            {"lastrowid": 1},  # Insert success
            (1, "T-1234", "in", 1000, None, "C-1,C-2", "tomatoes")
        ])
        
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response1 = client.post('/weight', json=sample_weight_data)
            
        assert response1.status_code == 201
        data1 = json.loads(response1.data)
        assert data1["id"] == 1
        assert data1["bruto"] == 1000

        # Weigh-out
        exit_data = {**sample_weight_data, "direction": "out", "weight": 400}
        
        mock_db.set_results([
            (1, "C-1,C-2", 1000, "tomatoes", "in"),  # Previous record
            (100, "kg"),  # C-1 weight
            (220, "kg"),  # C-2 weight
            {"lastrowid": 2},  # Insert success
            {
                "id": 1,
                "truck": "T-1234",
                "bruto": 1000,
                "truckTara": 400,
                "neto": 280
            }
        ])
        
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response2 = client.post('/weight', json=exit_data)
            
        assert response2.status_code == 201
        data2 = json.loads(response2.data)
        assert data2["truckTara"] == 400
        assert data2["neto"] == 280

    def test_get_weight_empty_timerange(self, client, mock_db):
        """Test weight retrieval for empty time range"""
        mock_db.dictionary = True
        mock_db.set_results([
            []  # Empty result set
        ])
        
        response = client.get('/weight?t1=20250101000000&t2=20250102000000')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_weight_post_invalid_direction(self, client):
        """Test error handling for invalid direction"""
        data = {
            "direction": "invalid",
            "truck": "T-1234",
            "weight": 1000,
            "unit": "kg"
        }
        
        response = client.post('/weight', json=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Direction must be" in data["message"]

    def test_weight_post_invalid_unit(self, client):
        """Test error handling for invalid weight unit"""
        data = {
            "direction": "in",
            "truck": "T-1234",
            "weight": 1000,
            "unit": "invalid"
        }
        
        response = client.post('/weight', json=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Unit must be" in data["message"]

    def test_health_check(self, client, mock_db):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "200 OK"

    def test_unknown_containers(self, client, mock_db):
        """Test unknown containers retrieval"""
        mock_db.dictionary = True
        mock_db.set_results([
            [{"container_id": "C-1"}, {"container_id": "C-2"}],  # All containers
            [{"container_id": "C-1"}]  # Registered containers
        ])
        
        response = client.get('/unknown')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert "C-2" in data

    def test_standalone_container_weight(self, client, mock_db):
        """Test standalone container weighing"""
        data = {
            "direction": "none",
            "containers": "C-1",
            "weight": 500,
            "unit": "kg",
            "produce": "tomatoes",
            "force": True
        }
        
        mock_db.dictionary = True
        mock_db.set_results([
            None,  # Initial direction check
            (100, "kg"),  # Container weight lookup
            {"lastrowid": 1},  # Insert record
            {
                "id": 1,
                "container": "C-1",
                "bruto": 500,
                "neto": 400
            }
        ])
        
        response = client.post('/weight', json=data)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "id" in data
        assert data["bruto"] == 500
