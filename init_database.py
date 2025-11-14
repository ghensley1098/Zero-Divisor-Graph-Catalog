# init_database.py
from database import ZeroDivisorDatabase
import os

def initialize_database():
    """Initialize a fresh database with the enhanced schema including self-loops"""
    db_path = "zero_divisor_catalog.db"
    
    # Remove existing database if you want a fresh start
    if os.path.exists(db_path):
        response = input("Database already exists. Delete and create fresh? (y/n): ")
        if response.lower() == 'y':
            os.remove(db_path)
            print("Old database removed.")
        else:
            print("Using existing database.")
    
    # Initialize the database
    db = ZeroDivisorDatabase(db_path)
    print("Database initialized successfully!")
    print(f"Database file: {os.path.abspath(db_path)}")
    
    # Test the connection
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables created: {[table[0] for table in tables]}")
        
        # Check if self_loops columns exist
        cursor.execute("PRAGMA table_info(MyNumber);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"MyNumber columns: {column_names}")
        
        conn.close()
    except Exception as e:
        print(f"Error testing database: {e}")

if __name__ == "__main__":
    initialize_database()