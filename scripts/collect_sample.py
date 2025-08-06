"""Script to collect a single sample row of player match data."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
from datetime import datetime
from loguru import logger
import pandas as pd

from src.scrapers.fbref import FBrefScraper
from src.data.database import init_database, get_db


def collect_sample_match():
    """Collect data for a single match as a test."""
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # Create scraper
    scraper = FBrefScraper()
    
    # Example match URL 
    # Format: https://fbref.com/en/matches/[match-id]/[match-name]
    match_url = input("Enter FBref match URL: ").strip()
    player_name = input("Enter player name to search for: ").strip()
    
    if not match_url or not player_name:
        logger.error("Match URL and player name are required")
        return
    
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
        
        # Display the data
        logger.info("Scraped data:")
        for key, value in player_data.items():
            print(f"  {key}: {value}")
        
        # Save to JSON for inspection
        output_file = f"data/samples/sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(player_data, f, indent=2, default=str)
        
        logger.success(f"Sample data saved to {output_file}")
        
        # Optionally save to database
        save_to_db = input("Save to database? (y/n): ").strip().lower()
        if save_to_db == 'y':
            save_sample_to_db(player_data)
            
    except Exception as e:
        logger.error(f"Error collecting sample: {e}")
        raise


def save_sample_to_db(data: dict):
    """Save sample data to database."""
    db = get_db()
    
    try:
        with db.connect() as conn:
            # Insert into player_match_stats table
            conn.execute("""
                INSERT INTO player_match_stats (
                    player_name, match_url, date, competition, venue,
                    starting, position, minutes, fouls, fouled,
                    team_fouls, team_fouled, team_possession_pct, opponent_possession_pct,
                    referee_name, attendance, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('player_name'),
                data.get('match_url'),
                data.get('date'),
                data.get('competition'),
                data.get('venue'),
                data.get('starting'),
                data.get('position'),
                data.get('minutes'),
                data.get('fouls'),
                data.get('fouled'),
                data.get('team_fouls'),
                data.get('team_fouled'),
                data.get('team_possession_pct'),
                data.get('opponent_possession_pct'),
                data.get('referee_name'),
                data.get('attendance'),
                data.get('scraped_at')
            ))
            
            conn.commit()
            logger.success("Data saved to database")
            
    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        raise


def inspect_match_structure():
    """Inspect the structure of FBref match data."""
    scraper = FBrefScraper()
    
    match_url = input("Enter FBref match URL to inspect structure: ").strip()
    
    if not match_url:
        logger.error("Match URL is required")
        return
        
    logger.info(f"Inspecting match structure for {match_url}")
    
    try:
        # Get raw match data
        match_data = scraper.fbref.scrape_match(match_url)
        
        if match_data is None:
            logger.error("No data returned")
            return
            
        # Inspect each DataFrame in the tuple
        logger.info(f"Match data contains {len(match_data)} DataFrames")
        
        for i, df in enumerate(match_data):
            if df is not None and isinstance(df, pd.DataFrame):
                logger.info(f"\nDataFrame {i}:")
                logger.info(f"  Shape: {df.shape}")
                logger.info(f"  Columns: {list(df.columns)}")
                if not df.empty:
                    logger.info(f"  First row sample:")
                    print(df.iloc[0])
            else:
                logger.info(f"\nDataFrame {i}: None or not a DataFrame")
                
    except Exception as e:
        logger.error(f"Error inspecting match: {e}")
        raise


def get_raw_dataframe():
    """Get raw DataFrame for experimentation."""
    scraper = FBrefScraper()
    
    match_url = input("Enter FBref match URL: ").strip()
    player_name = input("Enter player name: ").strip()
    
    if not match_url or not player_name:
        logger.error("Match URL and player name are required")
        return None
    
    logger.info(f"Getting raw data for {player_name} from {match_url}")
    
    try:
        # Get raw match data
        raw_match_data = scraper.fbref.scrape_match(match_url)
        
        # Save to file for easy loading in IPython
        import pickle
        filename = f"data/samples/raw_data_{player_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'wb') as f:
            pickle.dump((raw_match_data, player_name), f)
        
        logger.success(f"Raw data saved to {filename}")
        print(f"\nTo load in IPython, run:")
        print(f"import pickle")
        print(f"with open('{filename}', 'rb') as f:")
        print(f"    raw_data, player_name = pickle.load(f)")
        
        return raw_match_data, player_name
    except Exception as e:
        logger.error(f"Error getting raw data: {e}")
        return None


def get_player_data_for_experiment():
    """Get final processed player data for experimentation."""
    scraper = FBrefScraper()
    
    match_url = input("Enter FBref match URL: ").strip()
    player_name = input("Enter player name: ").strip()
    
    if not match_url or not player_name:
        logger.error("Match URL and player name are required")
        return None
    
    logger.info(f"Getting processed data for {player_name} from {match_url}")
    
    try:
        # Get the final processed player data
        player_data = scraper.scrape_match(match_url, player_name)
        
        if not player_data:
            logger.error("No data retrieved")
            return None
        
        # Save to file for easy loading in IPython
        import pickle
        filename = f"data/samples/player_data_{player_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'wb') as f:
            pickle.dump((player_data, player_name), f)
        
        logger.success(f"Player data saved to {filename}")
        print(f"\nTo load in IPython, run:")
        print(f"import pickle")
        print(f"with open('{filename}', 'rb') as f:")
        print(f"    player_data, player_name = pickle.load(f)")
        print(f"\nPlayer data keys: {list(player_data.keys())}")
        
        return player_data, player_name
    except Exception as e:
        logger.error(f"Error getting player data: {e}")
        return None


if __name__ == "__main__":
    print("Player Fouls Data Collection - Sample Test")
    print("==========================================")
    print("1. Collect sample match data for a player")
    print("2. Inspect FBref match data structure")
    print("3. Get raw DataFrame for experimentation")
    print("4. Get final player data for experimentation")
    
    choice = input("\nEnter choice (1, 2, 3, or 4): ").strip()
    
    if choice == "1":
        collect_sample_match()
    elif choice == "2":
        inspect_match_structure()
    elif choice == "3":
        result = get_raw_dataframe()
        if result:
            raw_data, player_name = result
            print(f"\nRaw DataFrame data for {player_name}:")
            print("=" * 50)
            print("Use this in IPython to experiment:")
            print(f"raw_data = {raw_data}")
            print(f"player_name = '{player_name}'")
    elif choice == "4":
        result = get_player_data_for_experiment()
        if result:
            player_data, player_name = result
            print(f"\nFinal player data for {player_name}:")
            print("=" * 50)
            print("Use this in IPython to experiment:")
            print(f"player_data = {player_data}")
            print(f"player_name = '{player_name}'")
    else:
        print("Invalid choice")