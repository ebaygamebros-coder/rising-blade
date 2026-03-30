import asyncio
import sqlite3
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_new_posts():
    conn = sqlite3.connect('rising_world_forum.db')
    cursor = conn.cursor()
    
    # Get existing thread URLs to know which to check
    cursor.execute('SELECT id, url FROM threads')
    thread_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        print("Checking for updates in threads...")
        
        # Check the first few pages of the 'Discussions (English)' board for active threads
        # You could extend this to all boards if needed
        url = "https://forum.rising-world.net/board/34-discussions-english/"
        await page.goto(url, timeout=60000)
        
        threads = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a'))
                .filter(a => a.href.includes('/thread/'))
                .map(a => ({ title: a.innerText.trim(), url: a.href }));
        }''')
        
        for thread in threads:
            if thread['url'] in thread_map:
                thread_id = thread_map[thread['url']]
                
                # Check for new posts in this thread
                await page.goto(thread['url'], timeout=60000)
                await asyncio.sleep(random.uniform(2, 5))
                
                posts = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('article.message')).map(post => ({
                        author: post.querySelector('.username')?.innerText.trim(),
                        content: post.querySelector('.messageBody')?.innerText.trim(),
                        timestamp: post.querySelector('time')?.getAttribute('datetime')
                    }));
                }''')
                
                # Add posts that aren't already in DB for this thread
                for post in posts:
                    cursor.execute('SELECT id FROM posts WHERE thread_id=? AND timestamp=? AND author=?', 
                                   (thread_id, post['timestamp'], post['author']))
                    if not cursor.fetchone():
                        cursor.execute('INSERT INTO posts (thread_id, author, content, timestamp) VALUES (?, ?, ?, ?)', 
                                       (thread_id, post['author'], post['content'], post['timestamp']))
                        print(f"Added new post in thread: {thread['title']} by {post['author']}")
                conn.commit()
        
        await browser.close()
    conn.close()
    print("Incremental forum update complete.")

if __name__ == "__main__":
    asyncio.run(scrape_new_posts())
