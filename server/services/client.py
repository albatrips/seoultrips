import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the project root. This is more robust.
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

def get_db_connection():
    db_host = os.getenv("DB_HOST")
    db_port_str = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")

    if not all([db_host, db_port_str, db_user, db_pass, db_name]):
        print("---")
        print("Error: One or more database environment variables are not set.")
        print("Please ensure DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME are all in your .env file.")
        print(f"Loaded ==> DB_HOST: {db_host}, DB_PORT: {db_port_str}, DB_USER: {db_user}, DB_PASS: {db_pass}, DB_NAME: {db_name}")
        print("---")
        return None

    try:
        db_port = int(db_port_str)
    except (ValueError, TypeError):
        print(f"Error: Invalid DB_PORT: '{db_port_str}'. It must be a number.")
        return None

    try:
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def get_user():
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def save_user(age, gender, location, travel_time):
    print('save_user', age, gender, location, travel_time)
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        # Use REPLACE INTO to either insert a new user with ID 1,
        # or replace the existing one. This ensures a single-player profile.
        query = "REPLACE INTO users (user_id, age, gender, location, travel_time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (1, age, gender, location, travel_time))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error saving user: {err}")
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close() 