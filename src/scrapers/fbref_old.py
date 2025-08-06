"""FBref scraper using ScraperFC library."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
from loguru import logger

try:
    from ScraperFC import FBref as ScraperFCFBref
except ImportError:
    logger.error("ScraperFC not installed. Run: pip install ScraperFC")
    raise

from .base import BaseScraper


class FBrefScraper(BaseScraper):
    """Scraper for FBref data using ScraperFC."""
    
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
            
            if match_data is None:
                logger.error(f"No data returned for {match_url}")
                return {}
            
            # Extract player-specific data
            if player_name:
                player_data = self._extract_player_data(match_data, player_name, match_url)
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
            "competition": "Premier League",  # Could extract from Stage column
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
            if isinstance(home_stats, pd.DataFrame):
                player_row = self._find_player_in_stats(home_stats, player_name)
                if player_row is not None:
                    result.update(self._extract_player_row(player_row))
                    result["venue"] = "Home"
                    result["opponent"] = row.get("Away Team")
                    player_found = True
        
        # Check away team stats if not found in home
        if not player_found and "Away Player Stats" in match_data.columns:
            away_stats = row["Away Player Stats"]
            if isinstance(away_stats, pd.DataFrame):
                player_row = self._find_player_in_stats(away_stats, player_name)
                if player_row is not None:
                    result.update(self._extract_player_row(player_row))
                    result["venue"] = "Away"
                    result["opponent"] = row.get("Home Team")
                    player_found = True
        
        if not player_found:
            logger.warning(f"Player {player_name} not found in match {match_url}")
            
        return result
    
    def _find_player_in_stats(self, player_stats: pd.DataFrame, player_name: str) -> Optional[pd.Series]:
        """Find a player in the player stats DataFrame.
        
        Args:
            player_stats: DataFrame containing player statistics
            player_name: Name of the player to find
            
        Returns:
            Player row as Series, or None if not found
        """
        if player_stats.empty:
            return None
            
        # Look for common player column names
        player_cols = [col for col in player_stats.columns if 'player' in col.lower() or 'name' in col.lower()]
        
        for col in player_cols:
            matches = player_stats[player_stats[col] == player_name]
            if not matches.empty:
                return matches.iloc[0]
        
        # Also try direct column name "Player" if it exists
        if "Player" in player_stats.columns:
            matches = player_stats[player_stats["Player"] == player_name]
            if not matches.empty:
                return matches.iloc[0]
                
        logger.debug(f"Available columns in player stats: {list(player_stats.columns)}")
        if not player_stats.empty:
            logger.debug(f"Sample player names: {player_stats.iloc[:3].to_dict()}")
            
        return None
    
    def _extract_player_row(self, player_row: pd.Series) -> Dict[str, Any]:
        """Extract relevant statistics from a player's row.
        
        Args:
            player_row: Pandas Series containing player statistics
            
        Returns:
            Dictionary with extracted statistics
        """
        # Map FBref column names to our schema
        column_mapping = {
            "Min": "minutes",
            "Fls": "fouls",
            "Fld": "fouled",
            "Tkl": "tackles",
            "Tkl.1": "tackles_won",  # May need adjustment based on actual columns
            "Def 3rd": "tackles_def_3rd",
            "Mid 3rd": "tackles_mid_3rd",
            "Att 3rd": "tackles_att_3rd",
            "Tkl%": "tackle_success_pct",
            "Lost": "challenges_lost",
            "Blocks": "blocks",
            "Att": "take_ons_attempted",
            "Succ": "take_ons_succeeded",
            "Pos": "position",
            "Start": "starting",
        }
        
        extracted = {}
        for fbref_col, our_col in column_mapping.items():
            if fbref_col in player_row:
                value = player_row[fbref_col]
                # Handle different data types
                if our_col == "starting":
                    extracted[our_col] = value == "Y" or value == True
                elif our_col == "minutes":
                    # Handle substitution notation (e.g., "90" or "45+2")
                    extracted[our_col] = self._parse_minutes(value)
                else:
                    extracted[our_col] = value
                    
        return extracted
    
    def _parse_minutes(self, minutes_str: Any) -> int:
        """Parse minutes played from various formats.
        
        Args:
            minutes_str: Minutes string (e.g., "90", "45+2", 90)
            
        Returns:
            Integer minutes played
        """
        if pd.isna(minutes_str):
            return 0
            
        if isinstance(minutes_str, (int, float)):
            return int(minutes_str)
            
        # Handle string formats
        minutes_str = str(minutes_str)
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
        """Process raw match data when no specific player is requested.
        
        Args:
            match_data: DataFrame from ScraperFC
            match_url: Match URL
            
        Returns:
            Dictionary with match information
        """
        result = {
            "match_url": match_url,
            "scraped_at": datetime.now().isoformat(),
            "data_type": str(type(match_data))
        }
        
        # Add basic match info if available
        if not match_data.empty:
            result["match_info_shape"] = match_data.shape
            result["match_info_columns"] = list(match_data.columns)
                
        return result
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate FBref data for required fields.
        
        Args:
            data: Scraped data dictionary
            
        Returns:
            True if data contains minimum required fields
        """
        # Required fields for a valid player match record
        required_fields = ["player_name", "minutes", "fouls", "fouled"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False
                
        # Additional validation
        if data.get("minutes", 0) < 0 or data.get("minutes", 0) > 120:
            logger.warning(f"Invalid minutes value: {data.get('minutes')}")
            return False
            
        return True
    
    def get_match_links(self, league: str, season: str) -> List[str]:
        """Get all match links for a league season.
        
        Args:
            league: League identifier (e.g., "Premier-League")
            season: Season identifier (e.g., "2023-2024")
            
        Returns:
            List of match URLs
        """
        try:
            links = self.fbref.get_match_links(league, season)
            logger.info(f"Found {len(links)} matches for {league} {season}")
            return links
        except Exception as e:
            logger.error(f"Error getting match links: {e}")
            return []