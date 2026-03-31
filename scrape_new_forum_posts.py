import asyncio
import sqlite3
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_new_posts():
    conn = sqlite3.connect('rising_world_forum.db')
    cursor = conn.cursor()
    
    # Get existing thread URLs
    cursor.execute('SELECT id, url FROM threads')
    thread_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Get board URLs
    cursor.execute('SELECT id, url FROM boards')
    board_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        print("Checking for updates in forum sections...")
        
        for board_url, board_id in board_map.items():
            print(f"Checking board: {board_url}")
            await page.goto(board_url, timeout=60000)
            await asyncio.sleep(random.uniform(1, 3)) # Faster speed
            
            threads = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('h3 > a[href*="/thread/"]'));
                return anchors.map(a => ({ title: a.innerText.trim(), url: a.href }));
            }''')
            
            for thread in threads:
                if thread['url'] not in thread_map:
                    cursor.execute('INSERT INTO threads (board_id, title, url) VALUES (?, ?, ?)', 
                                   (board_id, thread['title'], thread['url']))
                    conn.commit()
                    thread_id = cursor.lastrowid
                    thread_map[thread['url']] = thread_id
                    print(f"  New thread found: {thread['title']}")
                else:
                    thread_id = thread_map[thread['url']]
                
                await page.goto(thread['url'], timeout=60000)
                await asyncio.sleep(random.uniform(1, 2)) # Faster speed
                
                posts = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('article.message')).map(post => ({
                        author: post.querySelector('.username')?.innerText.trim(),
                        content: post.querySelector('.messageBody')?.innerText.trim(),
                        timestamp: post.querySelector('.messagePublicationTime time')?.getAttribute('datetime')
                    }));
                }''')
                
                for post in posts:
                    cursor.execute('SELECT id FROM posts WHERE thread_id=? AND timestamp=? AND author=?', 
                                   (thread_id, post['timestamp'], post['author']))
                    if not cursor.fetchone():
                        cursor.execute('INSERT INTO posts (thread_id, author, content, timestamp) VALUES (?, ?, ?, ?)', 
                                       (thread_id, post['author'], post['content'], post['timestamp']))
                        print(f"    Added new post by {post['author']}")
                conn.commit()
        
        await browser.close()
    conn.close()
    print("Incremental forum update complete.")

if __name__ == "__main__":
    asyncio.run(scrape_new_posts())
