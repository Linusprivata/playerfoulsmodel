"""Inspect what data ScraperFC actually provides."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ScraperFC import FBref as ScraperFCFBref
import pandas as pd
from loguru import logger
import json

def inspect_scraperfc_data():
    """Deep inspection of ScraperFC data structure."""
    
    fbref = ScraperFCFBref()
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    
    logger.info(f"Scraping match data from {match_url}")
    
    try:
        # Get raw match data
        match_data = fbref.scrape_match(match_url)
        
        if match_data is None or match_data.empty:
            logger.error("No data returned")
            return
            
        logger.info(f"Match data shape: {match_data.shape}")
        logger.info(f"Match data columns: {list(match_data.columns)}")
        
        # Get first row
        row = match_data.iloc[0]
        
        # Check for team stats in the data
        logger.info("\n" + "="*60)
        logger.info("SEARCHING FOR TEAM STATS IN DATA:")
        logger.info("="*60)
        
        for col in match_data.columns:
            if 'team' in str(col).lower() or 'stat' in str(col).lower():
                logger.info(f"\nFound potential team stats column: {col}")
                value = row[col]
                if isinstance(value, pd.DataFrame):
                    logger.info(f"  - DataFrame shape: {value.shape}")
                    logger.info(f"  - Columns: {list(value.columns)[:10]}...")
                elif isinstance(value, pd.Series):
                    logger.info(f"  - Series length: {len(value)}")
                    logger.info(f"  - Index: {list(value.index)[:10]}...")
                else:
                    logger.info(f"  - Type: {type(value)}")
                    logger.info(f"  - Value: {value}")
        
        # Check Home and Away team stats
        logger.info("\n" + "="*60)
        logger.info("HOME AND AWAY TEAM STATS:")
        logger.info("="*60)
        
        if "Home Team Stats" in match_data.columns:
            home_stats = row["Home Team Stats"]
            logger.info("\nHome Team Stats structure:")
            logger.info(f"Type: {type(home_stats)}")
            if isinstance(home_stats, pd.Series):
                for category in home_stats.index:
                    logger.info(f"\n  Category: {category}")
                    df = home_stats[category]
                    if isinstance(df, pd.DataFrame):
                        logger.info(f"    Shape: {df.shape}")
                        # Look for team-level stats
                        if df.shape[0] == 1 or 'Team' in str(df.index):
                            logger.info(f"    Possible team stats! First row:")
                            logger.info(f"    {df.iloc[0] if not df.empty else 'Empty'}")
        
        if "Away Team Stats" in match_data.columns:
            away_stats = row["Away Team Stats"]
            logger.info("\nAway Team Stats structure:")
            logger.info(f"Type: {type(away_stats)}")
            if isinstance(away_stats, pd.Series):
                for category in away_stats.index:
                    logger.info(f"\n  Category: {category}")
                    df = away_stats[category]
                    if isinstance(df, pd.DataFrame):
                        logger.info(f"    Shape: {df.shape}")
                        # Look for team-level stats
                        if df.shape[0] == 1 or 'Team' in str(df.index):
                            logger.info(f"    Possible team stats! First row:")
                            logger.info(f"    {df.iloc[0] if not df.empty else 'Empty'}")
        
        # Check for match info columns
        logger.info("\n" + "="*60)
        logger.info("MATCH INFO COLUMNS:")
        logger.info("="*60)
        
        for col in match_data.columns:
            if any(keyword in str(col).lower() for keyword in ['referee', 'attendance', 'venue', 'stadium']):
                logger.info(f"Found: {col} = {row[col]}")
        
        # Check all columns that are not dataframes/series
        logger.info("\n" + "="*60)
        logger.info("ALL SIMPLE COLUMNS (non-DataFrame/Series):")
        logger.info("="*60)
        
        for col in match_data.columns:
            value = row[col]
            if not isinstance(value, (pd.DataFrame, pd.Series)):
                logger.info(f"{col}: {value}")
        
        # Save full structure for manual inspection
        output_file = "data/samples/scraperfc_full_structure.txt"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("FULL SCRAPERFC DATA STRUCTURE\n")
            f.write("="*60 + "\n\n")
            
            for col in match_data.columns:
                f.write(f"\nColumn: {col}\n")
                f.write("-"*40 + "\n")
                value = row[col]
                f.write(f"Type: {type(value)}\n")
                
                if isinstance(value, pd.DataFrame):
                    f.write(f"DataFrame shape: {value.shape}\n")
                    f.write(f"Columns: {list(value.columns)}\n")
                    if not value.empty:
                        f.write("First few rows:\n")
                        f.write(str(value.head()) + "\n")
                elif isinstance(value, pd.Series):
                    f.write(f"Series length: {len(value)}\n")
                    f.write(f"Index: {list(value.index)}\n")
                    f.write("Content:\n")
                    for idx in value.index:
                        f.write(f"  {idx}: {type(value[idx])} - shape {value[idx].shape if hasattr(value[idx], 'shape') else 'N/A'}\n")
                else:
                    f.write(f"Value: {value}\n")
        
        logger.success(f"Full structure saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    inspect_scraperfc_data()