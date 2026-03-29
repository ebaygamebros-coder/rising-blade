# Project Context: Rising Blade

A program to monitor, scrap and parse the forum and wiki of the video game Rising World.

## Status:
- Database initialized with member info.
- Scraper successfully bypassing firewall with Stealth.
- Incremental updates working.
- Workspace cleaned and .gitignore updated.

## Notes:
- Keep the scraper speed low to avoid being blocked by the forum's WAF.
- Database file is excluded from git; only the schema and scripts are tracked.
- Use Playwright-Stealth for all future scraping.
