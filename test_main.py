from main import setup_database, get_weather_data, insert_weather
import sqlite3
import os
import pytest

# Define the test database file
TEST_DB_FILE = 'test_weatherdata.db'

@pytest.fixture
def test_db():
    """Fixture to set up and tear down a test database."""
    # Ensure the database file does not exist before the test
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    
    # Setup the database for the test
    setup_database(db_file=TEST_DB_FILE)
    
    yield TEST_DB_FILE
    
    # Teardown: remove the database file after the test
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def test_setup_database(test_db):
    """Tests the database setup using a test-specific database."""
    # Check if the database file was created
    assert os.path.exists(test_db)
    
    # Check if the table was created
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hbg_weather';")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == 'hbg_weather'

def test_get_weather_data(mocker):
    """Tests the data retrieval and parsing using pytest-mock."""
    # Create a mock for the OWM object and its methods
    mock_weather = mocker.MagicMock()
    mock_weather.detailed_status = 'clouds'
    mock_weather.temperature.return_value = {'temp': 10}

    mock_observation = mocker.MagicMock()
    mock_observation.weather = mock_weather

    mock_mgr = mocker.MagicMock()
    mock_mgr.weather_at_place.return_value = mock_observation

    # Use mocker to patch the OWM class in the main module
    mock_owm_class = mocker.patch('main.OWM')
    mock_owm_class.return_value.weather_manager.return_value = mock_mgr

    data = get_weather_data()

    assert data is not None
    assert data[1] == 'clouds'
    assert data[2] == 10

def test_insert_weather(test_db):
    """Tests inserting data into the test database."""
    test_data = ('2023-01-01T12:00:00', 'sunny', 20.0)
    insert_weather(test_data, db_file=test_db)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    try:
        # Verify that the data was inserted correctly
        cursor.execute("SELECT * FROM hbg_weather WHERE timestamp = ?", (test_data[0],))
        result = cursor.fetchone()
        assert result is not None
        assert result[1] == test_data[0]
        assert result[2] == test_data[1]
        assert result[3] == test_data[2]
    finally:
        # The fixture will handle the cleanup of the entire database file
        conn.close()