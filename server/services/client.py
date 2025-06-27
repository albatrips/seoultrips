import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path
from decimal import Decimal

# Load .env file from the project root. This is more robust.
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path, override=False) 

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

def get_routes_by_categories(categories: list):
    if not categories:
        return []

    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Create a query with a WHERE clause that checks if the route's category is in the provided list.
        # This uses FIND_IN_SET for comma-separated category strings, or a simple IN clause.
        # We'll build the placeholders dynamically to avoid SQL injection.
        # placeholders = ','.join(['%s'] * len(categories))

        conditions = " OR ".join([f"FIND_IN_SET(%s, r.category)" for _ in categories])
        
        # This query joins the two tables and filters routes by the selected categories.
        # It orders the results to ensure course steps are sequential.
        query = f"""
            SELECT 
                r.route_title,
                r.set_id,
                s.course_id,
                s.place_name
            FROM 
                route_table r
            JOIN 
                set_table s ON r.set_id = s.set_id
            WHERE 
                {conditions}
            ORDER BY 
                r.set_id, s.course_id;
        """

        cursor.execute(query, tuple(categories))
        results = cursor.fetchall()
        
        # Group the flat SQL results into a nested structure by route_title.
        routes = {}
        for row in results:
            title = row['route_title']
            if title not in routes:
                routes[title] = {
                    'route_title': title,
                    'set_id': row['set_id'],
                    'courses': []
                }
            routes[title]['courses'].append({
                'course_id': row['course_id'],
                'place_name': row['place_name']
            })
        
        return list(routes.values())

    except mysql.connector.Error as err:
        print(f"Error fetching routes: {err}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_set_by_id(set_id: int):
    if not set_id:
        return []
    
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        # Re-expanding the query to include all possible fields to match the database schema.
        # This will ensure data is fetched correctly.
        query = "SELECT course_id, mission, place_name, description, photomission, take_time, signgu, lat, lng FROM set_table WHERE set_id = %s ORDER BY course_id"
        cursor.execute(query, (set_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching set details: {err}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_quests(quests_data: list):
    if not quests_data:
        return
    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quests")
        
        query = """
            INSERT INTO quests (quest_id, mission, place_name, description, is_cleared, address, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = [
            (q.get('course_id'), q.get('mission'), q.get('place_name'), q.get('description'), 0, q.get('address'), q.get('lat'), q.get('lng'))
            for q in quests_data
        ]
        cursor.executemany(query, values)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error creating quests: {err}")
        conn.rollback()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_all_quests():
    conn = get_db_connection()
    if conn is None:
        # Return test data when database connection fails
        return [
            {"id": 1, "title": "경복궁 방문", "description": "경복궁에서 사진찍기", "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!", "lat": 37.579617, "lng": 126.977041},
            {"id": 2, "title": "북촌한옥마을 걷기", "description": "한옥마을에서 전통 문화 체험", "mission": "전통 한옥 거리를 걸으며 한국의 아름다운 전통을 느껴보세요!", "lat": 37.580146, "lng": 126.976892},
            {"id": 3, "title": "인사동 카페 방문", "description": "전통 찻집에서 차 마시기", "mission": "전통 찻집에서 따뜻한 차 한 잔과 함께 여유로운 시간을 보내세요!", "lat": 37.5760, "lng": 126.9859}
        ]
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT quest_id as id, place_name as title, description, mission, lat, lng FROM quests ORDER BY quest_id"
        cursor.execute(query)
        result = cursor.fetchall()
        
        # Convert Decimal values to float
        for row in result:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        
        # Return test data if no data found in database
        if not result:
            return [
                {"id": 1, "title": "경복궁 방문", "description": "경복궁에서 사진찍기", "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!", "lat": 37.579617, "lng": 126.977041},
                {"id": 2, "title": "북촌한옥마을 걷기", "description": "한옥마을에서 전통 문화 체험", "mission": "전통 한옥 거리를 걸으며 한국의 아름다운 전통을 느껴보세요!", "lat": 37.580146, "lng": 126.976892},
                {"id": 3, "title": "인사동 카페 방문", "description": "전통 찻집에서 차 마시기", "mission": "전통 찻집에서 따뜻한 차 한 잔과 함께 여유로운 시간을 보내세요!", "lat": 37.5760, "lng": 126.9859}
            ]
        
        return result
    except mysql.connector.Error as err:
        print(f"Error fetching all quests: {err}")
        # Return test data when database query fails
        return [
            {"id": 1, "title": "경복궁 방문", "description": "경복궁에서 사진찍기", "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!", "lat": 37.579617, "lng": 126.977041},
            {"id": 2, "title": "북촌한옥마을 걷기", "description": "한옥마을에서 전통 문화 체험", "mission": "전통 한옥 거리를 걸으며 한국의 아름다운 전통을 느껴보세요!", "lat": 37.580146, "lng": 126.976892},
            {"id": 3, "title": "인사동 카페 방문", "description": "전통 찻집에서 차 마시기", "mission": "전통 찻집에서 따뜻한 차 한 잔과 함께 여유로운 시간을 보내세요!", "lat": 37.5760, "lng": 126.9859}
        ]
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close() 