import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import sys

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
        "Timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,

        -- Hourly Weather Variables
        "temperature_2m" FLOAT,
        "relative_humidity_2m" FLOAT,
        "dew_point_2m" FLOAT,
        "apparent_temperature" FLOAT,
        "precipitation" FLOAT,
        "rain" FLOAT,
        "snowfall" FLOAT,
        "weather_code" INTEGER,
        "cloud_cover" FLOAT,
        "cloud_cover_low" FLOAT,
        "cloud_cover_mid" FLOAT,
        "cloud_cover_high" FLOAT,
        "pressure_msl" FLOAT,
        "surface_pressure" FLOAT,
        "vapour_pressure_deficit" FLOAT,
        "evapotranspiration" FLOAT,
        "wind_speed_10m" FLOAT,
        "wind_speed_20m" FLOAT,
        "wind_speed_50m" FLOAT,
        "wind_speed_100m" FLOAT,
        "wind_speed_150m" FLOAT,
        "wind_speed_200m" FLOAT,
        "wind_direction_10m" FLOAT,
        "wind_direction_20m" FLOAT,
        "wind_direction_50m" FLOAT,
        "wind_direction_100m" FLOAT,
        "wind_direction_150m" FLOAT,
        "wind_direction_200m" FLOAT,
        "wind_gusts_10m" FLOAT,
        "temperature_20m" FLOAT,
        "temperature_50m" FLOAT,
        "temperature_100m" FLOAT,
        "temperature_150m" FLOAT,
        "temperature_200m" FLOAT,

        FOREIGN KEY ("WeatherStationId") REFERENCES "WeatherStation" ("Id")
            ON UPDATE NO ACTION ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS "WeatherDatas_index_0"
    ON "WeatherDatas" ("Id");
    """
    create_trigger_function = """
    CREATE OR REPLACE FUNCTION delete_old_weather_data() RETURNS TRIGGER AS $$
    BEGIN
        DELETE FROM "WeatherDatas" WHERE "Timestamp" < NOW() - INTERVAL '1 week';
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """

    create_trigger = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'delete_old_weather_data_trigger') THEN
            CREATE TRIGGER delete_old_weather_data_trigger
            BEFORE DELETE ON "WeatherDatas"
            FOR EACH ROW
            EXECUTE FUNCTION delete_old_weather_data();
        END IF;
    END $$;
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
    cursor.execute(create_trigger_function)
    cursor.execute(create_trigger)

    # Commit the transaction
    conn.commit()

    print("Tables and indexes created successfully!")

except Exception as e:
    print(f"Error occurred: {e}")
    if conn:
        conn.rollback()
    sys.exit(1)

finally:
    # Close the connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("Connection closed.")
