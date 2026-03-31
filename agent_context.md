# Project Context: Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Status:
- Member database: Fully populated (6,929 members) with incremental updates.
- Official Forum database: Fully populated with incremental updates and automated translation.
- Wiki database: Fully populated via MediaWiki API.
- Steam Community Forum (Rising World): Successfully implemented vision-based scraping to bypass WAF, populating conversations and metadata.
- Workspace: Cleaned of artifacts and version-controlled.

## Notes:
- Keep scraper speed low to avoid WAF blocks.
- Database files (`rising_world_members.db`, `rising_world_forum.db`, `wiki_articles.db`, `steam_forum.db`) are excluded from Git.
- Use Playwright-Stealth for forum scraping, MediaWiki API for wiki, and Gemini 2.5 Flash for vision-based Steam scraping.
- Translation script can be run to batch-process any remaining non-English posts.
