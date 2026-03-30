# Project Context: Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Status:
- Member database: Fully populated (6,929 members).
- Forum database: Fully populated (boards, threads, posts, timestamps, conversational history).
- Incremental update scripts: Implemented for both members and forum threads.
- Translation pipeline: German content automatically translated to English.
- Wiki scraping: Attempted, but currently blocked by Fandom's robust anti-bot measures. Further investigation or alternative data sources needed.
- Workspace: Cleaned and version-controlled.

## Notes:
- Keep scraper speed low to avoid being blocked by WAFs.
- Database files (`rising_world_members.db`, `rising_world_forum.db`, `wiki_articles.db`) are excluded from Git.
- Use Playwright-Stealth for all scraping operations, but Fandom wiki proved challenging.
- The incremental forum scraper targets the main board; it can be extended to all boards if monitoring depth needs to increase.
- Translation script should be run periodically to handle new non-English content.
