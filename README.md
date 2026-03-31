# Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Features:
- Member Database: Tracks forum member activity.
- Official Forum Database: Scrapes and parses boards, threads, posts, and conversational history.
- Steam Forum Database: Vision-based scraper uses Gemini 2.5 Flash to extract and store full conversational histories from Steam.
- Wiki Database: Populated via MediaWiki API.
- Translation pipeline: Automates English translation of non-English content.
- Stealth automation: Bypasses firewall protections using Playwright and vision models.

## Current Status:
- All core scraping modules for Member, Official Forum, Steam Forum, and Wiki are operational and integrated into SQLite databases.

## Project Context
- **Databases:** SQLite local storage.
- **Scraping Engines:** Playwright/Stealth (Official Forum), MediaWiki API (Wiki), Vision-model parsing (Steam).
- **Workflow:** Incremental daily checks targeting recent activity.
