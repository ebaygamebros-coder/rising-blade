# Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Features:
- Database-backed member information tracking (username, rank, gender, registration date, stats).
- Comprehensive official forum scraping: Boards, threads, posts, timestamps, and conversational histories.
- Incremental new member/post discovery for the official forum.
- Automated translation of non-English content for the official forum.
- Comprehensive wiki scraping via MediaWiki API: Articles, URLs, content, last updated timestamp, and author.
- Stealth-enabled browser automation to bypass official forum firewall protections.

## Current Limitations:
- **Steam Community Forum Scraping:** While board and thread metadata are being collected, the extraction and population of individual post content into the database is currently experiencing issues. This area requires further debugging.

## Project Context
- **Databases:** SQLite used for local storage (members, official forum, wiki, Steam forum).
- **Scraping Engines:** Playwright with `playwright-stealth` for browser-based tasks (official forum), and `requests` for API-based tasks (wiki).
- **Workflow:** Incremental daily checks targeting recent registrations and active threads on the official forum; full crawls for wiki and Steam forum as needed (with incremental updates to be developed for Steam once post extraction is resolved).
