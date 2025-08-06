"""Test alternative approaches to get the missing FBref data."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ScraperFC import FBref as ScraperFCFBref
import pandas as pd
from loguru import logger
import time

def test_scraperfc_capabilities():
    """Test what else ScraperFC can provide."""
    
    fbref = ScraperFCFBref()
    
    logger.info("Testing ScraperFC capabilities...")
    
    # Check available methods
    logger.info("\nAvailable ScraperFC methods:")
    for method in dir(fbref):
        if not method.startswith('_'):
            logger.info(f"  - {method}")
    
    # Try to get team stats if available
    match_url = "https://fbref.com/en/matches/b9e00aac/Chelsea-Nottingham-Forest-October-6-2024-Premier-League"
    
    # Check if there's a method for team stats
    if hasattr(fbref, 'scrape_team_match_stats'):
        logger.info("\nTrying scrape_team_match_stats...")
        try:
            team_stats = fbref.scrape_team_match_stats(match_url)
            logger.info(f"Team stats: {team_stats}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    # Check if there's a method for match details
    if hasattr(fbref, 'scrape_match_details'):
        logger.info("\nTrying scrape_match_details...")
        try:
            match_details = fbref.scrape_match_details(match_url)
            logger.info(f"Match details: {match_details}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    # Check if we can get the lineup
    if hasattr(fbref, 'scrape_lineup'):
        logger.info("\nTrying scrape_lineup...")
        try:
            lineup = fbref.scrape_lineup(match_url)
            logger.info(f"Lineup: {lineup}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    # Try accessing the underlying session if it exists
    if hasattr(fbref, 'session') or hasattr(fbref, '_session'):
        logger.info("\nScraperFC has a session attribute - we might be able to use it")
        session = getattr(fbref, 'session', None) or getattr(fbref, '_session', None)
        if session:
            logger.info(f"Session type: {type(session)}")
    
    # Check if ScraperFC uses selenium or requests
    if hasattr(fbref, 'driver') or hasattr(fbref, '_driver'):
        logger.info("\nScraperFC might be using Selenium")
    
    # Try to understand how ScraperFC works internally
    logger.info("\nChecking ScraperFC internals...")
    
    # Look at the scrape_match source if possible
    import inspect
    try:
        source = inspect.getsource(fbref.scrape_match)
        logger.info("scrape_match source code preview:")
        lines = source.split('\n')[:10]
        for line in lines:
            logger.info(f"  {line}")
    except:
        logger.info("Cannot inspect source code")
    
    # Alternative: Use selenium ourselves for the missing data
    logger.info("\n" + "="*60)
    logger.info("RECOMMENDATION:")
    logger.info("="*60)
    logger.info("""
Since ScraperFC doesn't provide team stats, referee, attendance, or starting lineup,
and direct HTML requests are blocked, we have these options:

1. Use Selenium WebDriver to scrape the additional fields
2. Use a proxy service or different headers
3. Cache the HTML when ScraperFC fetches it (if we can hook into it)
4. Accept that these fields are not available from FBref for now
5. Get these fields from Sofascore or Whoscored instead

For now, let's proceed with the data we CAN get from FBref (25 fields)
and move on to Sofascore/Whoscored integration which might have these fields.
""")

if __name__ == "__main__":
    test_scraperfc_capabilities()