import os
import psycopg2

# Load environment variables
QDB_HOST = os.getenv("QDB_PG_HOST", "localhost")
QDB_PORT = os.getenv("QDB_PG_PORT", "8812")
QDB_USER = os.getenv("QDB_PG_USER", "admin")
QDB_PASSWORD = os.getenv("QDB_PG_PASSWORD", "quest")

# Function to validate PostgreSQL connection
def validate_questdb_pg_connection():
    try:
        conn = psycopg2.connect(
            host=QDB_HOST,
            port=QDB_PORT,
            user=QDB_USER,
            password=QDB_PASSWORD,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"QuestDB PostgreSQL connection successful. Version: {version}")
        conn.close()
    except Exception as e:
        print(f"Error connecting to QuestDB PostgreSQL: {e}")

validate_questdb_pg_connection()
