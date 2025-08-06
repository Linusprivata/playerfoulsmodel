#!/usr/bin/env python3
"""Find Cole Palmer's foul-related stats."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from ScraperFC import FBref
import pandas as pd


def find_cole_fouls():
    """Find Cole Palmer's foul-related statistics."""
    print("Looking for Cole Palmer's foul statistics...")
    
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    
    fbref = FBref()
    result = fbref.scrape_match(match_url)
    
    # Get home team stats (Chelsea)
    home_stats = result.iloc[0]["Home Player Stats"]
    
    print("Available stat categories:")
    for category in home_stats.index:
        print(f"  - {category}")
    
    # Look through each category for foul-related columns
    for category in home_stats.index:
        df = home_stats[category]
        if isinstance(df, pd.DataFrame):
            # Look for foul-related columns
            foul_cols = [col for col in df.columns if 'Fls' in str(col) or 'Fld' in str(col) or 'Foul' in str(col)]
            if foul_cols:
                print(f"\n🔍 Found foul columns in '{category}' category: {foul_cols}")
                
                # Find Cole Palmer in this category
                player_col = None
                for col in df.columns:
                    if 'Player' in str(col):
                        player_col = col
                        break
                
                if player_col:
                    cole_rows = df[df[player_col].str.contains("Cole Palmer", na=False)]
                    if not cole_rows.empty:
                        print(f"Cole Palmer's {category} stats:")
                        cole_data = cole_rows.iloc[0]
                        for col in foul_cols:
                            print(f"  {col}: {cole_data[col]}")
                        
                        # Show all stats for context
                        print(f"\nAll Cole Palmer's {category} stats:")
                        for col in df.columns:
                            print(f"  {col}: {cole_data[col]}")
    
    # Check if Misc category has foul data
    if "Misc" in home_stats.index:
        print(f"\n📊 Detailed look at 'Misc' category:")
        misc_df = home_stats["Misc"]
        print(f"Misc columns: {list(misc_df.columns)}")
        
        # Find Cole Palmer in Misc
        player_col = None
        for col in misc_df.columns:
            if 'Player' in str(col):
                player_col = col
                break
                
        if player_col:
            cole_rows = misc_df[misc_df[player_col].str.contains("Cole Palmer", na=False)]
            if not cole_rows.empty:
                print("Cole Palmer's Misc stats (likely contains fouls):")
                cole_data = cole_rows.iloc[0]
                for col in misc_df.columns:
                    print(f"  {col}: {cole_data[col]}")


if __name__ == "__main__":
    find_cole_fouls()