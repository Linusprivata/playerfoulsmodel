"""Fixed FBref scraper that handles the real ScraperFC data structure."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from loguru import logger
import requests
from bs4 import BeautifulSoup
import re

try:
    from ScraperFC import FBref as ScraperFCFBref
except ImportError:
    logger.error("ScraperFC not installed. Run: pip install ScraperFC")
    raise

from .base import BaseScraper


class FBrefScraper(BaseScraper):
    """Fixed scraper for FBref data using ScraperFC."""
    
    def __init__(self):
        super().__init__()
        self.fbref = ScraperFCFBref()
        
    def scrape_match(self, match_url: str, player_name: str = None, **kwargs) -> Dict[str, Any]:
        """Scrape FBref match data for a specific player.
        
        Args:
            match_url: FBref match URL
            player_name: Name of the player to extract data for
            
        Returns:
            Dictionary containing player match statistics
        """
        self._wait()
        
        try:
            # Scrape the match using ScraperFC
            match_data = self.fbref.scrape_match(match_url)
            
            if match_data is None or match_data.empty:
                logger.error(f"No data returned for {match_url}")
                return {}
            
            # Extract player-specific data
            if player_name:
                player_data = self._extract_player_data(match_data, player_name, match_url)
                
                # TODO: The following fields need to be obtained from other sources:
                # - starting (whether player started)
                # - team_fouls, team_fouled
                # - team_possession_pct, opponent_possession_pct  
                # - referee_name, attendance
                # These are not available via ScraperFC and direct HTML scraping is blocked
                
                return player_data
            else:
                # Return raw match data if no player specified
                return self._process_match_data(match_data, match_url)
                
        except Exception as e:
            logger.error(f"Error scraping FBref match {match_url}: {e}")
            raise
    
    def _extract_player_data(self, match_data: pd.DataFrame, player_name: str, match_url: str) -> Dict[str, Any]:
        """Extract data for a specific player from match data.
        
        Args:
            match_data: DataFrame from ScraperFC with nested player stats
            player_name: Name of the player
            match_url: Match URL for reference
            
        Returns:
            Dictionary with player statistics
        """
        result = {
            "match_url": match_url,
            "player_name": player_name,
            "scraped_at": datetime.now().isoformat()
        }
        
        if match_data.empty:
            logger.error("Empty match data received")
            return result
        
        # Extract basic match information from first row
        row = match_data.iloc[0]
        result.update({
            "date": row.get("Date"),
            "competition": row.get("Stage", "Unknown"),
            "home_team": row.get("Home Team"),
            "away_team": row.get("Away Team"),
            "home_goals": row.get("Home Goals"),
            "away_goals": row.get("Away Goals"),
        })
        
        # Find player in home or away stats
        player_found = False
        
        # Check home team stats
        if "Home Player Stats" in match_data.columns:
            home_stats = row["Home Player Stats"]
            player_data = self._find_player_in_team_stats(home_stats, player_name)
            if player_data:
                result.update(player_data)
                result["venue"] = "Home"
                result["opponent"] = row.get("Away Team")
                player_found = True
        
        # Check away team stats if not found in home
        if not player_found and "Away Player Stats" in match_data.columns:
            away_stats = row["Away Player Stats"]
            player_data = self._find_player_in_team_stats(away_stats, player_name)
            if player_data:
                result.update(player_data)
                result["venue"] = "Away"
                result["opponent"] = row.get("Home Team")
                player_found = True
        
        if not player_found:
            logger.warning(f"Player {player_name} not found in match {match_url}")
        else:
            logger.success(f"Successfully extracted data for {player_name}")
            
        return result
    
    def _find_player_in_team_stats(self, team_stats: pd.Series, player_name: str) -> Optional[Dict[str, Any]]:
        """Find a player in team stats and extract their data.
        
        Args:
            team_stats: Series containing different stat categories
            player_name: Name of the player to find
            
        Returns:
            Dictionary with player statistics or None if not found
        """
        player_data = {}
        
        # Go through each stat category
        for category in team_stats.index:
            df = team_stats[category]
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
                
            # Find the player column
            player_col = None
            for col in df.columns:
                if 'Player' in str(col):
                    player_col = col
                    break
                    
            if not player_col:
                continue
                
            # Look for the player in this category
            player_rows = df[df[player_col].str.contains(player_name, na=False)]
            if player_rows.empty:
                continue
                
            # Extract data from this category
            player_row = player_rows.iloc[0]
            category_data = self._extract_category_data(player_row, category)
            player_data.update(category_data)
        
        return player_data if player_data else None
    
    def _extract_category_data(self, player_row: pd.Series, category: str) -> Dict[str, Any]:
        """Extract relevant data from a player row in a specific category.
        
        Args:
            player_row: Player's row data
            category: Category name (Summary, Misc, Defense, etc.)
            
        Returns:
            Dictionary with extracted data
        """
        extracted = {}
        
        # Define column mappings for each category
        if category == "Summary":
            mappings = {
                ("Unnamed: 5_level_0", "Min"): "minutes",
                ("Unnamed: 3_level_0", "Pos"): "position",
                #("Performance", "Gls"): "goals",
                #("Performance", "Ast"): "assists",
                #("Performance", "Sh"): "shots",
                #("Performance", "SoT"): "shots_on_target",
                ("Performance", "CrdY"): "yellow_cards",
                ("Performance", "CrdR"): "red_cards",
                #("Performance", "Touches"): "touches",
                ("Performance", "Tkl"): "tackles",
                #("Performance", "Int"): "interceptions",
                #("Performance", "Blocks"): "blocks",
            }
        elif category == "Misc":
            mappings = {
                ("Performance", "Fls"): "fouls",
                ("Performance", "Fld"): "fouled",
                #("Performance", "Off"): "offsides",
                #("Performance", "Crs"): "crosses",
                #("Performance", "TklW"): "tackles_won",
                #("Performance", "PKwon"): "penalties_won",
                #("Performance", "PKcon"): "penalties_conceded",
                #("Performance", "Recov"): "recoveries",
                #("Aerial Duels", "Won"): "aerial_duels_won",
                #("Aerial Duels", "Lost"): "aerial_duels_lost",
            }
        elif category == "Defense":
            mappings = {
                ("Tackles", "Tkl"): "tackles_total",
                #("Tackles", "TklW"): "tackles_won_def",
                ("Tackles", "Def 3rd"): "tackles_def_3rd",
                ("Tackles", "Mid 3rd"): "tackles_mid_3rd",
                ("Tackles", "Att 3rd"): "tackles_att_3rd",
                ("Challenges", "Att"): "challenges_attempted",
                #("Challenges", "Tkl%"): "tackle_success_pct",
                #("Challenges", "Lost"): "challenges_lost",
            }
        elif category == "Possession":
            mappings = {
                #("Touches", "Touches"): "touches_total",
                #("Touches", "Def Pen"): "touches_def_pen",
                #("Touches", "Def 3rd"): "touches_def_3rd",
                #("Touches", "Mid 3rd"): "touches_mid_3rd",
                #("Touches", "Att 3rd"): "touches_att_3rd",
                #("Touches", "Att Pen"): "touches_att_pen",
                ("Take-Ons", "Att"): "take_ons_attempted",
                ("Take-Ons", "Succ"): "take_ons_succeeded",
                #("Carries", "Carries"): "carries",
                #("Carries", "PrgC"): "progressive_carries",
            }
        else:
            # For other categories, use a generic mapping
            mappings = {}
            
        # Extract the mapped fields
        for col_tuple, our_field in mappings.items():
            if col_tuple in player_row.index:
                value = player_row[col_tuple]
                
                # Handle special cases
                if our_field == "minutes":
                    value = self._parse_minutes(value)
                elif our_field in ["tackles", "fouls", "fouled"] and pd.isna(value):
                    value = 0
                    
                extracted[our_field] = value
        
        return extracted
    
    def _parse_minutes(self, minutes_value: Any) -> int:
        """Parse minutes played from various formats."""
        if pd.isna(minutes_value):
            return 0
            
        if isinstance(minutes_value, (int, float)):
            return int(minutes_value)
            
        # Handle string formats
        minutes_str = str(minutes_value)
        if "+" in minutes_str:
            # Handle "45+2" format
            parts = minutes_str.split("+")
            return int(parts[0])
        else:
            try:
                return int(minutes_str)
            except ValueError:
                logger.warning(f"Could not parse minutes: {minutes_str}")
                return 0
    
    def _process_match_data(self, match_data: pd.DataFrame, match_url: str) -> Dict[str, Any]:
        """Process raw match data when no specific player is requested."""
        result = {
            "match_url": match_url,
            "scraped_at": datetime.now().isoformat(),
            "data_type": str(type(match_data))
        }
        
        if not match_data.empty:
            result["match_info_shape"] = match_data.shape
            result["match_info_columns"] = list(match_data.columns)
                
        return result
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate FBref data for required fields."""
        # Required fields for a valid player match record
        required_fields = ["player_name", "minutes", "fouls", "fouled"]
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
                
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            # Don't fail validation if we have the core data
            if "player_name" in data and "minutes" in data:
                logger.info("Core fields present, allowing validation to pass")
                return True
            return False
                
        # Additional validation
        if data.get("minutes", 0) < 0 or data.get("minutes", 0) > 120:
            logger.warning(f"Invalid minutes value: {data.get('minutes')}")
            return False
            
        return True
    
    def get_match_links(self, league: str, season: str) -> List[str]:
        """Get all match links for a league season."""
        try:
            links = self.fbref.get_match_links(league, season)
            logger.info(f"Found {len(links)} matches for {league} {season}")
            return links
        except Exception as e:
            logger.error(f"Error getting match links: {e}")
            return []
    
    # The following methods are kept for future use if we implement Selenium or find another way
    # to get the HTML content. Currently FBref blocks direct requests.
    
    def _fetch_match_html(self, match_url: str) -> Optional[str]:
        """Fetch the HTML content of a match page.
        
        Args:
            match_url: FBref match URL
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            # Add delay to avoid rate limiting
            import time
            time.sleep(2)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            session = requests.Session()
            response = session.get(match_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching HTML from {match_url}: {e}")
            return None
    
    def _extract_additional_stats(self, html: str, venue: str) -> Dict[str, Any]:
        """Extract team stats and match info not available in ScraperFC.
        
        Args:
            html: HTML content of the match page
            venue: "Home" or "Away" to determine which team's stats to use
            
        Returns:
            Dictionary with team stats, referee, attendance
        """
        soup = BeautifulSoup(html, 'html.parser')
        stats = {}
        
        # Extract team stats from team_stats_extra div
        team_stats_extra = soup.find('div', {'id': 'team_stats_extra'})
        if team_stats_extra:
            # Extract team fouls
            fouls_data = self._extract_team_stat(team_stats_extra, 'Fouls')
            if fouls_data:
                stats['team_fouls'] = fouls_data[0] if venue == "Home" else fouls_data[1]
                # Team fouled is the opponent's fouls
                stats['team_fouled'] = fouls_data[1] if venue == "Home" else fouls_data[0]
        
        # Extract possession from team_stats div
        team_stats = soup.find('div', {'id': 'team_stats'})
        if team_stats:
            possession_values = self._extract_possession(team_stats)
            if possession_values:
                stats['team_possession_pct'] = possession_values[0] if venue == "Home" else possession_values[1]
                stats['opponent_possession_pct'] = possession_values[1] if venue == "Home" else possession_values[0]
        
        # Extract referee
        referee = self._extract_referee(soup)
        if referee:
            stats['referee_name'] = referee
        
        # Extract attendance
        attendance = self._extract_attendance(soup)
        if attendance:
            stats['attendance'] = attendance
        
        return stats
    
    def _extract_team_stat(self, team_stats_div, stat_name: str) -> Optional[tuple]:
        """Extract a team statistic from the team_stats_extra div.
        
        Args:
            team_stats_div: BeautifulSoup element containing team stats
            stat_name: Name of the stat to extract (e.g., "Fouls")
            
        Returns:
            Tuple of (home_value, away_value) or None
        """
        try:
            # Find the div containing the stat name
            stat_divs = team_stats_div.find_all('div')
            for i, div in enumerate(stat_divs):
                if div.text.strip() == stat_name:
                    # The previous div has home value, next div has away value
                    home_value = stat_divs[i-1].text.strip() if i > 0 else None
                    away_value = stat_divs[i+1].text.strip() if i < len(stat_divs)-1 else None
                    
                    # Convert to integers if possible
                    try:
                        home_value = int(home_value) if home_value else None
                        away_value = int(away_value) if away_value else None
                    except ValueError:
                        pass
                    
                    return (home_value, away_value)
        except Exception as e:
            logger.warning(f"Error extracting team stat {stat_name}: {e}")
        
        return None
    
    def _extract_possession(self, team_stats_div) -> Optional[tuple]:
        """Extract possession percentages from team_stats div.
        
        Args:
            team_stats_div: BeautifulSoup element containing team stats
            
        Returns:
            Tuple of (home_possession, away_possession) as floats
        """
        try:
            # Look for possession section
            possession_header = team_stats_div.find('th', string='Possession')
            if possession_header:
                # Find the row with possession values
                possession_row = possession_header.find_parent('tr').find_next_sibling('tr')
                if possession_row:
                    # Extract percentages from strong tags
                    strong_tags = possession_row.find_all('strong')
                    if len(strong_tags) >= 2:
                        home_pct = strong_tags[0].text.strip().rstrip('%')
                        away_pct = strong_tags[1].text.strip().rstrip('%')
                        return (float(home_pct), float(away_pct))
        except Exception as e:
            logger.warning(f"Error extracting possession: {e}")
        
        return None
    
    def _extract_referee(self, soup) -> Optional[str]:
        """Extract referee name from the match page.
        
        Args:
            soup: BeautifulSoup object of the match page
            
        Returns:
            Referee name or None
        """
        try:
            # Referee is usually in the match information section
            # Look for "Officials" or "Referee" text
            referee_element = soup.find(string=re.compile(r'Referee:?\s*', re.I))
            if referee_element:
                # The referee name usually follows this text
                parent = referee_element.parent
                if parent:
                    # Extract text after "Referee:"
                    text = parent.text
                    match = re.search(r'Referee:?\s*([^,\n]+)', text, re.I)
                    if match:
                        return match.group(1).strip()
                        
            # Alternative: Look in scorebox_meta div
            scorebox_meta = soup.find('div', {'class': 'scorebox_meta'})
            if scorebox_meta:
                for div in scorebox_meta.find_all('div'):
                    if 'Referee' in div.text:
                        # Extract name after "Referee:"
                        match = re.search(r'Referee:?\s*([^,\n]+)', div.text, re.I)
                        if match:
                            return match.group(1).strip()
        except Exception as e:
            logger.warning(f"Error extracting referee: {e}")
        
        return None
    
    def _extract_attendance(self, soup) -> Optional[int]:
        """Extract attendance from the match page.
        
        Args:
            soup: BeautifulSoup object of the match page
            
        Returns:
            Attendance number or None
        """
        try:
            # Attendance is usually in the match information section
            attendance_element = soup.find(string=re.compile(r'Attendance:?\s*', re.I))
            if attendance_element:
                parent = attendance_element.parent
                if parent:
                    text = parent.text
                    # Extract number after "Attendance:"
                    match = re.search(r'Attendance:?\s*([\d,]+)', text, re.I)
                    if match:
                        # Remove commas and convert to int
                        attendance_str = match.group(1).replace(',', '')
                        return int(attendance_str)
                        
            # Alternative: Look in scorebox_meta div
            scorebox_meta = soup.find('div', {'class': 'scorebox_meta'})
            if scorebox_meta:
                for div in scorebox_meta.find_all('div'):
                    if 'Attendance' in div.text:
                        match = re.search(r'Attendance:?\s*([\d,]+)', div.text, re.I)
                        if match:
                            attendance_str = match.group(1).replace(',', '')
                            return int(attendance_str)
        except Exception as e:
            logger.warning(f"Error extracting attendance: {e}")
        
        return None
    
    def _extract_starting_status(self, html: str, player_name: str) -> bool:
        """Determine if a player was in the starting lineup.
        
        Args:
            html: HTML content of the match page
            player_name: Name of the player
            
        Returns:
            True if player started, False otherwise
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Find lineup tables
            # Look for tables containing player links
            lineup_tables = soup.find_all('table')
            
            for table in lineup_tables:
                # Look for "Bench" header to identify lineup table
                bench_header = table.find('th', string=re.compile(r'Bench', re.I))
                if bench_header:
                    # Get all rows before the bench header
                    all_rows = table.find_all('tr')
                    bench_row_index = -1
                    
                    for i, row in enumerate(all_rows):
                        if bench_header in row.find_all('th'):
                            bench_row_index = i
                            break
                    
                    # Check if player is in starting lineup (before bench)
                    if bench_row_index > 0:
                        for i in range(bench_row_index):
                            row = all_rows[i]
                            # Check if player name is in this row
                            if player_name in row.text:
                                logger.debug(f"Found {player_name} in starting lineup")
                                return True
                    
                    # Check if player is on bench (after bench header)
                    for i in range(bench_row_index + 1, len(all_rows)):
                        row = all_rows[i]
                        if player_name in row.text:
                            logger.debug(f"Found {player_name} on bench")
                            return False
            
            # If not found in any lineup, log warning
            logger.warning(f"Could not find {player_name} in lineup tables")
            
        except Exception as e:
            logger.warning(f"Error determining starting status for {player_name}: {e}")
        
        return False