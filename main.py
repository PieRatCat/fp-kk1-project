import sqlite3
from pyowm import OWM
import os
from dotenv import load_dotenv
import datetime
import logging

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(filename=os.path.join(log_dir, 'app.log'), level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load OWM API key from .env file
load_dotenv()
api_key = os.getenv('OWM_API_KEY')

# Database file
DB_FILE = 'weatherdata.db'

def setup_database(db_file=DB_FILE):
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    sql_create_table ='''
        CREATE TABLE IF NOT EXISTS hbg_weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            temperature REAL NOT NULL
        );
    '''
    cursor.execute(sql_create_table)
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    logging.info("Database setup complete.")

# Fetch weather data from OWM with pyowm https://github.com/csparpa/pyowm

def get_weather_data(place='Helsingborg,SE'):
    """Fetches weather data from OWM."""
    try:
        owm = OWM(api_key)
        mgr = owm.weather_manager()

        # Current weather in Helsingborg
        observation = mgr.weather_at_place(place)
        w = observation.weather

        status = w.detailed_status
        temperature = w.temperature('celsius')
        timestamp = datetime.datetime.now().isoformat()
        
        logging.info(f"Successfully fetched weather data for {place}.")
        return (timestamp, status, temperature['temp'])
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return None

# Insert weather data into the table
def insert_weather(data, db_file=DB_FILE):
    """Inserts weather data into the database."""
    if data is None:
        logging.warning("No weather data to insert.")
        return
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()    
     
    sql_insert = '''
        INSERT INTO hbg_weather (timestamp, status, temperature)
        VALUES (?, ?, ?);
    '''
    try:
        cursor.execute(sql_insert, data)
        conn.commit()
        logging.info("Data inserted successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error inserting data: {e}")
    finally:
        conn.close()

def main():
    """Main function to run the script."""
    setup_database()
    # Get the latest weather data and insert it into the database
    weather_data_to_insert = get_weather_data()
    insert_weather(weather_data_to_insert)

if __name__ == "__main__":
    main()

