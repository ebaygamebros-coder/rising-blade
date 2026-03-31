import asyncio
import sqlite3
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_steam_thread(url, thread_id, cursor, conn):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        try:
            print(f"  Scraping thread: {url}")
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(2, 4))
            
            posts = await page.evaluate('''() => {
                const commentElements = document.querySelectorAll('.commentthread_comment');
                return Array.from(commentElements).map(post => ({
                    author: post.querySelector('.commentthread_user_link')?.innerText.trim(),
                    content: post.querySelector('.commentthread_comment_text')?.innerText.trim(),
                    timestamp: post.querySelector('.commentthread_comment_timestamp')?.innerText.trim()
                }));
            }''')
            
            print(f"    Extracted {len(posts)} posts.")
            
            for post in posts:
                # Add to DB, ensure author/content is valid
                if post['author'] and post['content']:
                    # Use INSERT INTO explicitly
                    cursor.execute('INSERT INTO posts (thread_id, author, content, timestamp) VALUES (?, ?, ?, ?)', 
                                   (thread_id, post['author'], post['content'], post['timestamp']))
            # Force commit
            conn.commit()
            print("    Committed posts to database.")
        except Exception as e:
            print(f"Error scraping thread {url}: {e}")
            
        await browser.close()

async def scrape_steam_forum():
    conn = sqlite3.connect('steam_forum.db')
    cursor = conn.cursor()
    
    # Pre-defined Steam sub-forums for Rising World
    boards = [
        {"name": "General Discussions", "url": "https://steamcommunity.com/app/324080/discussions/"},
        {"name": "Suggestions", "url": "https://steamcommunity.com/app/324080/discussions/12/"},
        {"name": "Offtopic", "url": "https://steamcommunity.com/app/324080/discussions/16/"}
    ]
    
    # Ensure tables exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS boards (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, url TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS threads (id INTEGER PRIMARY KEY AUTOINCREMENT, board_id INTEGER, title TEXT, url TEXT UNIQUE, last_activity TEXT, FOREIGN KEY(board_id) REFERENCES boards(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, thread_id INTEGER, author TEXT, content TEXT, timestamp TEXT, FOREIGN KEY(thread_id) REFERENCES threads(id))''')
    conn.commit()
    
    for board in boards:
        cursor.execute('INSERT OR IGNORE INTO boards (name, url) VALUES (?, ?)', (board['name'], board['url']))
        conn.commit()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        for board in boards:
            # Fetch ID
            row = cursor.execute('SELECT id FROM boards WHERE url=?', (board['url'],)).fetchone()
            if row:
                board_id = row[0]
            else:
                continue
            
            print(f"Scraping board: {board['name']}")
            await page.goto(board['url'], timeout=60000)
            await asyncio.sleep(random.uniform(5, 10))
            
            # Scrape threads
            threads = await page.evaluate('''() => {
                const topics = Array.from(document.querySelectorAll('.forum_topic'));
                return topics.map(t => ({
                    title: t.querySelector('.forum_topic_name')?.innerText.trim(),
                    url: t.querySelector('a.forum_topic_overlay')?.href
                }));
            }''')
            
            for thread in threads:
                if thread['url']:
                    title = thread['title'] if thread['title'] else "Unknown Thread"
                    cursor.execute('INSERT OR IGNORE INTO threads (board_id, title, url) VALUES (?, ?, ?)', 
                                   (board_id, title, thread['url']))
                    conn.commit()
                    thread_id = cursor.execute('SELECT id FROM threads WHERE url=?', (thread['url'],)).fetchone()[0]
                    
                    await scrape_steam_thread(thread['url'], thread_id, cursor, conn)
        
        await browser.close()
    conn.close()
    print("Steam forum crawl complete.")

if __name__ == "__main__":
    asyncio.run(scrape_steam_forum())
