import sqlite3

def create_forum_database():
    conn = sqlite3.connect('rising_world_forum.db')
    cursor = conn.cursor()
    
    # Boards (Sections)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            url TEXT UNIQUE
        )
    ''')
    
    # Threads (belonging to a board)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board_id INTEGER,
            title TEXT,
            url TEXT UNIQUE,
            FOREIGN KEY(board_id) REFERENCES boards(id)
        )
    ''')
    
    # Posts (belonging to a thread)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER,
            author TEXT,
            content TEXT,
            FOREIGN KEY(thread_id) REFERENCES threads(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Forum database initialized.")

if __name__ == "__main__":
    create_forum_database()
