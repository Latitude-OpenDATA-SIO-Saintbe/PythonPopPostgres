import requests
import psycopg2
from dotenv import load_dotenv
import os

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

def fetch_french_cities():
    url = "https://geo.api.gouv.fr/communes?fields=nom,centre&format=json&geometry=centre"
    try:
        response = requests.get(url)
        response.raise_for_status()
        cities = response.json()
        return [(city['nom'], city['centre']['coordinates'][1], city['centre']['coordinates'][0]) for city in cities]
    except Exception as e:
        print("Error fetching French cities data:", e)
        return []

def fetch_departments():
    url = "https://gist.githubusercontent.com/Tazeg/e0c05fdb39552010e9d0e8218aa3f23c/raw/792f846499b67f135b274ff54d72260ffad48dfe/depts.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        departments = response.json()
        return departments
    except Exception as e:
        print("Error fetching department data:", e)
        return []

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


# Fetch and seed all French city location data
french_cities = fetch_french_cities()
if french_cities:
    seed_city_locations(french_cities)
else:
    print("No French city location data to insert.")
# Fetch all departments and seed them
departments = fetch_departments()
if departments:
    seed_departments(departments)
else:
    print("No department data to insert.")
