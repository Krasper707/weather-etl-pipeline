import requests
import pandas as pd
import time
import os
import json
import sqlite3
import pandas as pd
def getCoords(city):
    """Returns the Lat/Long of a city using openstreetmap"""
    headers={'user-agent':'my-app/0.0.1'}
    urlcoords=f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    data=requests.get(urlcoords,headers=headers).json()
    if not data:
        return None

    return float(data[0]['lat']),float(data[0]['lon'])

def build_city_coords(cities):
    """Loops through cities to get coords, respecting API rate limits."""
    cityCoordinates = {}
    for city in cities:
        print(f"City: {city}")
        coords = getCoords(city)
        if coords:
            cityCoordinates[city] = coords
        time.sleep(1) 
    return cityCoordinates

def check_or_load(filename,function):
    """Caching system: Loads from file if exists, else runs function and saves."""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        data=function()   
        with open(filename, 'w') as f:
            json.dump(data, f)
        return data
def extract_weather(latitude,longitude):
    """Fetches daily weather forecast from Open-Meteo."""
    url=f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,precipitation_sum"
    response=requests.get(url).json()
    return response

def transform_weather(data,cityname):
    """Cleans the raw json data from 'extract_weather' function """
    today_weather={}
    for key in data['daily']:
        today_weather[key]=data['daily'][key][0]
    today_weather['city_name']=cityname
    today_weather['is_raining']=today_weather['precipitation_sum']>0.0 
    return today_weather

def setup_database(cursor):
    """Creates the table with a composite UNIQUE constraint."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_weather(
            record_date DATE,
            city_name TEXT,
            max_temp FLOAT,
            min_temp FLOAT,
            wind_speed FLOAT,
            wind_gusts FLOAT,
            wind_direction FLOAT,
            precipitation FLOAT,
            is_raining BOOLEAN,
            UNIQUE(record_date, city_name) 
        )
    """)

def load_weather(cursor, clean_data):
    """Inserts a single transformed record into the database."""
    cursor.execute("""
        INSERT OR IGNORE INTO daily_weather VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        clean_data['time'],
        clean_data['city_name'],
        clean_data['temperature_2m_max'],
        clean_data['temperature_2m_min'],
        clean_data['wind_speed_10m_max'],
        clean_data['wind_gusts_10m_max'],
        clean_data['wind_direction_10m_dominant'],
        clean_data['precipitation_sum'],
        clean_data['is_raining']
    ))
if __name__ == "__main__":
    cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat", "New York", "Los Angeles", "Toronto", "Mexico City", "London", "Paris", "Berlin", "Madrid", "Rome", "Tokyo", "Beijing", "Shanghai", "Singapore", "Dubai", "Seoul", "Sydney", "Melbourne", "Cairo", "Lagos", "Johannesburg", "São Paulo", "Buenos Aires", "Santiago"]
    cityCoordinates = check_or_load("cityCoords.json", lambda: build_city_coords(cities))
    conn = sqlite3.connect("coffee_shop.db")
    cursor = conn.cursor()
    setup_database(cursor)
    
    print("\nStarting ETL Pipeline...")
    for city, coords in cityCoordinates.items():
        lat = coords[0]
        lon = coords[1]
        
        try:
            raw_data = extract_weather(lat, lon)
            clean_data = transform_weather(raw_data, city)
            load_weather(cursor, clean_data)
            print(f"Successfully loaded weather for {city}")
        except Exception as e:
            print(f"Failed to process {city}: {e}")
    conn.commit()
    
    print("\nETL Pipeline Complete! Verifying database contents...\n")
    query = "SELECT * FROM daily_weather"
    df = pd.read_sql(query, conn)
    print(df.to_string()) 
    conn.close()
