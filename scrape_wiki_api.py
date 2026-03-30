import requests
import sqlite3
import time

def scrape_wiki_via_api():
    base_url = "https://rising-world.fandom.com/api.php"
    conn = sqlite3.connect('wiki_articles.db')
    cursor = conn.cursor()
    
    # 1. Get all page titles
    print("Fetching all page titles from API...")
    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "aplimit": "500"
    }
    
    all_pages = []
    while True:
        response = requests.get(base_url, params=params).json()
        pages = response['query']['allpages']
        all_pages.extend(pages)
        
        if 'continue' in response:
            params['apcontinue'] = response['continue']['apcontinue']
        else:
            break
            
    print(f"Found {len(all_pages)} pages. Starting content extraction...")
    
    # 2. Scrape content for each page using 'revisions'
    for page in all_pages:
        title = page['title']
        print(f"Scraping: {title}")
        
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "revisions",
            "rvslots": "*",
            "rvprop": "content"
        }
        
        try:
            response = requests.get(base_url, params=params).json()
            pages = response['query']['pages']
            page_id = list(pages.keys())[0]
            
            # Extract content from 'main' slot
            revisions = pages[page_id].get('revisions', [])
            if revisions:
                content = revisions[0]['slots']['main']['*']
                url = f"https://rising-world.fandom.com/wiki/{title.replace(' ', '_')}"
                
                cursor.execute('INSERT OR REPLACE INTO articles (title, url, content) VALUES (?, ?, ?)', 
                               (title, url, content))
                conn.commit()
            
            time.sleep(0.5) # Polite delay
        except Exception as e:
            print(f"Error scraping {title}: {e}")
            
    conn.close()
    print("Wiki crawl complete.")

if __name__ == "__main__":
    scrape_wiki_via_api()
