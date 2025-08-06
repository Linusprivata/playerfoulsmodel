# Development Notes

## FBref Data Collection Status

### Successfully Extracting (25 fields):
- Basic match info: date, competition, venue, opponent, home/away teams and goals
- Player stats: position, minutes, fouls, fouled, yellow/red cards
- Defensive stats: tackles (total, by third), challenges attempted
- Possession stats: take-ons attempted/succeeded

### Cannot Extract via ScraperFC (7 fields):
1. **starting** - Whether player was in starting lineup
2. **team_fouls** - Total fouls by player's team
3. **team_fouled** - Total times player's team was fouled
4. **team_possession_pct** - Team's possession percentage
5. **opponent_possession_pct** - Opponent's possession percentage
6. **referee_name** - Match referee
7. **attendance** - Match attendance

### Reason:
- ScraperFC only provides player-level statistics, not team-level or match metadata
- Direct HTML scraping is blocked by FBref (403 Forbidden)
- These fields exist on the webpage but require HTML parsing

### Solutions:
1. **Option 1**: Use Selenium WebDriver for these specific fields (slower, more complex)
2. **Option 2**: Get these fields from Sofascore or Whoscored APIs
3. **Option 3**: Accept missing data for MVP and add later
4. **Current Decision**: Proceed with available data and attempt to get missing fields from other sources

## Next Steps:
1. Integrate Sofascore scraper - may have team stats and match metadata
2. Integrate Whoscored scraper - likely has referee and detailed match info
3. If critical fields still missing after all sources, consider Selenium as fallback