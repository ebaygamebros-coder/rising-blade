import json
import asyncio
import sqlite3
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_members():
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
            print(f"Scraping page {page_no}/231...")
            
            try:
                await page.goto(url, timeout=60000)
                await asyncio.sleep(random.uniform(5, 10))
                
                members = await page.evaluate('''() => {
                    const memberItems = document.querySelectorAll('li[data-object-id]');
                    const results = [];
                    memberItems.forEach(item => {
                        try {
                            const username = item.querySelector('.username')?.innerText.trim();
                            // rank is now a span badge
                            const rank = item.querySelector('.userTitleBadge')?.innerText.trim();
                            
                            // gender and member since are in the list items
                            const listItems = Array.from(item.querySelectorAll('.inlineList > li'));
                            let gender = null, memberSince = null;
                            listItems.forEach(li => {
                                const text = li.innerText.trim();
                                if (['Male', 'Female', 'Non-binary'].includes(text)) gender = text;
                                else if (text.includes('Member since')) memberSince = text.replace('Member since ', '').trim();
                            });
                            
                            // Stats are in dl.plain dt/dd pairs
                            let posts = 0, reactions = 0, points = 0;
                            const dts = item.querySelectorAll('dl.plain dt');
                            const dds = item.querySelectorAll('dl.plain dd');
                            
                            for(let i=0; i<dts.length; i++) {
                                const label = dts[i].innerText.toLowerCase();
                                const val = dds[i] ? dds[i].innerText.replace(/,/g, '').trim() : '0';
                                if(label.includes('posts')) posts = parseInt(val) || 0;
                                else if(label.includes('reactions')) reactions = parseInt(val) || 0;
                                else if(label.includes('points')) points = parseInt(val) || 0;
                            }
                            
                            if (username) {
                                results.push({username, rank, gender, memberSince, posts, reactions, points});
                            }
                        } catch(e) {}
                    });
                    return results;
                }''')
                
                for m in members:
                    cursor.execute('''INSERT OR IGNORE INTO members (username, rank, gender, member_since, posts, reactions_received, points) 
                                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                   (m['username'], m['rank'], m['gender'], m['memberSince'], m['posts'], m['reactions'], m['points']))
                conn.commit()
                print(f"Added {len(members)} members from page {page_no}.")
                
            except Exception as e:
                print(f"Error on page {page_no}: {e}")
                await asyncio.sleep(20)
                
        await browser.close()
    conn.close()

if __name__ == "__main__":
    asyncio.run(scrape_members())
