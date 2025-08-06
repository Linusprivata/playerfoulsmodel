"""DuckDB database connection and initialization."""

import os
from pathlib import Path
from typing import Optional
import duckdb
from loguru import logger
from dotenv import load_dotenv

from .schema import ALL_SCHEMAS

load_dotenv()


class Database:
    """DuckDB database connection manager."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to DuckDB database file. If None, uses env variable.
        """
        self.db_path = db_path or os.getenv("DUCKDB_PATH", "data/duckdb/playerfouls.db")
        self._ensure_db_directory()
        self.conn = None
        
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Database directory ensured: {db_dir}")
        
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Create or return database connection."""
        if self.conn is None:
            self.conn = duckdb.connect(self.db_path)
            logger.info(f"Connected to DuckDB at {self.db_path}")
        return self.conn
    
    def initialize_schema(self):
        """Create all tables if they don't exist."""
        conn = self.connect()
        for schema in ALL_SCHEMAS:
            try:
                conn.execute(schema)
                logger.debug(f"Schema created/verified")
            except Exception as e:
                logger.error(f"Error creating schema: {e}")
                raise
        conn.commit()
        logger.info("All database schemas initialized")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_db() -> Database:
    """Get database instance."""
    return Database()


def init_database():
    """Initialize database with all schemas."""
    db = get_db()
    db.initialize_schema()
    db.close()
    logger.info("Database initialization complete")