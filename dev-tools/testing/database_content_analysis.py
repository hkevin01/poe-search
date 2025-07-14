#!/usr/bin/env python3
"""Check database content to see what data we actually have."""

import logging
import sqlite3
import sys
from pathlib import Path

# Set up logging
project_root = Path(__file__).parent.parent.parent
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "database_content_analysis.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def analyze_database(db_path):
    """Analyze a single database file."""
    logger.info(f"=== ANALYZING DATABASE: {db_path} ===")
    
    if not db_path.exists():
        logger.warning(f"Database file does not exist: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"Tables: {[table[0] for table in tables]}")
        
        for table_name in [table[0] for table in tables]:
            if table_name.startswith('sqlite_'):
                continue
                
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            logger.info(f"  {table_name}: {count} rows")
            
            # Get structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            logger.info(f"    Columns: {col_names}")
            
            # Get sample data if any exists
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()
                for i, sample in enumerate(samples):
                    sample_str = str(sample)[:100] + "..." if len(str(sample)) > 100 else str(sample)
                    logger.info(f"    Sample {i+1}: {sample_str}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error analyzing database {db_path}: {e}")


def main():
    """Analyze all database files."""
    logger.info("=== DATABASE CONTENT ANALYSIS ===")
    
    db_files = [
        project_root / "data" / "poe_search.db",
        project_root / "data" / "my_conversations.db",
        project_root / "data" / "test_conversations.db"
    ]
    
    for db_file in db_files:
        analyze_database(db_file)
    
    logger.info(f"=== ANALYSIS COMPLETE - Log: {log_file} ===")


if __name__ == "__main__":
    main()
