import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Apply stealth correctly
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)
        
        print("Navigating to forum with stealth...")
        try:
            await page.goto("https://forum.rising-world.net/", timeout=60000)
            await asyncio.sleep(5)
            
            # Use the selectors identified from the snapshot (e.g., thread link classes/titles)
            # The snapshot showed headings within listitems for thread titles
            threads = await page.evaluate('''() => {
                const threadElements = document.querySelectorAll('h3 a');
                const results = [];
                threadElements.forEach(el => {
                    const title = el.innerText.trim();
                    const link = el.href;
                    if (title && link.includes('thread/')) {
                        results.push({
                            title: title,
                            link: link
                        });
                    }
                });
                return results;
            }''')
            
            with open('test_results.json', 'w') as f:
                json.dump(threads, f, indent=4)
            print(f"Scraped {len(threads)} threads.")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            await page.screenshot(path="stealth_error.png")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
