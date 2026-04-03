import sqlite3
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth

DB_NAME = "api_docs.db"
BASE_URL = "https://javadoc.rising-world.net/latest/"

async def scrape():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_docs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        type TEXT,
                        description TEXT,
                        url TEXT UNIQUE
                      )''')
    conn.commit()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/120.0.0.0"
        )
        page = await context.new_page()
        stealth_instance = stealth.Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        print(f"Accessing {BASE_URL}")
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        
        # Correctly identify package links
        packages = await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a[href*="package-summary.html"]'));
            return links.map(a => ({ name: a.innerText, url: a.href }));
        }''')
        
        for pkg in packages:
            print(f"Scraping package: {pkg['name']}")
            await page.goto(pkg['url'], wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # The structure uses a div with id #class-summary and a table inside
            # We select all links within the summary table
            classes = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('div#class-summary a'));
                return links.map(a => ({ name: a.innerText, url: a.href }));
            }''')
            
            for cls in classes:
                if not cls['name']: continue
                print(f"  Inserting {cls['name']}...")
                try:
                    cursor.execute("INSERT INTO api_docs (name, type, url) VALUES (?, ?, ?)", 
                                   (cls['name'], 'class', cls['url']))
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"DB Error: {e}")
        
        await browser.close()
    conn.close()
    print("Scraping complete.")

if __name__ == "__main__":
    asyncio.run(scrape())
