#!/usr/bin/env python3
"""Verify that the project setup is working correctly."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger


def test_database_connection():
    """Test that we can connect to the database."""
    try:
        from src.data.database import get_db
        
        db = get_db()
        with db.connect() as conn:
            # Test basic query
            result = conn.execute("SELECT 1 as test").fetchone()
            if result[0] == 1:
                logger.success("✓ Database connection working")
                return True
            else:
                logger.error("✗ Database query returned unexpected result")
                return False
                
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False


def test_scraper_imports():
    """Test that scraper imports work."""
    try:
        from src.scrapers.fbref import FBrefScraper
        scraper = FBrefScraper()
        logger.success("✓ FBref scraper import working")
        return True
        
    except Exception as e:
        logger.error(f"✗ Scraper import failed: {e}")
        return False


def test_scraperfc_library():
    """Test that ScraperFC library is working."""
    try:
        from ScraperFC import FBref
        fbref = FBref()
        logger.success("✓ ScraperFC library import working")
        return True
        
    except Exception as e:
        logger.error(f"✗ ScraperFC library failed: {e}")
        return False


def test_database_schema():
    """Test that database tables exist."""
    try:
        from src.data.database import get_db
        
        db = get_db()
        with db.connect() as conn:
            # Check if our main table exists
            tables = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'main'
            """).fetchall()
            
            table_names = [table[0] for table in tables]
            expected_tables = ['player_match_stats', 'players', 'teams', 'referees', 'matches']
            
            missing_tables = [table for table in expected_tables if table not in table_names]
            
            if not missing_tables:
                logger.success(f"✓ All database tables exist: {', '.join(expected_tables)}")
                return True
            else:
                logger.error(f"✗ Missing database tables: {', '.join(missing_tables)}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Database schema check failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("Player Fouls Model - Setup Verification")
    print("======================================")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Scraper Imports", test_scraper_imports),
        ("ScraperFC Library", test_scraperfc_library),
        ("Database Schema", test_database_schema),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("VERIFICATION RESULTS:")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:<20}: {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python scripts/collect_sample.py")
        print("2. Test with a real FBref match URL")
        print("3. Example URL format: https://fbref.com/en/matches/[match-id]/[match-name]")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())