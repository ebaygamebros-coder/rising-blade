import sqlite3

def create_database():
    conn = sqlite3.connect('rising_world_members.db')
    cursor = conn.cursor()
    
    # Define schema based on member information structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            rank TEXT,
            gender TEXT,
            member_since TEXT,
            website TEXT,
            posts INTEGER,
            reactions_received INTEGER,
            points INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database created with members schema.")

if __name__ == "__main__":
    create_database()
