import asyncio
import sqlite3
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_steam_forum():
    conn = sqlite3.connect('steam_forum.db')
    cursor = conn.cursor()
    
    # Pre-defined Steam sub-forums for Rising World
    boards = [
        {"name": "General Discussions", "url": "https://steamcommunity.com/app/324080/discussions/"},
        {"name": "Suggestions", "url": "https://steamcommunity.com/app/324080/discussions/?fp=2"}, # Simplified
        {"name": "Offtopic", "url": "https://steamcommunity.com/app/324080/discussions/16/"}
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        for board in boards:
            cursor.execute('INSERT OR IGNORE INTO boards (name, url) VALUES (?, ?)', (board['name'], board['url']))
            board_id = cursor.execute('SELECT id FROM boards WHERE url=?', (board['url'],)).fetchone()[0]
            conn.commit()
            
            print(f"Scraping board: {board['name']}")
            await page.goto(board['url'], timeout=60000)
            await asyncio.sleep(random.uniform(5, 10))
            
            # Scrape threads
            threads = await page.evaluate('''() => {
                const threadLinks = Array.from(document.querySelectorAll('a.forum_topic_overlay'));
                return threadLinks.map(a => ({ title: a.innerText.trim(), url: a.href }));
            }''')
            
            for thread in threads:
                cursor.execute('INSERT OR IGNORE INTO threads (board_id, title, url) VALUES (?, ?, ?)', 
                               (board_id, thread['title'], thread['url']))
                conn.commit()
                thread_id = cursor.execute('SELECT id FROM threads WHERE url=?', (thread['url'],)).fetchone()[0]
                
                print(f"  Scraping thread: {thread['title']}")
                await page.goto(thread['url'], timeout=60000)
                await asyncio.sleep(random.uniform(3, 7))
                
                posts = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('.commentarea .commentthread_comment')).map(post => ({
                        author: post.querySelector('.commentthread_user_link')?.innerText.trim(),
                        content: post.querySelector('.commentthread_comment_text')?.innerText.trim(),
                        timestamp: post.querySelector('.commentthread_comment_timestamp')?.innerText.trim()
                    }));
                }''')
                
                for post in posts:
                    cursor.execute('INSERT INTO posts (thread_id, author, content, timestamp) VALUES (?, ?, ?, ?)', 
                                   (thread_id, post['author'], post['content'], post['timestamp']))
                conn.commit()
        
        await browser.close()
    conn.close()
    print("Steam forum crawl complete.")

if __name__ == "__main__":
    asyncio.run(scrape_steam_forum())
