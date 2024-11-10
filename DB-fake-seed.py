import requests
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import json
from itertools import zip_longest
import sys

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
db_params = {
    "dbname": os.getenv('DB_NAME'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "host": os.getenv('DB_HOST'),
    "port": os.getenv('DB_PORT')
}

def seed_city_locations(city_locations):
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        insert_query = """
            INSERT INTO "Cities" ("Name", "Latitude", "Longitude")
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        
        cur.executemany(insert_query, city_locations)
        conn.commit()
        print(f"{cur.rowcount} city locations were successfully inserted.")
        cur.close()
        conn.close()

    except Exception as e:
        print("Error inserting city location data:", e)
        sys.exit(1)

def fetch_french_cities():
    url = "https://geo.api.gouv.fr/communes?fields=nom,centre&format=json&geometry=centre"
    try:
        response = requests.get(url)
        response.raise_for_status()
        cities = response.json()
        return [(city['nom'], city['centre']['coordinates'][1], city['centre']['coordinates'][0]) for city in cities]
    except Exception as e:
        print("Error fetching French cities data:", e)
        sys.exit(1)

def fetch_departments():
    url = "https://gist.githubusercontent.com/Tazeg/e0c05fdb39552010e9d0e8218aa3f23c/raw/792f846499b67f135b274ff54d72260ffad48dfe/depts.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        departments = response.json()
        return departments
    except Exception as e:
        print("Error fetching department data:", e)
        sys.exit(1)

def seed_departments(departments):
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        insert_query = """
            INSERT INTO "Departements" ("Name", "Latitude", "Longitude", "Numero")
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        
        for dept in departments:
            dept_name = dept['nomShort']
            latitude = dept['lat']
            longitude = dept['lng']
            numero = dept['numero']
            cur.execute(insert_query, (dept_name, latitude, longitude, numero))

        conn.commit()
        print(f"{len(departments)} departments were successfully inserted.")
        cur.close()
        conn.close()

    except Exception as e:
        print("Error inserting department data:", e)
        sys.exit(1)

def fetch_weather_stations():
    url = "https://meteo.comptoir.net/api/stations"
    try:
        response = requests.get(url)
        response.raise_for_status()
        stations = response.json().get('stations', [])
        return [(station['name'], station['latitude'], station['longitude']) for station in stations]
    except Exception as e:
        print("Error fetching weather stations data:", e)
        sys.exit(1)

def seed_weather_stations(weather_stations):
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        insert_query = """
            INSERT INTO "WeatherStation" ("Name", "Latitude", "Longitude")
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
                
        cur.executemany(insert_query, weather_stations)
        conn.commit()
        print(f"{cur.rowcount} weather stations were successfully inserted.")
        cur.close()
        conn.close()
    except Exception as e:
        print("Error inserting weather station data:", e)
        sys.exit(1)

def safe_get(data, key, index):
    """ Safely get the indexed item from a list or return None if not possible. """
    value = data.get(key, None)
    if isinstance(value, list) and len(value) > index:
        return value[index]
    return None

def fetch_weather_forecast(latitude, longitude):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,rain,snowfall,weather_code,pressure_msl,surface_pressure,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,et0_fao_evapotranspiration,vapour_pressure_deficit,wind_speed_10m,wind_speed_20m,wind_speed_50m,wind_speed_100m,wind_speed_150m,wind_speed_200m,wind_direction_10m,wind_direction_20m,wind_direction_50m,wind_direction_100m,wind_direction_150m,wind_direction_200m,wind_gusts_10m,temperature_20m,temperature_50m,temperature_100m,temperature_150m,temperature_200m&daily=weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration&start_date={start_date}&end_date={end_date}&models=meteofrance_seamless"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather forecast data for {latitude}, {longitude}:", e)
        sys.exit(1)

def seed_weather_forecast(weather_stations):
    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        insert_query = """
            INSERT INTO "WeatherDatas" (
                "WeatherStationId", "Timestamp", "Current_temperature_2m", "Current_relative_humidity_2m", 
                "Current_apparent_temperature", "Current_is_day", "Current_precipitation", "Current_rain", 
                "Current_showers", "Current_snowfall", "Current_weather_code", "Current_cloud_cover", 
                "Current_pressure_msl", "Current_surface_pressure", "Current_wind_speed_10m", 
                "Current_wind_direction_10m", "Current_wind_gusts_10m", "Hourly_temperature_2m", 
                "Hourly_relative_humidity_2m", "Hourly_dew_point_2m", "Hourly_apparent_temperature", 
                "Hourly_precipitation", "Hourly_rain", "Hourly_snowfall", "Hourly_weather_code", 
                "Hourly_cloud_cover_total", "Hourly_cloud_cover_low", "Hourly_cloud_cover_mid", 
                "Hourly_cloud_cover_high", "Hourly_pressure_msl", "Hourly_surface_pressure", 
                "Hourly_vapour_pressure_deficit", "Hourly_reference_evapotranspiration", "Hourly_wind_speed_10m", 
                "Hourly_wind_speed_20m", "Hourly_wind_speed_50m", "Hourly_wind_speed_100m", 
                "Hourly_wind_speed_150m", "Hourly_wind_speed_200m", "Hourly_wind_direction_10m", 
                "Hourly_wind_direction_20m", "Hourly_wind_direction_50m", "Hourly_wind_direction_100m", 
                "Hourly_wind_direction_150m", "Hourly_wind_direction_200m", "Hourly_wind_gusts_10m", 
                "Hourly_temperature_20m", "Hourly_temperature_50m", "Hourly_temperature_100m", 
                "Hourly_temperature_150m", "Hourly_temperature_200m", "Daily_weather_code", 
                "Daily_max_temperature_2m", "Daily_min_temperature_2m", "Daily_max_apparent_temperature", 
                "Daily_min_apparent_temperature", "Daily_sunrise", "Daily_sunset", "Daily_daylight_duration", 
                "Daily_sunshine_duration", "Daily_uv_index", "Daily_uv_index_clear_sky", "Daily_precipitation_sum", 
                "Daily_rain_sum", "Daily_showers_sum", "Daily_snowfall_sum", "Daily_precipitation_hours", 
                "Daily_precipitation_probability_max", "Daily_max_wind_speed_10m", "Daily_max_wind_gusts_10m", 
                "Daily_dominant_wind_direction_10m", "Daily_shortwave_radiation_sum", "Daily_reference_evapotranspiration"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        
        for station in weather_stations:
            latitude, longitude = station[1], station[2]
            cur.execute('SELECT "Id" FROM "WeatherStation" WHERE "Latitude" = %s AND "Longitude" = %s', (latitude, longitude))
            weather_station_id = cur.fetchone()
            if weather_station_id:
                weather_station_id = weather_station_id[0]
                forecast_data = fetch_weather_forecast(latitude, longitude)
                if forecast_data:
                    daily_times = forecast_data.get('daily', {}).get('time', [])
                    for i, timestamp in enumerate(daily_times):
                        daily_data = [
                            safe_get(forecast_data.get('daily', {}), key, i)
                            for key in [
                                'temperature_2m_max', 'relative_humidity_2m', 'apparent_temperature_max',
                                'is_day', 'precipitation_sum', 'rain_sum', 'showers_sum', 'snowfall_sum',
                                'weather_code', 'cloud_cover', 'pressure_msl', 'surface_pressure',
                                'wind_speed_10m_max', 'wind_direction_10m_dominant', 'wind_gusts_10m_max',
                                'temperature_2m', 'relative_humidity_2m', 'dew_point_2m', 'apparent_temperature',
                                'precipitation', 'rain', 'snowfall', 'weather_code', 'cloud_cover_total',
                                'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high', 'pressure_msl',
                                'surface_pressure', 'vapour_pressure_deficit', 'reference_evapotranspiration',
                                'wind_speed_10m', 'wind_speed_20m', 'wind_speed_50m', 'wind_speed_100m',
                                'wind_speed_150m', 'wind_speed_200m', 'wind_direction_10m', 'wind_direction_20m',
                                'wind_direction_50m', 'wind_direction_100m', 'wind_direction_150m', 'wind_direction_200m',
                                'wind_gusts_10m', 'temperature_20m', 'temperature_50m', 'temperature_100m',
                                'temperature_150m', 'temperature_200m', 'weather_code', 'temperature_2m_max',
                                'temperature_2m_min', 'apparent_temperature_max', 'apparent_temperature_min',
                                'sunrise', 'sunset', 'daylight_duration', 'sunshine_duration', 'uv_index_max',
                                'uv_index_clear_sky_max', 'precipitation_sum', 'rain_sum', 'showers_sum',
                                'snowfall_sum', 'precipitation_hours', 'precipitation_probability_max',
                                'wind_speed_10m_max', 'wind_gusts_10m_max', 'wind_direction_10m_dominant',
                                'shortwave_radiation_sum', 'reference_evapotranspiration'
                            ]
                        ]
                    current_times = forecast_data.get('current', {}).get('time', [])
                    for i, timestamp in enumerate(current_times):
                        current_data = [
                            safe_get(forecast_data.get('current', {}), key, i)
                            for key in [
                                'temperature_2m', 'relative_humidity_2m', 'apparent_temperature', 'is_day', 
                                'precipitation', 'rain', 'showers', 'snowfall', 'weather_code', 'cloud_cover', 
                                'pressure_msl', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m', 
                                'wind_gusts_10m'
                            ]
                        ]
                    hourly_times = forecast_data.get('hourly', {}).get('time', [])
                    for i, timestamp in enumerate(hourly_times):
                        hourly_data = [
                            safe_get(forecast_data.get('hourly', {}), key, i)
                            for key in [
                                'temperature_2m', 'relative_humidity_2m', 'dew_point_2m', 'apparent_temperature', 
                                'precipitation', 'rain', 'snowfall', 'weather_code', 'cloud_cover_total', 
                                'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high', 'pressure_msl', 
                                'surface_pressure', 'vapour_pressure_deficit', 'reference_evapotranspiration', 
                                'wind_speed_10m', 'wind_speed_20m', 'wind_speed_50m', 'wind_speed_100m', 
                                'wind_speed_150m', 'wind_speed_200m', 'wind_direction_10m', 'wind_direction_20m', 
                                'wind_direction_50m', 'wind_direction_100m', 'wind_direction_150m', 
                                'wind_direction_200m', 'wind_gusts_10m', 'temperature_20m', 'temperature_50m', 
                                'temperature_100m', 'temperature_150m', 'temperature_200m'
                            ]
                        ]
                        values = (weather_station_id, timestamp, *current_data, *hourly_data, *daily_data)
                        try:
                            cur.execute(insert_query, values)
                        except Exception as insert_error:
                            print("Insert failed:", insert_error)

        conn.commit()
        print("Weather forecast data was successfully inserted.")
        cur.close()
        conn.close()
    except Exception as e:
        print("Error inserting weather forecast data:", e)
        sys.exit(1)

weather_stations = fetch_weather_stations()
if weather_stations:
    seed_weather_stations(weather_stations)
else:
    print("No weather station data to insert.")
    sys.exit(1)

# Fetch and seed all French city location data
french_cities = fetch_french_cities()
if french_cities:
    seed_city_locations(french_cities)
else:
    print("No French city location data to insert.")
    sys.exit(1)

# Fetch all departments and seed them
departments = fetch_departments()
if departments:
    seed_departments(departments)
else:
    print("No department data to insert.")
    sys.exit(1)

seed_weather_forecast(weather_stations)

try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute("SELECT pg_size_pretty(pg_database_size('laravel'));")
    db_size = cur.fetchone()
    print(f"Database size: {db_size[0]}")
    cur.close()
    conn.close()
except Exception as e:
    print("Error fetching database size:", e)
    sys.exit(1)
