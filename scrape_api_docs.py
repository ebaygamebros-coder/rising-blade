import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL
BASE_URL = "https://javadoc.rising-world.net/latest/"
DB_NAME = "api_docs.db"

def init_db():
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
    conn.close()

def scrape_packages():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    package_links = soup.select('a[href*="package-summary.html"]')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for link in package_links:
        pkg_url = urljoin(BASE_URL, link['href'])
        pkg_name = link.text
        print(f"Scraping package: {pkg_name}")
        
        # Crawl classes in package
        pkg_response = requests.get(pkg_url)
        pkg_soup = BeautifulSoup(pkg_response.text, 'html.parser')
        
        # Javadoc class links usually appear in a specific table or list
        links = pkg_soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            # Check if it looks like a class summary page
            # Usually: 'class-name.html'
            if href and '.html' in href and 'class' in href:
                print(f"DEBUG: Found class link: {link.text} -> {href}")
                class_url = urljoin(pkg_url, href)
                try:
                    cursor.execute("INSERT OR IGNORE INTO api_docs (name, type, url) VALUES (?, ?, ?)", 
                                   (link.text, 'class', class_url))
                except sqlite3.IntegrityError:
                    pass
    
    conn.commit()
    conn.close()
    print("Scraping complete.")

if __name__ == "__main__":
    init_db()
    scrape_packages()
