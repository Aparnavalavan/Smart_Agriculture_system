
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "database", "smart_agriculture.db")

SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

connection = sqlite3.connect(DB_PATH)

with open(SCHEMA_PATH, "r") as file:
    connection.executescript(file.read())

connection.commit()
connection.close()

print("Database created successfully!")
print("Farmers table created successfully!")
