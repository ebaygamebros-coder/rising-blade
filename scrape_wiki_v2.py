import requests
import sqlite3
import time

def scrape_wiki_via_api():
    base_api_url = "https://rising-world.fandom.com/api.php"
    conn = sqlite3.connect('wiki_articles.db')
    cursor = conn.cursor()
    
    # Ensure schema is up to date
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            url TEXT UNIQUE,
            content TEXT,
            last_updated TEXT,
            author TEXT
        )
    ''')
    conn.commit()
    
    # 1. Get all page titles
    print("Fetching all page titles from API...")
    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "aplimit": "500",
        "apfilterredir": "nonredirects"
    }
    
    all_pages = []
    while True:
        response = requests.get(base_api_url, params=params).json()
        pages = response['query']['allpages']
        all_pages.extend(pages)
        if 'continue' in response:
            params['apcontinue'] = response['continue']['apcontinue']
        else:
            break
            
    print(f"Found {len(all_pages)} pages. Starting detailed extraction...")
    
    # 2. Extract detailed info for each page
    for page in all_pages:
        title = page['title']
        
        # API query to get content, timestamp, and metadata
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "revisions",
            "rvprop": "content|timestamp|user",
            "rvslots": "main"
        }
        
        try:
            response = requests.get(base_api_url, params=params).json()
            pages = response['query']['pages']
            page_id = list(pages.keys())[0]
            data = pages[page_id]
            
            if 'revisions' in data:
                rev = data['revisions'][0]
                content = rev.get('slots', {}).get('main', {}).get('*', '')
                timestamp = rev.get('timestamp')
                author = rev.get('user')
                url = f"https://rising-world.fandom.com/wiki/{title.replace(' ', '_')}"
                
                cursor.execute('''INSERT OR REPLACE INTO articles (title, url, content, last_updated, author) 
                                  VALUES (?, ?, ?, ?, ?)''', 
                               (title, url, content, timestamp, author))
                conn.commit()
                print(f"Scraped: {title} (Updated: {timestamp}, Author: {author})")
                
            time.sleep(0.5) # Polite delay
        except Exception as e:
            print(f"Error scraping {title}: {e}")
            
    conn.close()
    print("Wiki crawl complete.")

if __name__ == "__main__":
    scrape_wiki_via_api()
