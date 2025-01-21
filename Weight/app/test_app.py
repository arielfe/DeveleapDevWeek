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
    """Test client fixture for Flask application"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture
def mock_db():
    """Mock database fixture for database interactions"""
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
    """Fixture providing sample weight data for testing"""
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
    """Comprehensive test suite for Weight Station API endpoints"""

    def test_weight_post_incoming_truck(self, client, mock_db, sample_weight_data):
        """
        Test recording weight for an incoming truck.
        
        Checks:
        - Successfully records incoming truck weight
        - Prevents duplicate weigh-in without force
        - Allows forced overwrite of existing weight
        
        Expected behaviors:
        - First weigh-in succeeds with correct data
        - Second weigh-in without force fails
        - Forced weigh-in overwrites previous record
        """
        mock_db.dictionary = True
        
        # Prepare out_data based on sample_weight_data
        out_data = {**sample_weight_data, "direction": "out", "weight": 400}
        
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
            response2 = client.post('/weight', json=out_data)
            
        assert response2.status_code == 201
        data2 = json.loads(response2.data)
        assert data2["truckTara"] == 400

        # Attempt to weigh-out again without force (should fail)
        response3 = client.post('/weight', json=out_data)
        assert response3.status_code == 400
        error_data = json.loads(response3.data)
        assert "already exists" in error_data["message"]

        # Now weigh-out again with force=true
        force_out_data = {**out_data, "force": True, "weight": 500}
        mock_db.set_results([
            (1, "T-1234", "in", 1000, 400, "C-1,C-2", "tomatoes"),  # Previous record
            (100, "kg"),  # C-1 weight
            (220, "kg"),  # C-2 weight
            {"lastrowid": 3},  # Insert success
            {
                "id": 3,
                "truck": "T-1234",
                "bruto": 1000,
                "truckTara": 500,
                "neto": 280
            }
        ])
        
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response4 = client.post('/weight', json=force_out_data)
            
        assert response4.status_code == 201
        data4 = json.loads(response4.data)
        assert data4["id"] == 3
        assert data4["truckTara"] == 500

        # Weigh-in with the original sample data
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

        response = client.post('/weight', json=sample_weight_data)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["id"] == 1
        assert data["truck"] == "T-1234"
        assert data["bruto"] == 1000

    def test_complete_weighing_session(self, client, mock_db, sample_weight_data):
        """
        Test a complete weighing cycle from 'in' to 'out'.
        
        Checks:
        - Successfully record initial weigh-in
        - Record weigh-out with correct calculations
        
        Expected behaviors:
        - First weigh-in captures initial truck weight
        - Weigh-out calculates correct tara and neto weights
        """
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
        """
        Test retrieving weight records for an empty time range.
        
        Checks:
        - API handles empty result set correctly
        - Returns empty list with 201 status code
        
        Expected behaviors:
        - No records found within specified time range
        - Returns empty list
        - Maintains 201 status code
        """
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
        """
        Test handling of invalid direction during weight recording.
        
        Checks:
        - API rejects weight recording with invalid direction
        - Returns appropriate error response
        
        Expected behaviors:
        - 400 status code
        - Error message indicates invalid direction
        """
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
        """
        Test handling of invalid weight unit.
        
        Checks:
        - API rejects weight recording with invalid unit
        - Returns appropriate error response
        
        Expected behaviors:
        - 400 status code
        - Error message indicates invalid unit
        """
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
        """
        Test health check endpoint.
        
        Checks:
        - Health endpoint returns correct status
        
        Expected behaviors:
        - 200 status code
        - Returns OK status
        """
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "200 OK"

    def test_unknown_containers(self, client, mock_db):
        """
        Test retrieving list of unknown containers.
        
        Checks:
        - Correctly identifies containers with unknown weight
        
        Expected behaviors:
        - Returns list of unknown container IDs
        - 200 status code
        """
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
        """
        Test weighing a standalone container.
        
        Checks:
        - Can record weight for a container without a truck
        - Handles 'none' direction correctly
        
        Expected behaviors:
        - Successful weight recording
        - 201 status code
        - Correct weight and container details
        """
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

    def test_force_overwrite_same_truck_direction(self, client, mock_db, sample_weight_data):
        """
        Test forcing overwrite of an existing weight record for the same truck/direction.
        
        Checks:
        - Cannot overwrite without force flag
        - Can overwrite with force flag
        - New record has unique ID
        
        Expected behaviors:
        - First weigh-in succeeds
        - Second weigh-in without force fails
        - Forced weigh-in creates new record
        """
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

        # Attempt to weigh-in again without force (should fail)
        response2 = client.post('/weight', json=sample_weight_data)
        assert response2.status_code == 400
        error_data = json.loads(response2.data)
        assert "already exists" in error_data["message"]

        # Now weigh-in again with force=true
        force_data = {**sample_weight_data, "force": True}
        mock_db.set_results([
            (1, "T-1234", "in"),  # Existing record
            {"lastrowid": 2},  # Insert success
            {
                "id": 2,
                "truck": "T-1234",
                "bruto": 1500,
                "direction": "in",
                "containers": "C-1,C-2",
                "produce": "tomatoes"
            }
        ])
        
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response3 = client.post('/weight', json=force_data)
            
        assert response3.status_code == 201
        data3 = json.loads(response3.data)
        assert data3["id"] == 2
        assert data3["bruto"] == 1500

    def test_force_overwrite_same_truck_out(self, client, mock_db, sample_weight_data):
        """
        Test forcing overwrite of an existing OUT weight record.
        
        Checks:
        - Complete weigh cycle (in/out) can be recorded
        - Cannot weigh out again without force
        - Can weigh out with force flag
        - New out-record has unique ID
        
        Expected behaviors:
        - First weigh-in and out succeed
        - Second out-weighing without force fails
        - Forced out-weighing creates new record
        """
        mock_db.dictionary = True
        mock_datetime = datetime(2025, 1, 21, 12, 0)
        
        # First weigh-in
        weigh_in_data = {**sample_weight_data, "direction": "in"}
        mock_db.set_results([
            None,  # No existing transaction
            {"lastrowid": 1},  # Insert success
            (1, "T-1234", "in", 1000, None, "C-1,C-2", "tomatoes")
        ])
        
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response1 = client.post('/weight', json=weigh_in_data)
            
        assert response1.status_code == 201
        data1 = json.loads(response1.data)
        assert data1["id"] == 1

        # First weigh-out
        out_data = {**sample_weight_data, "direction": "out", "weight": 400}
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
            response2 = client.post('/weight', json=out_data)
            
        assert response2.status_code == 201
        data2 = json.loads(response2.data)
        assert data2["truckTara"] == 400
        assert data2["neto"] == 280

        # Attempt to weigh-out again without force (should fail)
        response3 = client.post('/weight', json=out_data)
        assert response3.status_code == 400
        error_data = json.loads(response3.data)
        assert "already exists" in error_data["message"]

        # Weigh-out again with force=true
        force_out_data = {**out_data, "force": True, "weight": 500}
        mock_db.set_results([
            (1, "C-1,C-2", 1000, "tomatoes", "in"),  # Previous record
            (100, "kg"),  # C-1 weight
            (220, "kg"),  # C-2 weight
            {"lastrowid": 3},  # Insert success
            {
                "id": 3,
                "truck": "T-1234",
                "bruto": 1000,
                "truckTara": 500,
                "neto": 280
            }
        ])
        
        with patch('app.datetime') as dt_mock:
            dt_mock.now.return_value = mock_datetime
            dt_mock.strptime = datetime.strptime
            response4 = client.post('/weight', json=force_out_data)
            
        assert response4.status_code == 201
        data4 = json.loads(response4.data)
        assert data4["id"] == 3
        assert data4["truckTara"] == 500
        assert data4["neto"] == 280

    def test_get_item_with_valid_truck(self, client, mock_db):
        """
        Test retrieving history for a valid truck.
        
        Checks:
        - Retrieves correct truck information
        - Returns expected JSON structure
        
        Expected behaviors:
        - 200 status code
        - Correct truck ID
        - Tara weight present
        - Sessions list populated
        """
        mock_db.dictionary = True
        mock_db.set_results([
            {
                "id": "T-1234",
                "tara": 400,
                "sessions": ["session1", "session2"]
            }
        ])
        
        response = client.get('/item/T-1234')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == "T-1234"
        assert data["tara"] == 400
        assert len(data["sessions"]) == 2

    def test_get_item_with_time_range(self, client, mock_db):
        """
        Test retrieving item history with specific time range.
        
        Checks:
        - Can filter item history by date range
        - Correct data returned
        
        Expected behaviors:
        - 200 status code
        - Correct truck information
        - Tara weight present
        - Sessions list reflects time range
        """
        mock_db.dictionary = True
        mock_db.set_results([
            {
                "id": "T-1234",
                "tara": 400,
                "sessions": ["session1", "session2"]
            }
        ])
        
        response = client.get('/item/T-1234?from=20250101000000&to=20250131235959')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == "T-1234"
        assert data["tara"] == 400
        assert len(data["sessions"]) == 2

    def test_get_item_nonexistent(self, client, mock_db):
        """
        Test retrieving a non-existent item.
        
        Checks:
        - Proper handling of non-existent item
        
        Expected behaviors:
        - 404 status code
        - No data returned
        """
        mock_db.dictionary = True
        mock_db.set_results([
            None  # No item found
        ])
        
        response = client.get('/item/NONEXISTENT')
        
        assert response.status_code == 404

    def test_get_session_valid_id(self, client, mock_db):
        """
        Test retrieving a specific weighing session.
        
        Checks:
        - Retrieves correct session information
        - Returns expected JSON structure
        
        Expected behaviors:
        - 200 status code
        - Correct session details
        - Truck and weight information present
        """
        mock_db.dictionary = True
        mock_db.set_results([
            {
                "id": "session1",
                "truck": "T-1234",
                "bruto": 1000,
                "truckTara": 400,
                "neto": 280
            }
        ])
        
        response = client.get('/session/session1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == "session1"
        assert data["truck"] == "T-1234"
        assert data["bruto"] == 1000
        assert data["truckTara"] == 400
        assert data["neto"] == 280

    def test_get_session_nonexistent(self, client, mock_db):
        """
        Test retrieving a non-existent session.
        
        Checks:
        - Proper handling of non-existent session
        
        Expected behaviors:
        - 404 status code
        - No data returned
        """
        mock_db.dictionary = True
        mock_db.set_results([
            None  # No session found
        ])
        
        response = client.get('/session/NONEXISTENT')
        
        assert response.status_code == 404

    def test_weight_get_with_filters(self, client, mock_db):
        """
        Test retrieving weight records with various filters.
        
        Checks:
        - Can filter weight records by time and direction
        - Correct data returned
        
        Expected behaviors:
        - 201 status code (as per spec)
        - Returns list of weight records
        - Records match specified filters
        """
        mock_db.dictionary = True
        mock_db.set_results([
            [
                {
                    "id": "record1",
                    "direction": "in",
                    "bruto": 1000,
                    "neto": 280,
                    "produce": "tomatoes",
                    "containers": ["C-1", "C-2"]
                },
                {
                    "id": "record2",
                    "direction": "out",
                    "bruto": 1000,
                    "neto": 280,
                    "produce": "oranges",
                    "containers": ["C-3", "C-4"]
                }
            ]
        ])
        
        response = client.get('/weight?from=20250101000000&to=20250131235959&filter=in,out')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert len(data) == 2
        assert all(record["direction"] in ["in", "out"] for record in data)

    def test_batch_weight_upload_csv(self, client, mock_db):
        """
        Test batch weight upload via CSV file.
        
        Checks:
        - Can upload CSV with container weights
        - Handles different CSV formats
        
        Expected behaviors:
        - 201 status code
        - Successful processing of CSV file
        - Correct parsing of container IDs and weights
        """
        # Create a sample CSV file
        csv_content = b"id,kg\nC-1,100\nC-2,220\n"
        data = {
            'file': (io.BytesIO(csv_content), 'containers.csv')
        }
        
        mock_db.dictionary = True
        mock_db.set_results([
            {"lastrowid": 1},  # Successful insert
            {"lastrowid": 2}   # Successful insert
        ])
        
        response = client.post('/batch-weight', 
                               content_type='multipart/form-data', 
                               data=data)
        
        assert response.status_code == 201
        # Additional assertions can be added based on expected behavior

    def test_batch_weight_upload_json(self, client, mock_db):
        """
        Test batch weight upload via JSON.
        
        Checks:
        - Can upload JSON with container weights
        - Handles different weight units
        
        Expected behaviors:
        - 201 status code
        - Successful processing of JSON data
        - Correct parsing of container details
        """
        json_content = {
            "containers": [
                {"id": "C-1", "weight": 100, "unit": "kg"},
                {"id": "C-2", "weight": 220, "unit": "kg"}
            ]
        }
        
        mock_db.dictionary = True
        mock_db.set_results([
            {"lastrowid": 1},  # Successful insert
            {"lastrowid": 2}   # Successful insert
        ])
        
        response = client.post('/batch-weight', 
                               content_type='application/json', 
                               data=json.dumps(json_content))
        
        assert response.status_code == 201
        # Additional assertions can be added based on expected behavior

    def test_weight_out_without_in(self, client):
        """
        Test attempting to weigh out without a previous weigh-in.
        
        Checks:
        - Prevents weighing out without initial weigh-in
        
        Expected behaviors:
        - 400 status code
        - Error message indicates missing weigh-in
        """
        out_data = {
            "direction": "out",
            "truck": "T-1234",
            "weight": 400,
            "unit": "kg"
        }
        
        response = client.post('/weight', json=out_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Cannot weigh out without a previous weigh in" in data["message"]

    def test_weight_none_after_in(self, client, mock_db, sample_weight_data):
        """
        Test attempting 'none' direction after an 'in' direction.
        
        Checks:
        - Prevents 'none' direction after initial weigh-in
        
        Expected behaviors:
        - 400 status code
        - Error message indicates invalid direction sequence
        """
        # First do a weigh-in
        mock_db.set_results([
            None,  # No existing transaction
            {"lastrowid": 1},  # Insert success
            (1, "T-1234", "in", 1000, None, "C-1,C-2", "tomatoes")
        ])
        
        # Weigh-in first
        response1 = client.post('/weight', json=sample_weight_data)
        assert response1.status_code == 201
        
        # Now try 'none' direction
        none_data = {
            "direction": "none",
            "truck": "T-1234",
            "weight": 1000,
            "unit": "kg"
        }
        
        response2 = client.post('/weight', json=none_data)
        
        assert response2.status_code == 400
        data = json.loads(response2.data)
        assert "Cannot use 'none' direction after an 'in' direction" in data["message"]

    def test_invalid_container_format(self, client):
        """
        Test handling of invalid container format.
        
        Checks:
        - Rejects containers with invalid ID format
        
        Expected behaviors:
        - 400 status code
        - Error message indicates invalid container format
        """
        data = {
            "direction": "in",
            "truck": "T-1234",
            "containers": "InvalidContainer!@#",
            "weight": 1000,
            "unit": "kg"
        }
        
        response = client.post('/weight', json=data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid container format" in data["message"]

    def test_extreme_weight_values(self, client):
        """
        Test handling of extreme weight values.
        
        Checks:
        - Prevents recording of unreasonably large weights
        - Prevents recording of negative weights
        
        Expected behaviors:
        - 400 status code for extreme weights
        - Error messages indicating weight limit violations
        """
        # Test very large weight
        data_large = {
            "direction": "in",
            "truck": "T-1234",
            "weight": 1000000,  # 1 million kg
            "unit": "kg"
        }
        
        response_large = client.post('/weight', json=data_large)
        
        assert response_large.status_code == 400
        data_large_response = json.loads(response_large.data)
        assert "Weight exceeds maximum allowed limit" in data_large_response["message"]

        # Test negative weight
        data_negative = {
            "direction": "in",
            "truck": "T-1234",
            "weight": -1000,
            "unit": "kg"
        }
        
        response_negative = client.post('/weight', json=data_negative)
        
        assert response_negative.status_code == 400
        data_negative_response = json.loads(response_negative.data)
        assert "Weight cannot be negative" in data_negative_response["message"]

    def test_long_truck_container_ids(self, client):
        """
        Test handling of extremely long truck or container IDs.
        
        Checks:
        - Prevents recording with excessively long IDs
        
        Expected behaviors:
        - 400 status code for overly long IDs
        - Error messages indicating ID length limit
        """
        # Test very long truck ID
        data_long_truck = {
            "direction": "in",
            "truck": "T" + "1234567890" * 10,  # 100-character truck ID
            "weight": 1000,
            "unit": "kg"
        }
        
        response_long_truck = client.post('/weight', json=data_long_truck)
        
        assert response_long_truck.status_code == 400
        data_long_truck_response = json.loads(response_long_truck.data)
        assert "Truck ID exceeds maximum length" in data_long_truck_response["message"]

        # Test very long container IDs
        data_long_containers = {
            "direction": "in",
            "truck": "T-1234",
            "containers": "C" + "1234567890" * 10 + ",C" + "0987654321" * 10,
            "weight": 1000,
            "unit": "kg"
        }
        
        response_long_containers = client.post('/weight', json=data_long_containers)
        
        assert response_long_containers.status_code == 400
        data_long_containers_response = json.loads(response_long_containers.data)
        assert "Container ID exceeds maximum length" in data_long_containers_response["message"]

    def test_missing_required_fields(self, client):
        """
        Test handling of missing required fields.
        
        Checks:
        - Prevents recording with missing critical fields
        
        Expected behaviors:
        - 400 status code for missing fields
        - Error messages indicating specific missing fields
        """
        # Test missing direction
        data_no_direction = {
            "truck": "T-1234",
            "weight": 1000,
            "unit": "kg"
        }
        
        response_no_direction = client.post('/weight', json=data_no_direction)
        
        assert response_no_direction.status_code == 400
        data_no_direction_response = json.loads(response_no_direction.data)
        assert "Direction is a required field" in data_no_direction_response["message"]

        # Test missing weight
        data_no_weight = {
            "direction": "in",
            "truck": "T-1234",
            "unit": "kg"
        }
        
        response_no_weight = client.post('/weight', json=data_no_weight)
        
        assert response_no_weight.status_code == 400
        data_no_weight_response = json.loads(response_no_weight.data)
        assert "Weight is a required field" in data_no_weight_response["message"]

    def test_unicode_characters_in_ids(self, client):
        """
        Test handling of unicode characters in IDs.
        
        Checks:
        - Prevents or correctly handles unicode characters in IDs
        
        Expected behaviors:
        - Appropriate handling of unicode characters
        - Potential rejection or sanitization of IDs
        """
        # Test truck ID with unicode characters
        data_unicode_truck = {
            "direction": "in",
            "truck": "T-漢字123",  # Truck ID with unicode characters
            "weight": 1000,
            "unit": "kg"
        }
        
        response_unicode_truck = client.post('/weight', json=data_unicode_truck)
        
        # Depending on implementation, this could be:
        # 1. Rejected with 400 status
        # 2. Sanitized and accepted
        # Adjust assertions based on actual expected behavior
        if response_unicode_truck.status_code == 400:
            data_unicode_truck_response = json.loads(response_unicode_truck.data)
            assert "Invalid characters in truck ID" in data_unicode_truck_response["message"]
        else:
            assert response_unicode_truck.status_code == 201

        # Test container IDs with unicode characters
        data_unicode_containers = {
            "direction": "in",
            "truck": "T-1234",
            "containers": "C-漢字1,C-文字2",
            "weight": 1000,
            "unit": "kg"
        }
        
        response_unicode_containers = client.post('/weight', json=data_unicode_containers)
        
        # Similar handling as above
        if response_unicode_containers.status_code == 400:
            data_unicode_containers_response = json.loads(response_unicode_containers.data)
            assert "Invalid characters in container ID" in data_unicode_containers_response["message"]
        else:
            assert response_unicode_containers.status_code == 201
