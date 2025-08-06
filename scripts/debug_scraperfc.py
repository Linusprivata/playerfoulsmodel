#!/usr/bin/env python3
"""Debug script to understand ScraperFC data format."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from ScraperFC import FBref
import pandas as pd


def debug_scraperfc():
    """Debug what ScraperFC actually returns."""
    print("Testing ScraperFC with Chelsea vs Nottingham Forest match...")
    
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    
    fbref = FBref()
    
    try:
        print("Calling fbref.scrape_match()...")
        result = fbref.scrape_match(match_url)
        
        print(f"\nResult type: {type(result)}")
        
        if result is None:
            print("Result is None - ScraperFC failed to scrape")
            return
            
        if isinstance(result, tuple):
            print(f"Result is a tuple with {len(result)} elements")
            for i, item in enumerate(result):
                print(f"  Element {i}: {type(item)}")
                if isinstance(item, pd.DataFrame):
                    print(f"    Shape: {item.shape}")
                    print(f"    Columns: {list(item.columns)[:10]}...")  # First 10 columns
                    
        elif isinstance(result, pd.DataFrame):
            print("Result is a single DataFrame")
            print(f"  Shape: {result.shape}")
            print(f"  Columns: {list(result.columns)}")
            
            # Look for player columns
            player_columns = [col for col in result.columns if 'player' in col.lower() or 'name' in col.lower()]
            print(f"  Player-related columns: {player_columns}")
            
            # Show first few rows
            print("\nFirst 5 rows:")
            print(result.head())
            
            # Look at the nested player stats
            if "Home Player Stats" in result.columns:
                home_stats = result.iloc[0]["Home Player Stats"]
                print(f"\nHome Player Stats type: {type(home_stats)}")
                print(f"Home Player Stats content:\n{home_stats}")
                    
            if "Away Player Stats" in result.columns:
                away_stats = result.iloc[0]["Away Player Stats"]
                print(f"\nAway Player Stats type: {type(away_stats)}")
                print(f"Away Player Stats content:\n{away_stats}")
                
                # Check if Cole Palmer is in away stats
                if isinstance(away_stats, pd.Series):
                    away_str = str(away_stats)
                    if "Cole Palmer" in away_str:
                        print("\n✓ Found 'Cole Palmer' in Away Player Stats!")
                    else:
                        print("\n✗ 'Cole Palmer' not found in Away Player Stats")
                        print("Looking for similar names...")
                        if "Palmer" in away_str:
                            print("  Found 'Palmer'")
                        if "Cole" in away_str:
                            print("  Found 'Cole'")
            
        elif isinstance(result, dict):
            print("Result is a dictionary")
            print(f"  Keys: {list(result.keys())}")
            
        else:
            print(f"Result is something else: {type(result)}")
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_scraperfc()