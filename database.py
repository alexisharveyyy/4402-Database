"""
Database initialization and connection module.
Handles SQLite database setup and provides connection utilities.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Database file path
DB_PATH = Path(__file__).parent / "restaurant.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Args:
        db_path: Optional custom path to database file.
        
    Returns:
        sqlite3.Connection: Database connection object.
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


@contextmanager
def get_db_cursor(db_path: Optional[Path] = None):
    """
    Context manager for database operations.
    Automatically handles connection and cursor lifecycle.
    
    Args:
        db_path: Optional custom path to database file.
        
    Yields:
        tuple: (connection, cursor) for database operations.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def init_database(db_path: Optional[Path] = None, schema_path: Optional[Path] = None) -> bool:
    """
    Initialize the database by executing the schema SQL file.
    
    Args:
        db_path: Optional custom path to database file.
        schema_path: Optional custom path to schema SQL file.
        
    Returns:
        bool: True if initialization was successful.
    """
    schema = schema_path or SCHEMA_PATH
    
    if not schema.exists():
        raise FileNotFoundError(f"Schema file not found: {schema}")
    
    with open(schema, 'r') as f:
        schema_sql = f.read()
    
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    
    try:
        conn.executescript(schema_sql)
        conn.commit()
        print(f"✓ Database initialized successfully at {path}")
        return True
    except sqlite3.Error as e:
        print(f"✗ Database initialization failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def check_database_exists(db_path: Optional[Path] = None) -> bool:
    """
    Check if the database file exists and has tables.
    
    Args:
        db_path: Optional custom path to database file.
        
    Returns:
        bool: True if database exists and has tables.
    """
    path = db_path or DB_PATH
    
    if not path.exists():
        return False
    
    try:
        with get_db_cursor(path) as (conn, cursor):
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            count = cursor.fetchone()[0]
            return count > 0
    except sqlite3.Error:
        return False


def get_table_counts(db_path: Optional[Path] = None) -> dict:
    """
    Get row counts for all tables in the database.
    
    Args:
        db_path: Optional custom path to database file.
        
    Returns:
        dict: Dictionary mapping table names to row counts.
    """
    tables = [
        'customers', 'employees', 'tables', 'categories',
        'menu_items', 'reservations', 'shifts', 'orders', 'order_items'
    ]
    
    counts = {}
    
    with get_db_cursor(db_path) as (conn, cursor):
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.Error:
                counts[table] = 0
    
    return counts


def reset_database(db_path: Optional[Path] = None) -> bool:
    """
    Drop all tables and reinitialize the database.
    
    Args:
        db_path: Optional custom path to database file.
        
    Returns:
        bool: True if reset was successful.
    """
    path = db_path or DB_PATH
    
    if path.exists():
        path.unlink()
        print(f"✓ Removed existing database: {path}")
    
    return init_database(path)


if __name__ == "__main__":
    # If run directly, initialize the database
    init_database()

