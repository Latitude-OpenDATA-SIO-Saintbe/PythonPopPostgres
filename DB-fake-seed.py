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
        select_query = """
            SELECT 1 FROM "Cities" WHERE "Name" = %s AND "Latitude" = %s AND "Longitude" = %s;
        """

        countInsert = 0  # Initialize countInsert

        for city in city_locations:
            cur.execute(select_query, city)
            if not cur.fetchone():
                cur.execute(insert_query, city)
                countInsert += 1  # Use correct increment operator

        conn.commit()
        print(f"{countInsert} city locations were successfully inserted.")
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
        select_query = """
            SELECT 1 FROM "Departements" WHERE "Name" = %s AND "Latitude" = %s AND "Longitude" = %s AND "Numero" = %s;
        """

        countInsert = 0  # Initialize countInsert

        for dept in departments:
            dept_name = dept['nomShort']
            latitude = dept['lat']
            longitude = dept['lng']
            numero = dept['numero']
            cur.execute(select_query, (dept_name, latitude, longitude, numero))
            if not cur.fetchone():
                cur.execute(insert_query, (dept_name, latitude, longitude, numero))
                countInsert += 1  # Use correct increment operator

        conn.commit()
        print(f"{countInsert} departments were successfully inserted.")
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
        select_query = """
            SELECT 1 FROM "WeatherStation" WHERE "Name" = %s AND "Latitude" = %s AND "Longitude" = %s;
        """

        countInsert = 0  # Initialize countInsert

        for station in weather_stations:
            cur.execute(select_query, station)
            if not cur.fetchone():
                cur.execute(insert_query, station)
                countInsert += 1

        conn.commit()
        print(f"{countInsert} weather stations were successfully inserted.")
        cur.close()
        conn.close()
    except Exception as e:
        print("Error inserting weather station data:", e)
        sys.exit(1)

def fetch_weather_forecast(latitude, longitude):
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,rain,snowfall,weather_code,pressure_msl,surface_pressure,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,et0_fao_evapotranspiration,vapour_pressure_deficit,wind_speed_10m,wind_speed_20m,wind_speed_50m,wind_speed_100m,wind_speed_150m,wind_speed_200m,wind_direction_10m,wind_direction_20m,wind_direction_50m,wind_direction_100m,wind_direction_150m,wind_direction_200m,wind_gusts_10m,temperature_20m,temperature_50m,temperature_100m,temperature_150m,temperature_200m&start_date={start_date}&end_date={end_date}&models=meteofrance_seamless"
    try:
        #print(url)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather forecast data for {latitude}, {longitude}:", e)
        sys.exit(1)

