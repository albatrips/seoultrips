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

def get_all_categories():
    """Get all unique categories from route_table"""
    conn = get_db_connection()
    if conn is None:
        # Return default categories if database connection fails
        return ['액티비티', '자연', '산책', '야경', '문화', '맛집', '쇼핑', '역사', '예술', '카페']
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM route_table WHERE category IS NOT NULL AND category != ''")
        results = cursor.fetchall()
        
        # Split comma-separated categories and collect unique ones
        categories = set()
        for row in results:
            if row[0]:
                # Split by comma and strip whitespace
                cat_list = [cat.strip() for cat in row[0].split(',') if cat.strip()]
                categories.update(cat_list)
        
        # Add some additional hardcoded categories
        additional_categories = ['문화', '맛집', '쇼핑', '역사', '예술', '카페', '체험', '휴식', '경치']
        categories.update(additional_categories)
        
        # Convert to sorted list
        return sorted(list(categories))
    
    except mysql.connector.Error as err:
        print(f"Error fetching categories: {err}")
        # Return default categories on error
        return ['액티비티', '자연', '산책', '야경', '문화', '맛집', '쇼핑', '역사', '예술', '카페']
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
        # Include total_estimated_time in the query
        query = f"""
            SELECT 
                r.route_title,
                r.set_id,
                r.total_estimated_time,
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
                    'total_estimated_time': row['total_estimated_time'],
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

def get_max_quest_id():
    """Get the maximum quest_id from the quests table"""
    conn = get_db_connection()
    if conn is None:
        return 0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(quest_id) FROM quests")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    except mysql.connector.Error as err:
        print(f"Error fetching max quest_id: {err}")
        return 0
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def create_quests(quests_data: list):
    if not quests_data:
        print("No quests data provided to create_quests")
        return
    
    print(f"Creating {len(quests_data)} quests:")
    for i, quest in enumerate(quests_data):
        print(f"  Quest {i+1}: {quest.get('place_name', 'No name')} - {quest.get('mission', 'No mission')}")
    
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed in create_quests")
        return

    try:
        cursor = conn.cursor()
        
        # Clear all existing quests first
        print("Clearing all existing quests...")
        cursor.execute("DELETE FROM quests")
        
        # Reset AUTO_INCREMENT to start from 1
        cursor.execute("ALTER TABLE quests AUTO_INCREMENT = 1")
        
        query = """
            INSERT INTO quests (mission, place_name, description, is_cleared, address, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = []
        for i, q in enumerate(quests_data):
            values.append((
                q.get('mission'), 
                q.get('place_name'), 
                q.get('description'), 
                0, 
                q.get('address'), 
                q.get('lat'), 
                q.get('lng')
            ))
            print(f"  Prepared quest {i+1}: {q.get('place_name')} at ({q.get('lat')}, {q.get('lng')})")
        
        cursor.executemany(query, values)
        conn.commit()
        print(f"Successfully created {len(values)} new quests (replaced all existing quests)")
        
        # Verify the insertion
        cursor.execute("SELECT quest_id, place_name FROM quests ORDER BY quest_id ASC")
        all_quests = cursor.fetchall()
        print("All quests in database after replacement:")
        for quest in all_quests:
            print(f"  quest_id: {quest[0]}, place_name: {quest[1]}")
            
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
        print("Database connection failed, returning fallback data")
        # Return test data when database connection fails
        return [
            {"id": 1, "title": "경복궁 방문", "description": "경복궁에서 사진찍기", "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!", "is_cleared": 0, "lat": 37.579617, "lng": 126.977041},
            {"id": 2, "title": "북촌한옥마을 걷기", "description": "한옥마을에서 전통 문화 체험", "mission": "전통 한옥 거리를 걸으며 한국의 아름다운 전통을 느껴보세요!", "is_cleared": 0, "lat": 37.580146, "lng": 126.976892},
            {"id": 3, "title": "인사동 카페 방문", "description": "전통 찻집에서 차 마시기", "mission": "전통 찻집에서 따뜻한 차 한 잔과 함께 여유로운 시간을 보내세요!", "is_cleared": 0, "lat": 37.5760, "lng": 126.9859}
        ]
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get all quests ordered by quest_id
        query = """
            SELECT quest_id as id, place_name as title, description, mission, is_cleared, lat, lng, address
            FROM quests 
            ORDER BY quest_id ASC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        print(f"Found {len(result)} quests in database")
        
        # Convert Decimal values to float
        for row in result:
            for key, value in row.items():
                if isinstance(value, Decimal):
                    row[key] = float(value)
        
        if result:
            print(f"Returning quests: {[q['title'] for q in result]}")
            return result
        else:
            print("No quest results found, returning fallback data")
            return [
                {"id": 1, "title": "경복궁 방문", "description": "경복궁에서 사진찍기", "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!", "is_cleared": 0, "lat": 37.579617, "lng": 126.977041},
                {"id": 2, "title": "북촌한옥마을 걷기", "description": "한옥마을에서 전통 문화 체험", "mission": "전통 한옥 거리를 걸으며 한국의 아름다운 전통을 느껴보세요!", "is_cleared": 0, "lat": 37.580146, "lng": 126.976892},
                {"id": 3, "title": "인사동 카페 방문", "description": "전통 찻집에서 차 마시기", "mission": "전통 찻집에서 따뜻한 차 한 잔과 함께 여유로운 시간을 보내세요!", "is_cleared": 0, "lat": 37.5760, "lng": 126.9859}
            ]
            
    except mysql.connector.Error as err:
        print(f"Error fetching all quests: {err}")
        # Return test data when database query fails
        return [
            {"id": 1, "title": "경복궁 방문", "description": "경복궁에서 사진찍기", "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!", "is_cleared": 0, "lat": 37.579617, "lng": 126.977041},
            {"id": 2, "title": "북촌한옥마을 걷기", "description": "한옥마을에서 전통 문화 체험", "mission": "전통 한옥 거리를 걸으며 한국의 아름다운 전통을 느껴보세요!", "is_cleared": 0, "lat": 37.580146, "lng": 126.976892},
            {"id": 3, "title": "인사동 카페 방문", "description": "전통 찻집에서 차 마시기", "mission": "전통 찻집에서 따뜻한 차 한 잔과 함께 여유로운 시간을 보내세요!", "is_cleared": 0, "lat": 37.5760, "lng": 126.9859}
        ]
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_quest_by_id(quest_id: int):
    """Get detailed quest information by quest_id including photomission from set_table"""
    conn = get_db_connection()
    if conn is None:
        # Return test data when database connection fails
        return {
            "id": quest_id,
            "title": "경복궁 방문",
            "description": "경복궁에서 사진찍기",
            "mission": "궁궐의 아름다운 건축물과 함께 인증샷을 촬영해보세요!",
            "photomission": "궁궐의 웅장한 전각을 배경으로 한 인증샷을 촬영해주세요. 전통 건축의 아름다움과 함께 당신의 모습을 담아보세요!",
            "is_cleared": 0,
            "lat": 37.579617,
            "lng": 126.977041,
            "address": "서울특별시 종로구 사직로 161",
            "place_name": "경복궁"
        }
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First try to get from quests table
        quest_query = """
            SELECT quest_id as id, place_name as title, description, mission, is_cleared, lat, lng, address
            FROM quests 
            WHERE quest_id = %s
        """
        cursor.execute(quest_query, (quest_id,))
        quest_result = cursor.fetchone()
        
        if quest_result:
            # Convert Decimal values to float
            for key, value in quest_result.items():
                if isinstance(value, Decimal):
                    quest_result[key] = float(value)
            
            # Try to get additional photomission data from set_table if available
            set_query = """
                SELECT photomission, take_time, signgu
                FROM set_table 
                WHERE place_name = %s
                LIMIT 1
            """
            cursor.execute(set_query, (quest_result['title'],))
            set_result = cursor.fetchone()
            
            if set_result and set_result['photomission']:
                quest_result['photomission'] = set_result['photomission']
                quest_result['take_time'] = set_result['take_time']
                quest_result['signgu'] = set_result['signgu']
            else:
                # Generate dynamic photomission based on place name
                quest_result['photomission'] = f"{quest_result['title']}에서 특별한 순간을 담아보세요! 이곳만의 독특한 분위기와 함께 멋진 인증샷을 촬영해주세요."
            
            return quest_result
        else:
            # Fallback test data
            return {
                "id": quest_id,
                "title": f"퀘스트 {quest_id}",
                "description": "특별한 모험이 당신을 기다리고 있습니다.",
                "mission": "이 장소에서 멋진 퀘스트를 수행해보세요!",
                "photomission": "이곳의 특별한 분위기를 담은 인증샷을 촬영해주세요. 당신만의 독특한 시각으로 이 순간을 기록해보세요!",
                "is_cleared": 0,
                "lat": 37.579617,
                "lng": 126.977041,
                "address": "서울특별시",
                "place_name": f"퀘스트 장소 {quest_id}"
            }
            
    except mysql.connector.Error as err:
        print(f"Error fetching quest by id: {err}")
        return {
            "id": quest_id,
            "title": f"퀘스트 {quest_id}",
            "description": "특별한 모험이 당신을 기다리고 있습니다.",
            "mission": "이 장소에서 멋진 퀘스트를 수행해보세요!",
            "photomission": "이곳의 특별한 분위기를 담은 인증샷을 촬영해주세요. 당신만의 독특한 시각으로 이 순간을 기록해보세요!",
            "is_cleared": 0,
            "lat": 37.579617,
            "lng": 126.977041,
            "address": "서울특별시",
            "place_name": f"퀘스트 장소 {quest_id}"
        }
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close() 