import sqlite3

def update_schema():
    conn = sqlite3.connect('rising_world_members.db')
    cursor = conn.cursor()
    # Add rank and gender columns if they don't exist, or just recreate for robustness
    cursor.execute('DROP TABLE IF EXISTS members')
    cursor.execute('''
        CREATE TABLE members (
            id INTEGER PRIMARY KEY,
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
    print("Database schema updated.")

if __name__ == "__main__":
    update_schema()
