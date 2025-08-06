#!/usr/bin/env python3
"""Find Cole Palmer in the match data."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from ScraperFC import FBref
import pandas as pd


def find_cole_palmer():
    """Find Cole Palmer in the match data."""
    print("Looking for Cole Palmer...")
    
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    
    fbref = FBref()
    result = fbref.scrape_match(match_url)
    
    # First, let's see which team is which
    print(f"Home Team: {result.iloc[0]['Home Team']}")
    print(f"Away Team: {result.iloc[0]['Away Team']}")
    
    # Check home team stats first
    print("\n=== HOME TEAM STATS ===")
    home_stats = result.iloc[0]["Home Player Stats"]
    home_summary_df = home_stats["Summary"]
    
    # Find the player column and look for Cole Palmer
    for col in home_summary_df.columns:
        if 'Player' in str(col):
            players = home_summary_df[col]
            print("Home team players:")
            for i, player in enumerate(players):
                marker = "🎯" if "Cole Palmer" in str(player) else "  "
                print(f"{marker} {i}: {player}")
                
            # Try to find Cole Palmer specifically
            cole_palmer_rows = home_summary_df[home_summary_df[col].str.contains("Cole Palmer", na=False)]
            if not cole_palmer_rows.empty:
                print(f"\n✓ Found Cole Palmer in HOME team!")
                print("Cole Palmer's summary data:")
                cole_data = cole_palmer_rows.iloc[0]
                
                # Show his key stats
                print("\nCole Palmer's key stats from Summary:")
                for col_name in home_summary_df.columns:
                    value = cole_data[col_name]
                    if 'Performance' in str(col_name) or 'Min' in str(col_name):
                        print(f"  {col_name}: {value}")
                return True
            break
    
    # Check away team stats
    print("\n=== AWAY TEAM STATS ===")
    away_stats = result.iloc[0]["Away Player Stats"]
    summary_df = away_stats["Summary"]
    
    print(f"Summary DataFrame shape: {summary_df.shape}")
    print(f"Summary DataFrame columns: {summary_df.columns}")
    
    # Find the player column
    for col in summary_df.columns:
        if 'Player' in str(col):
            print(f"\nFound player column: {col}")
            players = summary_df[col]
            print("Players in this match:")
            for i, player in enumerate(players):
                marker = "🎯" if "Cole Palmer" in str(player) else "  "
                print(f"{marker} {i}: {player}")
            
            # Try to find Cole Palmer
            cole_palmer_rows = summary_df[summary_df[col].str.contains("Cole Palmer", na=False)]
            if not cole_palmer_rows.empty:
                print(f"\n✓ Found Cole Palmer!")
                print("Cole Palmer's data:")
                cole_data = cole_palmer_rows.iloc[0]
                print(cole_data)
                
                # Show his stats
                print("\nCole Palmer's key stats:")
                for col_name in summary_df.columns:
                    value = cole_data[col_name]
                    print(f"  {col_name}: {value}")
            else:
                print("\n✗ Cole Palmer not found")
            break


if __name__ == "__main__":
    find_cole_palmer()