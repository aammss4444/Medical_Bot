import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to the default 'postgres' database
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="Amey@p4444",
    host="localhost"
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()

try:
    cur.execute("CREATE DATABASE medical_bot;")
    print("Database 'medical_bot' created successfully.")
except psycopg2.errors.DuplicateDatabase:
    print("Database 'medical_bot' already exists.")
except Exception as e:
    print(f"Error creating database: {e}")
finally:
    cur.close()
    conn.close()
