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

    create_permissions_table = """
    CREATE TABLE IF NOT EXISTS "permissions" (
        "id" SERIAL PRIMARY KEY,
        "name" VARCHAR NOT NULL,
        "guard_name" VARCHAR NOT NULL,
        "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "permissions_unique_index"
    ON "permissions" ("name", "guard_name");
    """

    create_roles_table = """
    CREATE TABLE IF NOT EXISTS "roles" (
        "id" SERIAL PRIMARY KEY,
        "name" VARCHAR NOT NULL,
        "guard_name" VARCHAR NOT NULL,
        "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "Roles_unique_index"
    ON "roles" ("name", "guard_name");
    """

    create_model_has_permissions_table = """
    CREATE TABLE IF NOT EXISTS "model_has_permissions" (
        "permission_id" INTEGER NOT NULL,
        "model_type" VARCHAR NOT NULL,
        "model_id" INTEGER NOT NULL,
        PRIMARY KEY ("permission_id", "model_id", "model_type"),
        FOREIGN KEY ("permission_id") REFERENCES "permissions" ("id") ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS "ModelHasPermissions_model_id_model_type_index"
    ON "model_has_permissions" ("model_id", "model_type");
    """

    create_model_has_roles_table = """
    CREATE TABLE IF NOT EXISTS "model_has_roles" (
        "role_id" INTEGER NOT NULL,
        "model_type" VARCHAR NOT NULL,
        "model_id" INTEGER NOT NULL,
        PRIMARY KEY ("role_id", "model_id", "model_type"),
        FOREIGN KEY ("role_id") REFERENCES "roles" ("id") ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS "ModelHasRoles_model_id_model_type_index"
    ON "model_has_roles" ("model_id", "model_type");
    """

    create_role_has_permissions_table = """
    CREATE TABLE IF NOT EXISTS "role_has_permissions" (
        "permission_id" INTEGER NOT NULL,
        "role_id" INTEGER NOT NULL,
        PRIMARY KEY ("permission_id", "role_id"),
        FOREIGN KEY ("permission_id") REFERENCES "permissions" ("id") ON DELETE CASCADE,
        FOREIGN KEY ("role_id") REFERENCES "roles" ("id") ON DELETE CASCADE
    );
    """

    create_users_table = """
    CREATE TABLE IF NOT EXISTS "users" (
        "id" SERIAL PRIMARY KEY,
        "firstname" VARCHAR NOT NULL,
        "lastname" VARCHAR NOT NULL,
        "email" VARCHAR NOT NULL UNIQUE,
        "password" VARCHAR NOT NULL,
        "manager_id" INTEGER,
        "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY ("manager_id") REFERENCES "users" ("id")
    );
    CREATE INDEX IF NOT EXISTS "Users_index_0"
    ON "users" ("id");
    """

    create_invite_table = """
    CREATE TABLE IF NOT EXISTS "invites" (
        "id" SERIAL PRIMARY KEY,
        "token" VARCHAR NOT NULL UNIQUE,
        "expires_at" TIMESTAMP,
        "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE UNIQUE INDEX IF NOT EXISTS "invites_token_unique_index"
    ON "invites" ("token");
    """

    create_session_table = '''
    CREATE TABLE IF NOT EXISTS "sessions" (
        "id" VARCHAR PRIMARY KEY,
        "user_id" INTEGER,
        "ip_address" VARCHAR(45),
        "user_agent" TEXT,
        "payload" TEXT,
        "last_activity" INTEGER,
        FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE SET NULL
    );
    CREATE INDEX IF NOT EXISTS "sessions_user_id_index" ON "sessions" ("user_id");
    CREATE INDEX IF NOT EXISTS "sessions_last_activity_index" ON "sessions" ("last_activity");
    '''

    create_password_reset_tokens_table = '''
    CREATE TABLE IF NOT EXISTS "password_reset_tokens" (
        "email" VARCHAR(255) NOT NULL,
        "token" VARCHAR(255) NOT NULL,
        "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY ("email")
    );
    '''

    # Execute the SQL scripts to create tables and indexes
    cursor.execute(create_weather_station_table)
    cursor.execute(create_weather_datas_table)
    cursor.execute(create_cities_table)
    cursor.execute(create_departements_table)
    cursor.execute(create_trigger_function)
    cursor.execute(create_trigger)

    print("Connected to PostgreSQL!")
    conn.close()

    # SQL to create 'invite' database
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'invites'")
    exists = cursor.fetchone()
    if not exists:
        create_invite_db = f"CREATE DATABASE invites WITH OWNER = '{DB_USER}';"
        cursor.execute(create_invite_db)
        print("Database 'invites' created successfully!")
    else:
        print("Database 'invites' already exists.")
    conn.autocommit = False

    # Close the connection to the 'postgres' database and reconnect to the new 'invite' database
    conn.close()

    # Now connect to the 'invite' database to create the tables
    conn = psycopg2.connect(dbname='invites', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    print("Connected to the 'invites' database!")

    # Create tables for roles, permissions, models, model_has_roles, role_has_permissions, and users inside the newly created db user
    cursor.execute(create_permissions_table)
    cursor.execute(create_roles_table)
    cursor.execute(create_model_has_permissions_table)
    cursor.execute(create_model_has_roles_table)
    cursor.execute(create_role_has_permissions_table)
    cursor.execute(create_users_table)
    cursor.execute(create_invite_table)
    cursor.execute(create_session_table)
    cursor.execute(create_password_reset_tokens_table)

    print("Tables created successfully in the 'invite' database!")

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
