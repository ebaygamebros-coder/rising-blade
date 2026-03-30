# Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Features:
- Database-backed member information tracking (username, rank, gender, registration date, stats).
- Comprehensive forum scraping: Boards, threads, posts, timestamps, and conversational histories.
- Incremental new member/post discovery.
- Automated translation of non-English content.
- Stealth-enabled browser automation to bypass forum firewall protections.

## Project Context
- **Database:** SQLite used for local storage.
- **Scraping Engine:** Playwright with `playwright-stealth` for evasion.
- **Workflow:** Incremental daily checks targeting recent registrations and active threads.
