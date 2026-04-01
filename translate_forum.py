import sqlite3
import time
from googletrans import Translator

def translate_german_posts():
    conn = sqlite3.connect('rising_world_forum.db')
    cursor = conn.cursor()
    translator = Translator()
    
    # Select all German board posts
    cursor.execute('SELECT p.id, p.content FROM posts p JOIN threads t ON p.thread_id = t.id JOIN boards b ON t.board_id = b.id WHERE b.name LIKE "%German%"')
    posts = cursor.fetchall()
    
    print(f"Found {len(posts)} posts. Starting translation...")
    
    for post_id, content in posts:
        if not content or len(content.strip()) < 5:
            continue
            
        try:
            # Simple retry mechanism
            for _ in range(3):
                try:
                    detection = translator.detect(content)
                    if detection.lang == 'de':
                        print(f"  Translating post {post_id}...")
                        translated = translator.translate(content, dest='en').text
                        cursor.execute('UPDATE posts SET content = ? WHERE id = ?', (translated, post_id))
                        conn.commit()
                    break # Success
                except Exception as e:
                    time.sleep(2) # Wait before retry
            else:
                print(f"  Failed translation for post {post_id} after retries.")
        except Exception as e:
            print(f"Critcal error translating post {post_id}: {e}")
            
    conn.close()
    print("Translation complete.")

if __name__ == "__main__":
    translate_german_posts()
