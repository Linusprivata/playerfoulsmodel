"""Base scraper class for all data sources."""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import os

from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self):
        self.scrape_delay = float(os.getenv("SCRAPE_DELAY", "2"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))
        
    def _wait(self):
        """Wait between requests to be respectful."""
        time.sleep(self.scrape_delay)
        
    @abstractmethod
    def scrape_match(self, match_id: str, **kwargs) -> Dict[str, Any]:
        """Scrape data for a single match.
        
        Args:
            match_id: Unique identifier for the match
            **kwargs: Additional parameters specific to the data source
            
        Returns:
            Dictionary containing scraped match data
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate scraped data for completeness and correctness.
        
        Args:
            data: Scraped data dictionary
            
        Returns:
            True if data is valid, False otherwise
        """
        pass
    
    def scrape_with_retry(self, match_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Scrape with retry logic.
        
        Args:
            match_id: Unique identifier for the match
            **kwargs: Additional parameters
            
        Returns:
            Scraped data or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping {match_id}, attempt {attempt + 1}/{self.max_retries}")
                data = self.scrape_match(match_id, **kwargs)
                
                if self.validate_data(data):
                    logger.success(f"Successfully scraped {match_id}")
                    return data
                else:
                    logger.warning(f"Invalid data for {match_id}")
                    
            except Exception as e:
                logger.error(f"Error scraping {match_id}: {e}")
                if attempt < self.max_retries - 1:
                    self._wait()
                    
        logger.error(f"Failed to scrape {match_id} after {self.max_retries} attempts")
        return None