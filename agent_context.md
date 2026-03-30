# Project Context: Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Status:
- Member database: Fully populated (6,929 members) with incremental updates.
- Official Forum database: Fully populated (boards, threads, posts, timestamps, conversational history) with incremental updates and German-to-English translation.
- Wiki database: Fully populated via MediaWiki API with content, last updated timestamp, and author.
- Steam Community Forum (Rising World): Boards and threads are scraped successfully, but **post content extraction is currently failing to populate the database**.
- Workspace: Cleaned and version-controlled.

## Notes:
- Keep scraper speed low to avoid being blocked by WAFs.
- Database files (`rising_world_members.db`, `rising_world_forum.db`, `wiki_articles.db`, `steam_forum.db`) are excluded from Git.
- Use Playwright-Stealth for browser-based scraping (official forum, not wiki).
- The incremental forum scraper targets the main board; it can be extended to all boards if monitoring depth needs to increase.
- Translation script should be run periodically to handle new non-English content.
- **Steam Forum Post Extraction Issue:** Despite detailed selector analysis, posts from Steam Community threads are not being consistently saved to the database. Further debugging is required, potentially focusing on: 
    - Dynamic loading of comments. 
    - Deeper HTML structure changes within comment sections. 
    - More aggressive waits or interaction simulation to trigger content rendering.
