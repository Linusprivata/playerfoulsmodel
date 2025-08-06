#!/usr/bin/env python3
"""Detailed debug of ScraperFC structure."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from ScraperFC import FBref
import pandas as pd


def debug_detailed():
    """Debug the nested structure in detail."""
    print("Detailed ScraperFC Analysis")
    print("==========================")
    
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    
    fbref = FBref()
    result = fbref.scrape_match(match_url)
    
    if "Home Player Stats" in result.columns:
        print("\n🏠 HOME TEAM PLAYER STATS:")
        home_stats = result.iloc[0]["Home Player Stats"]
        
        for category in home_stats.index:
            df = home_stats[category]
            print(f"\n  {category}:")
            if isinstance(df, pd.DataFrame):
                print(f"    Shape: {df.shape}")
                print(f"    Columns: {list(df.columns)[:10]}...")  # First 10 columns
                # Look for player names
                for col in df.columns:
                    if 'player' in col.lower() or 'name' in col.lower() or col == 'Player':
                        print(f"    Player column '{col}' contains:")
                        for i, player in enumerate(df[col].head()):
                            print(f"      {i}: {player}")
                        break
            else:
                print(f"    Type: {type(df)}")
    
    if "Away Player Stats" in result.columns:
        print("\n🏃 AWAY TEAM PLAYER STATS:")
        away_stats = result.iloc[0]["Away Player Stats"]
        
        for category in away_stats.index:
            df = away_stats[category]
            print(f"\n  {category}:")
            if isinstance(df, pd.DataFrame):
                print(f"    Shape: {df.shape}")
                print(f"    Columns: {list(df.columns)[:10]}...")  # First 10 columns
                # Look for player names and Cole Palmer specifically
                for col in df.columns:
                    if 'player' in col.lower() or 'name' in col.lower() or col == 'Player':
                        print(f"    Player column '{col}' contains:")
                        for i, player in enumerate(df[col].head(10)):  # Show first 10 players
                            marker = "🎯" if "Cole Palmer" in str(player) else "  "
                            print(f"    {marker} {i}: {player}")
                        break
            else:
                print(f"    Type: {type(df)}")


if __name__ == "__main__":
    debug_detailed()