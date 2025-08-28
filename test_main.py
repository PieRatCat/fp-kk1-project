import pytest
import sqlite3
import os
from unittest.mock import patch, MagicMock
from main import setup_database, get_weather_data, insert_weather, DB_FILE

# Test database file
TEST_DB_FILE = 'test_weatherdata.db'

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: ensure the test database file does not exist before tests
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    
    # Yield control to the test function
    yield
    
    # Teardown: clean up the test database file after tests
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_setup_database():
    """Test that the database file and table are created."""
    setup_database(db_file=TEST_DB_FILE)
    
    # Check if the database file was created
    assert os.path.exists(TEST_DB_FILE)
    
    # Check if the table was created
    conn = sqlite3.connect(TEST_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hbg_weather';")
    assert cursor.fetchone() is not None
    conn.close()

@patch('main.OWM')
def test_get_weather_data(mock_owm):
    """Test the data retrieval and parsing using a mock."""
    mock_weather = MagicMock()
    mock_weather.detailed_status = 'clouds'
    mock_weather.temperature.return_value = {'temp': 15.0}
    
    mock_mgr = MagicMock()
    mock_mgr.weather_at_place.return_value.weather = mock_weather
    
    mock_owm.return_value.weather_manager.return_value = mock_mgr
    
    data = get_weather_data()
    
    assert data is not None
    assert isinstance(data[0], str) # Check if timestamp is a string
    assert data[1] == 'clouds'
    assert data[2] == 15.0

@patch('main.sqlite3.connect')
def test_insert_weather(mock_connect):
    """Test that the insert function correctly adds data to the database."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    test_data = ('2023-01-01T12:00:00', 'sunny', 20.0)
    
    insert_weather(test_data, db_file=TEST_DB_FILE)
    
    mock_connect.assert_called_once_with(TEST_DB_FILE)
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

def test_insert_weather_with_none_data():
    with patch('main.logging.warning') as mock_logging:
        insert_weather(None)
        mock_logging.assert_called_with("No weather data to insert.")