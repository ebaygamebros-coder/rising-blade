import json
import asyncio
import sqlite3
import random
import time
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_members():
    # Database setup
    conn = sqlite3.connect('rising_world_members.db')
    cursor = conn.cursor()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        for page_no in range(1, 232):
            url = f"https://www.rising-world.net/members-list/?pageNo={page_no}&sortField=wbbPosts&sortOrder=DESC&letter="
            print(f"Scraping page {page_no}/231: {url}")
            
            try:
                await page.goto(url, timeout=60000)
                # Randomized delay to mimic human behavior
                await asyncio.sleep(random.uniform(5, 15))
                
                members = await page.evaluate('''() => {
                    const memberItems = document.querySelectorAll('li.memberItem');
                    const results = [];
                    memberItems.forEach(item => {
                        try {
                            const username = item.querySelector('h3 a').innerText.trim();
                            const rank = item.querySelector('h3 span') ? item.querySelector('h3 span').innerText.trim() : null;
                            const stats = item.querySelectorAll('ul li');
                            const memberSince = stats[1] ? stats[1].innerText.replace('Member since ', '').trim() : null;
                            
                            const termElements = item.querySelectorAll('.dataListTerm');
                            const defElements = item.querySelectorAll('.dataListDefinition');
                            
                            let posts = 0, reactions = 0, points = 0;
                            
                            for(let i=0; i<termElements.length; i++) {
                                const label = termElements[i].innerText.toLowerCase();
                                const value = defElements[i].innerText.replace(/,/g, '').trim();
                                if(label.includes('posts')) posts = parseInt(value);
                                else if(label.includes('reactions')) reactions = parseInt(value);
                                else if(label.includes('points')) points = parseInt(value);
                            }
                            
                            results.push({username, rank, memberSince, posts, reactions, points});
                        } catch(e) {}
                    });
                    return results;
                }''')
                
                for m in members:
                    cursor.execute('''INSERT OR IGNORE INTO members (username, rank, member_since, posts, reactions_received, points) 
                                      VALUES (?, ?, ?, ?, ?, ?)''', 
                                   (m['username'], m['rank'], m['memberSince'], m['posts'], m['reactions'], m['points']))
                conn.commit()
                print(f"Added {len(members)} members from page {page_no}.")
                
            except Exception as e:
                print(f"Error on page {page_no}: {e}")
                await page.screenshot(path=f"error_page_{page_no}.png")
                await asyncio.sleep(30) # Longer wait on error
                
        await browser.close()
    conn.close()

if __name__ == "__main__":
    asyncio.run(scrape_members())
