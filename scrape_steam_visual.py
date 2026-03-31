import asyncio
import sqlite3
import random
import os
import json
import google.generativeai as genai
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Configure your Gemini API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def process_with_gemini(screenshot_path):
    """
    Sends the screenshot to Gemini 3.1 Flash Lite Preview to extract post data.
    Includes a longer delay to respect API rate limits.
    """
    print(f"  [Vision] Sending {screenshot_path} to Gemini 3.1 Flash Lite Preview...")
    
    # Simple retry logic for 429 Quota Exceeded errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('models/gemini-3.1-flash-lite-preview')
            
            with open(screenshot_path, "rb") as image_file:
                image_data = image_file.read()
            
            prompt = """
            Analyze this screenshot from a Steam Community discussion thread.
            Extract all posts. For each post, provide:
            - author (string)
            - content (string)
            - timestamp (string)
            
            Return the result strictly as a JSON array of objects. Do not include markdown formatting or extra text.
            """
            
            response = model.generate_content([
                {'mime_type': 'image/png', 'data': image_data},
                prompt
            ])
            
            json_str = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
            
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 30
                print(f"    Quota exceeded, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                print(f"Vision parsing error: {e}")
                return []
    return []

async def scrape_steam_thread(url, thread_id, cursor, conn):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 2000})
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        try:
            print(f"  Scraping thread: {url}")
            await page.goto(url, timeout=60000)
            await asyncio.sleep(random.uniform(5, 8)) # Increased delay before screenshot
            
            screenshot_path = f"thread_{thread_id}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            
            posts = await process_with_gemini(screenshot_path)
            
            print(f"    Extracted {len(posts)} posts for thread {thread_id}.")
            
            for post in posts:
                if post.get('author') and post.get('content'):
                    cursor.execute('INSERT OR IGNORE INTO posts (thread_id, author, content, timestamp) VALUES (?, ?, ?, ?)', 
                                   (thread_id, post['author'], post['content'], post['timestamp']))
            conn.commit()
            
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                
        except Exception as e:
            print(f"Error scraping thread {url}: {e}")
            
        await browser.close()

async def scrape_steam_forum():
    conn = sqlite3.connect('steam_forum.db')
    cursor = conn.cursor()
    
    boards = [
        {"name": "General Discussions", "url": "https://steamcommunity.com/app/324080/discussions/"}
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for board in boards:
            board_id = cursor.execute('SELECT id FROM boards WHERE url=?', (board['url'],)).fetchone()[0]
            print(f"Scraping board: {board['name']}")
            await page.goto(board['url'], timeout=60000)
            await asyncio.sleep(10)
            
            threads = await page.evaluate('''() => {
                const topics = Array.from(document.querySelectorAll('.forum_topic'));
                return topics.map(t => ({
                    title: t.querySelector('.forum_topic_name')?.innerText.trim(),
                    url: t.querySelector('a.forum_topic_overlay')?.href
                }));
            }''')
            
            for thread in threads:
                if thread['url']:
                    cursor.execute('INSERT OR IGNORE INTO threads (board_id, title, url) VALUES (?, ?, ?)', 
                                   (board_id, thread['title'], thread['url']))
                    conn.commit()
                    thread_id = cursor.execute('SELECT id FROM threads WHERE url=?', (thread['url'],)).fetchone()[0]
                    
                    # Check if already processed
                    count = cursor.execute('SELECT count(*) FROM posts WHERE thread_id=?', (thread_id,)).fetchone()[0]
                    if count == 0:
                        await scrape_steam_thread(thread['url'], thread_id, cursor, conn)
        
        await browser.close()
    conn.close()
    print("Steam forum visual crawl complete.")

if __name__ == "__main__":
    asyncio.run(scrape_steam_forum())
