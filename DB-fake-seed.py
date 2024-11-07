import psycopg2
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
    # Establish the connection
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    cursor = conn.cursor()
    print("Connected to the database!")

    # Insert data into "Cities" table
    cities_insert_query = """
    INSERT INTO "Cities" ("Name", "Position") VALUES
    ('Paris', '234;450'),
    ('London', '234;450'),
    ('New York', '234;450'),
    ('Tokyo', '234;450'),
    ('Berlin', '234;450');
    """
    cursor.execute(cities_insert_query)
    print("Cities data inserted successfully!")

    # Insert data into "Departements" table
    departements_insert_query = """
    INSERT INTO "Departements" ("Name") VALUES
    ('ain'), 
    ('aisne'), 
    ('allier'), 
    ('alpes-de-haute-provence');
    """
    cursor.execute(departements_insert_query)
    print("Departements data inserted successfully!")

    # Insert data into "MeteoDataDP" table
    meteo_data_insert_query = """
    INSERT INTO "MeteoDataDP" ("DepartmentId", "Temperature", "Humidity", "WindSpeed", "WindDirection", 
                               "Precipitation", "Pressure", "Date")
    VALUES
    ((SELECT Id FROM "Departements" WHERE "Name" = 'ain'), 20, 50, 10, 'N', 0, 1013, '2024-01-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'aisne'), 22, 60, 12, 'E', 5, 1012, '2024-01-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'allier'), 18, 55, 8, 'SW', 3, 1011, '2024-01-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'alpes-de-haute-provence'), 25, 40, 15, 'W', 2, 1009, '2024-01-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'ain'), 20, 50, 10, 'N', 0, 1013, '2024-02-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'aisne'), 22, 60, 12, 'E', 5, 1012, '2024-02-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'allier'), 18, 55, 8, 'SW', 3, 1011, '2024-02-01'),
    ((SELECT Id FROM "Departements" WHERE "Name" = 'alpes-de-haute-provence'), 25, 40, 15, 'W', 2, 1009, '2024-02-01');
    """
    cursor.execute(meteo_data_insert_query)
    print("MeteoDataDP data inserted successfully!")

    # Commit the transaction
    conn.commit()

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