def seed_weather_forecast(weather_stations):
    try:
        # Establish database connection
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        insert_query = """
            INSERT INTO "WeatherDatas" (
            "WeatherStationId", "Timestamp", "temperature_2m",
            "relative_humidity_2m", "dew_point_2m", "apparent_temperature",
            "precipitation", "rain", "snowfall", "weather_code",
            "cloud_cover", "cloud_cover_low", "cloud_cover_mid",
            "cloud_cover_high", "pressure_msl", "surface_pressure",
            "vapour_pressure_deficit", "evapotranspiration", "wind_speed_10m",
            "wind_speed_20m", "wind_speed_50m", "wind_speed_100m",
            "wind_speed_150m", "wind_speed_200m", "wind_direction_10m",
            "wind_direction_20m", "wind_direction_50m", "wind_direction_100m",
            "wind_direction_150m", "wind_direction_200m", "wind_gusts_10m",
            "temperature_20m", "temperature_50m", "temperature_100m",
            "temperature_150m", "temperature_200m"
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """

        select_query = """
            SELECT 1 FROM "WeatherDatas" WHERE "WeatherStationId" = %s AND "Timestamp" = %s AND
            "temperature_2m" = %s AND "relative_humidity_2m" = %s AND "dew_point_2m" = %s AND
            "apparent_temperature" = %s AND "precipitation" = %s AND "rain" = %s AND
            "snowfall" = %s AND "weather_code" = %s AND "cloud_cover" = %s AND
            "cloud_cover_low" = %s AND "cloud_cover_mid" = %s AND "cloud_cover_high" = %s AND
            "pressure_msl" = %s AND "surface_pressure" = %s AND "vapour_pressure_deficit" = %s AND
            "evapotranspiration" = %s AND "wind_speed_10m" = %s AND "wind_speed_20m" = %s AND
            "wind_speed_50m" = %s AND "wind_speed_100m" = %s AND "wind_speed_150m" = %s AND
            "wind_speed_200m" = %s AND "wind_direction_10m" = %s AND "wind_direction_20m" = %s AND
            "wind_direction_50m" = %s AND "wind_direction_100m" = %s AND "wind_direction_150m" = %s AND
            "wind_direction_200m" = %s AND "wind_gusts_10m" = %s AND "temperature_20m" = %s AND
            "temperature_50m" = %s AND "temperature_100m" = %s AND "temperature_150m" = %s AND
            "temperature_200m" = %s;
        """

        count_insert = 0  # Initialize count for inserted records

        # Loop through weather stations to fetch and insert forecast data
        for station in weather_stations:
            latitude, longitude = station[1], station[2]
            cur.execute('SELECT "Id" FROM "WeatherStation" WHERE "Latitude" = %s AND "Longitude" = %s', (latitude, longitude))
            weather_station_id = cur.fetchone()

            if weather_station_id:
                weather_station_id = weather_station_id[0]
                forecast_data = fetch_weather_forecast(latitude, longitude)

                if forecast_data:
                    # Extract the hourly times and weather data
                    times = forecast_data.get('hourly', {}).get('time', [])
                    temperature_2m = forecast_data.get('hourly', {}).get('temperature_2m', [])
                    relative_humidity_2m = forecast_data.get('hourly', {}).get('relative_humidity_2m', [])
                    dew_point_2m = forecast_data.get('hourly', {}).get('dew_point_2m', [])
                    apparent_temperature = forecast_data.get('hourly', {}).get('apparent_temperature', [])
                    precipitation = forecast_data.get('hourly', {}).get('precipitation', [])
                    rain = forecast_data.get('hourly', {}).get('rain', [])
                    snowfall = forecast_data.get('hourly', {}).get('snowfall', [])
                    weather_code = forecast_data.get('hourly', {}).get('weather_code', [])
                    cloud_cover = forecast_data.get('hourly', {}).get('cloud_cover', [])
                    cloud_cover_low = forecast_data.get('hourly', {}).get('cloud_cover_low', [])
                    cloud_cover_mid = forecast_data.get('hourly', {}).get('cloud_cover_mid', [])
                    cloud_cover_high = forecast_data.get('hourly', {}).get('cloud_cover_high', [])
                    pressure_msl = forecast_data.get('hourly', {}).get('pressure_msl', [])
                    surface_pressure = forecast_data.get('hourly', {}).get('surface_pressure', [])
                    vapour_pressure_deficit = forecast_data.get('hourly', {}).get('vapour_pressure_deficit', [])
                    evapotranspiration = forecast_data.get('hourly', {}).get('et0_fao_evapotranspiration', [])
                    wind_speed_10m = forecast_data.get('hourly', {}).get('wind_speed_10m', [])
                    wind_speed_20m = forecast_data.get('hourly', {}).get('wind_speed_20m', [])
                    wind_speed_50m = forecast_data.get('hourly', {}).get('wind_speed_50m', [])
                    wind_speed_100m = forecast_data.get('hourly', {}).get('wind_speed_100m', [])
                    wind_speed_150m = forecast_data.get('hourly', {}).get('wind_speed_150m', [])
                    wind_speed_200m = forecast_data.get('hourly', {}).get('wind_speed_200m', [])
                    wind_direction_10m = forecast_data.get('hourly', {}).get('wind_direction_10m', [])
                    wind_direction_20m = forecast_data.get('hourly', {}).get('wind_direction_20m', [])
                    wind_direction_50m = forecast_data.get('hourly', {}).get('wind_direction_50m', [])
                    wind_direction_100m = forecast_data.get('hourly', {}).get('wind_direction_100m', [])
                    wind_direction_150m = forecast_data.get('hourly', {}).get('wind_direction_150m', [])
                    wind_direction_200m = forecast_data.get('hourly', {}).get('wind_direction_200m', [])
                    wind_gusts_10m = forecast_data.get('hourly', {}).get('wind_gusts_10m', [])
                    temperature_20m = forecast_data.get('hourly', {}).get('temperature_20m', [])
                    temperature_50m = forecast_data.get('hourly', {}).get('temperature_50m', [])
                    temperature_100m = forecast_data.get('hourly', {}).get('temperature_100m', [])
                    temperature_150m = forecast_data.get('hourly', {}).get('temperature_150m', [])
                    temperature_200m = forecast_data.get('hourly', {}).get('temperature_200m', [])

                    # Loop through each timestamp (i)
                    for i, timestamp in enumerate(times):
                        # Prepare values for insertion
                        data = [
                            temperature_2m[i], relative_humidity_2m[i], dew_point_2m[i], apparent_temperature[i],
                            precipitation[i], rain[i], snowfall[i], weather_code[i], cloud_cover[i],
                            cloud_cover_low[i], cloud_cover_mid[i], cloud_cover_high[i], pressure_msl[i],
                            surface_pressure[i], vapour_pressure_deficit[i], evapotranspiration[i],
                            wind_speed_10m[i], wind_speed_20m[i], wind_speed_50m[i], wind_speed_100m[i],
                            wind_speed_150m[i], wind_speed_200m[i], wind_direction_10m[i], wind_direction_20m[i],
                            wind_direction_50m[i], wind_direction_100m[i], wind_direction_150m[i],
                            wind_direction_200m[i], wind_gusts_10m[i], temperature_20m[i], temperature_50m[i],
                            temperature_100m[i], temperature_150m[i], temperature_200m[i]
                        ]
                        values = (weather_station_id, timestamp, *data)

                        # Check if data already exists for the given station and timestamp
                        cur.execute(select_query, values)
                        if not cur.fetchone():
                            try:
                                # Insert the data into the database
                                cur.execute(insert_query, values)
                                count_insert += 1
                            except Exception as insert_error:
                                print("Insert failed:", insert_error)

        # Commit the changes
        conn.commit()
        print(f"{count_insert} records were successfully inserted.")
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

#seed_weather_forecast(weather_stations)

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
