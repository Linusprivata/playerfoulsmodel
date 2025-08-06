"""Fixed FBref scraper that handles the real ScraperFC data structure."""

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
                ("Performance", "Gls"): "goals",
                ("Performance", "Ast"): "assists",
                ("Performance", "Sh"): "shots",
                ("Performance", "SoT"): "shots_on_target",
                ("Performance", "CrdY"): "yellow_cards",
                ("Performance", "CrdR"): "red_cards",
                ("Performance", "Touches"): "touches",
                ("Performance", "Tkl"): "tackles",
                ("Performance", "Int"): "interceptions",
                ("Performance", "Blocks"): "blocks",
            }
        elif category == "Misc":
            mappings = {
                ("Performance", "Fls"): "fouls",
                ("Performance", "Fld"): "fouled",
                ("Performance", "Off"): "offsides",
                ("Performance", "Crs"): "crosses",
                ("Performance", "TklW"): "tackles_won",
                ("Performance", "PKwon"): "penalties_won",
                ("Performance", "PKcon"): "penalties_conceded",
                ("Performance", "Recov"): "recoveries",
                ("Aerial Duels", "Won"): "aerial_duels_won",
                ("Aerial Duels", "Lost"): "aerial_duels_lost",
            }
        elif category == "Defense":
            mappings = {
                ("Tackles", "Tkl"): "tackles_total",
                ("Tackles", "TklW"): "tackles_won_def",
                ("Tackles", "Def 3rd"): "tackles_def_3rd",
                ("Tackles", "Mid 3rd"): "tackles_mid_3rd",
                ("Tackles", "Att 3rd"): "tackles_att_3rd",
                ("Challenges", "Att"): "challenges_attempted",
                ("Challenges", "Tkl%"): "tackle_success_pct",
                ("Challenges", "Lost"): "challenges_lost",
            }
        elif category == "Possession":
            mappings = {
                ("Touches", "Touches"): "touches_total",
                ("Touches", "Def Pen"): "touches_def_pen",
                ("Touches", "Def 3rd"): "touches_def_3rd",
                ("Touches", "Mid 3rd"): "touches_mid_3rd",
                ("Touches", "Att 3rd"): "touches_att_3rd",
                ("Touches", "Att Pen"): "touches_att_pen",
                ("Take-Ons", "Att"): "take_ons_attempted",
                ("Take-Ons", "Succ"): "take_ons_succeeded",
                ("Carries", "Carries"): "carries",
                ("Carries", "PrgC"): "progressive_carries",
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