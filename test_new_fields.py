"""Test script to verify all 7 new FBref fields are extracted correctly."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import json
from datetime import datetime
from loguru import logger

from src.scrapers.fbref import FBrefScraper
from src.data.database import init_database

def test_cole_palmer_match():
    """Test extraction of all fields for Cole Palmer match."""
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # Create scraper
    scraper = FBrefScraper()
    
    # Test match data
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    player_name = "Cole Palmer"
    
    logger.info(f"Scraping match data for {player_name} from {match_url}")
    
    try:
        # Scrape the match
        player_data = scraper.scrape_match(match_url, player_name)
        
        if not player_data:
            logger.error("No data retrieved")
            return
            
        # Validate the data
        if scraper.validate_data(player_data):
            logger.success("Data validation passed")
        else:
            logger.warning("Data validation failed - some fields may be missing")
        
        # Display the data with special focus on new fields
        logger.info("=" * 60)
        logger.info("EXTRACTED DATA:")
        logger.info("=" * 60)
        
        # Group fields by source
        basic_fields = ["player_name", "date", "competition", "venue", "opponent", 
                       "home_team", "away_team", "home_goals", "away_goals"]
        
        original_fbref_fields = ["position", "minutes", "fouls", "fouled", 
                                 "tackles", "tackles_def_3rd", "tackles_mid_3rd", 
                                 "tackles_att_3rd", "challenges_attempted", 
                                 "take_ons_attempted", "take_ons_succeeded",
                                 "yellow_cards", "red_cards"]
        
        new_fbref_fields = ["starting", "team_fouls", "team_fouled", 
                           "team_possession_pct", "opponent_possession_pct",
                           "referee_name", "attendance"]
        
        logger.info("BASIC MATCH INFO:")
        for field in basic_fields:
            if field in player_data:
                print(f"  {field}: {player_data[field]}")
        
        logger.info("\nORIGINAL FBREF FIELDS:")
        for field in original_fbref_fields:
            if field in player_data:
                print(f"  {field}: {player_data[field]}")
        
        logger.info("\n🔥 NEW FBREF FIELDS (7 missing fields):")
        for field in new_fbref_fields:
            value = player_data.get(field, "NOT FOUND")
            status = "✅" if field in player_data and player_data[field] is not None else "❌"
            print(f"  {status} {field}: {value}")
        
        # Check completeness
        missing_new_fields = [f for f in new_fbref_fields 
                             if f not in player_data or player_data[f] is None]
        
        if not missing_new_fields:
            logger.success("\n✅ ALL 7 NEW FIELDS SUCCESSFULLY EXTRACTED!")
        else:
            logger.error(f"\n❌ Missing new fields: {missing_new_fields}")
        
        # Save to JSON for inspection
        output_file = f"data/samples/test_new_fields_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(player_data, f, indent=2, default=str)
        
        logger.success(f"\nFull data saved to {output_file}")
        
        # Summary statistics
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY:")
        logger.info("=" * 60)
        total_fields = len(player_data)
        logger.info(f"Total fields extracted: {total_fields}")
        
        # Verify expected values based on HTML snippets
        expected_values = {
            "venue": "Home",  # Chelsea was home team
            "fouls": 0,  # Cole Palmer had 0 fouls
            "fouled": 3,  # Cole Palmer was fouled 3 times
            "team_fouls": 12,  # Chelsea had 12 fouls
            "team_fouled": 11,  # Chelsea was fouled 11 times (Nottingham's fouls)
            "team_possession_pct": 65.0,  # Chelsea had 65% possession
            "opponent_possession_pct": 35.0,  # Nottingham had 35% possession
            "starting": True,  # Cole Palmer was in starting lineup (not on bench)
        }
        
        logger.info("\nVERIFYING EXPECTED VALUES:")
        for field, expected in expected_values.items():
            actual = player_data.get(field)
            match = "✅" if actual == expected else "❌"
            print(f"  {match} {field}: expected={expected}, actual={actual}")
            
    except Exception as e:
        logger.error(f"Error collecting sample: {e}")
        raise

if __name__ == "__main__":
    test_cole_palmer_match()