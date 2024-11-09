import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get database connection details from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    print("Connected to the database!")

    # SQL script to create tables and indices
    create_weather_station_table = """
    CREATE TABLE IF NOT EXISTS "WeatherStation" (
        "Id" SERIAL PRIMARY KEY,
        "Name" VARCHAR NOT NULL,
        "Latitude" FLOAT NOT NULL,
        "Longitude" FLOAT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS "WeatherStation_index_0"
    ON "WeatherStation" ("Id");
    """

    create_weather_datas_table = """
    CREATE TABLE IF NOT EXISTS "WeatherDatas" (
        "Id" SERIAL PRIMARY KEY,
        "WeatherStationId" INTEGER NOT NULL,
        "Timestamp" TIMESTAMPTZ NOT NULL,
        "Current_temperature_2m" FLOAT,
        "Current_relative_humidity_2m" FLOAT,
        "Current_apparent_temperature" FLOAT,
        "Current_is_day" BOOLEAN,
        "Current_precipitation" FLOAT,
        "Current_rain" FLOAT,
        "Current_showers" FLOAT,
        "Current_snowfall" FLOAT,
        "Current_weather_code" INTEGER,
        "Current_cloud_cover" FLOAT,
        "Current_pressure_msl" FLOAT,
        "Current_surface_pressure" FLOAT,
        "Current_wind_speed_10m" FLOAT,
        "Current_wind_direction_10m" FLOAT,
        "Current_wind_gusts_10m" FLOAT,

        -- Hourly Weather Variables
        "Hourly_temperature_2m" FLOAT,
        "Hourly_relative_humidity_2m" FLOAT,
        "Hourly_dew_point_2m" FLOAT,
        "Hourly_apparent_temperature" FLOAT,
        "Hourly_precipitation" FLOAT,
        "Hourly_rain" FLOAT,
        "Hourly_snowfall" FLOAT,
        "Hourly_weather_code" INTEGER,
        "Hourly_cloud_cover_total" FLOAT,
        "Hourly_cloud_cover_low" FLOAT,
        "Hourly_cloud_cover_mid" FLOAT,
        "Hourly_cloud_cover_high" FLOAT,
        "Hourly_pressure_msl" FLOAT,
        "Hourly_surface_pressure" FLOAT,
        "Hourly_vapour_pressure_deficit" FLOAT,
        "Hourly_reference_evapotranspiration" FLOAT,
        "Hourly_wind_speed_10m" FLOAT,
        "Hourly_wind_speed_20m" FLOAT,
        "Hourly_wind_speed_50m" FLOAT,
        "Hourly_wind_speed_100m" FLOAT,
        "Hourly_wind_speed_150m" FLOAT,
        "Hourly_wind_speed_200m" FLOAT,
        "Hourly_wind_direction_10m" FLOAT,
        "Hourly_wind_direction_20m" FLOAT,
        "Hourly_wind_direction_50m" FLOAT,
        "Hourly_wind_direction_100m" FLOAT,
        "Hourly_wind_direction_150m" FLOAT,
        "Hourly_wind_direction_200m" FLOAT,
        "Hourly_wind_gusts_10m" FLOAT,
        "Hourly_temperature_20m" FLOAT,
        "Hourly_temperature_50m" FLOAT,
        "Hourly_temperature_100m" FLOAT,
        "Hourly_temperature_150m" FLOAT,
        "Hourly_temperature_200m" FLOAT,

        -- Daily Weather Variables
        "Daily_weather_code" INTEGER,
        "Daily_max_temperature_2m" FLOAT,
        "Daily_min_temperature_2m" FLOAT,
        "Daily_max_apparent_temperature" FLOAT,
        "Daily_min_apparent_temperature" FLOAT,
        "Daily_sunrise" TIMESTAMPTZ,
        "Daily_sunset" TIMESTAMPTZ,
        "Daily_daylight_duration" INTEGER,
        "Daily_sunshine_duration" INTEGER,
        "Daily_uv_index" FLOAT,
        "Daily_uv_index_clear_sky" FLOAT,
        "Daily_precipitation_sum" FLOAT,
        "Daily_rain_sum" FLOAT,
        "Daily_showers_sum" FLOAT,
        "Daily_snowfall_sum" FLOAT,
        "Daily_precipitation_hours" INTEGER,
        "Daily_precipitation_probability_max" FLOAT,
        "Daily_max_wind_speed_10m" FLOAT,
        "Daily_max_wind_gusts_10m" FLOAT,
        "Daily_dominant_wind_direction_10m" FLOAT,
        "Daily_shortwave_radiation_sum" FLOAT,
        "Daily_reference_evapotranspiration" FLOAT,

        FOREIGN KEY ("WeatherStationId") REFERENCES "WeatherStation" ("Id")
            ON UPDATE NO ACTION ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS "WeatherDatas_index_0"
    ON "WeatherDatas" ("Id");
    """

    create_cities_table = """
    CREATE TABLE IF NOT EXISTS "Cities" (
        "Id" SERIAL PRIMARY KEY,
        "Name" VARCHAR NOT NULL,
        "Latitude" FLOAT NOT NULL,
        "Longitude" FLOAT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS "Cities_index_0"
    ON "Cities" ("Id");
    """

    create_departements_table = """
    CREATE TABLE IF NOT EXISTS "Departements" (
        "Id" SERIAL PRIMARY KEY,
        "Name" VARCHAR NOT NULL,
        "Latitude" FLOAT NOT NULL,
        "Longitude" FLOAT NOT NULL,
        "Numero" VARCHAR NOT NULL
    );
    CREATE INDEX IF NOT EXISTS "Departements_index_0"
    ON "Departements" ("Id");
    """

    # Execute the SQL scripts to create tables and indexes
    cursor.execute(create_weather_station_table)
    cursor.execute(create_weather_datas_table)
    cursor.execute(create_cities_table)
    cursor.execute(create_departements_table)

    # Commit the transaction
    conn.commit()

    print("Tables and indexes created successfully!")

except Exception as e:
    print(f"Error occurred: {e}")
    if conn:
        conn.rollback()

finally:
    # Close the connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("Connection closed.")
