import sqlite3

def init_steam_forum_db():
    conn = sqlite3.connect('steam_forum.db')
    cursor = conn.cursor()
    
    # Boards (Steam Sub-forums)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            url TEXT UNIQUE
        )
    ''')
    
    # Threads (belonging to a Steam board)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board_id INTEGER,
            title TEXT,
            url TEXT UNIQUE,
            last_activity TEXT,
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
            timestamp TEXT,
            FOREIGN KEY(thread_id) REFERENCES threads(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Steam forum database initialized.")

if __name__ == "__main__":
    init_steam_forum_db()
