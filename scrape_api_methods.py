import sqlite3
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth

DB_NAME = "api_docs.db"

async def scrape_methods():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_methods (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER,
                        name TEXT,
                        description TEXT,
                        FOREIGN KEY(class_id) REFERENCES api_docs(id)
                      )''')
    conn.commit()

    cursor.execute("SELECT id, name, url FROM api_docs")
    classes = cursor.fetchall()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/120.0.0.0"
        )
        page = await context.new_page()
        stealth_instance = stealth.Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        for class_id, class_name, url in classes:
            print(f"Scraping methods for {class_name}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Javadoc new structure usually uses <section class="summary">
                # We try a robust wait for the content
                try:
                    await page.wait_for_selector('section.summary', timeout=10000)
                except:
                    print("  No method summary section found.")
                    continue

                # Extract method data
                methods = await page.evaluate('''() => {
                    const rows = Array.from(document.querySelectorAll('section.summary .summary-table div.col-last'));
                    return rows.map(row => {
                        const name = row.previousElementSibling ? row.previousElementSibling.innerText : 'Unknown';
                        const desc = row.innerText;
                        return { name: name, desc: desc };
                    });
                }''')
                
                for m in methods:
                    if m['name']:
                        cursor.execute("INSERT INTO api_methods (class_id, name, description) VALUES (?, ?, ?)",
                                       (class_id, m['name'], m['desc']))
                conn.commit()
            except Exception as e:
                print(f"  Failed to scrape {class_name}: {e}")
                
        await browser.close()
    conn.close()
    print("Method scraping complete.")

if __name__ == "__main__":
    asyncio.run(scrape_methods())
