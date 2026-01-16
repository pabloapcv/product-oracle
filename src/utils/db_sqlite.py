"""
SQLite database adapter for Winner Engine (development/demo mode).
This provides a drop-in replacement for the PostgreSQL connection.
"""
import os
import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("SQLITE_DB_PATH", "winner_engine.db")


def get_db_connection():
    """
    Get SQLite database connection.
    
    Returns:
        sqlite3 connection object
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor.
    
    Yields:
        sqlite3 cursor
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def execute_query(query: str, params: Optional[tuple] = None, fetch: bool = True):
    """
    Execute a query and return results.
    Converts PostgreSQL syntax to SQLite where needed.
    
    Args:
        query: SQL query string (PostgreSQL syntax, will be adapted)
        params: Query parameters
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, else None
    """
    import re
    from datetime import date, timedelta
    
    original_params = params
    new_params = []
    param_idx = 0
    
    # Convert ILIKE to LIKE (SQLite LIKE is case-insensitive for ASCII)
    query = query.replace("ILIKE", "LIKE")
    
    # Handle ANY(%s) - convert to IN (?, ?, ...) with expanded parameters
    def replace_any(match):
        nonlocal param_idx, new_params, original_params
        if original_params and param_idx < len(original_params):
            param_value = original_params[param_idx]
            param_idx += 1
            
            if isinstance(param_value, list):
                # Expand list into multiple ? placeholders
                placeholders = ",".join(["?"] * len(param_value))
                new_params.extend(param_value)
                return f"IN ({placeholders})"
            else:
                new_params.append(param_value)
                return "= ?"
        return "IN (?)"
    
    # Replace ANY(%s) patterns
    query = re.sub(r"ANY\(%s\)", replace_any, query)
    
    # Handle date arithmetic with INTERVAL
    def replace_interval_date(match):
        nonlocal param_idx, new_params, original_params
        # Match patterns like: dt >= %s - INTERVAL '4 weeks'
        interval_str = match.group(2) if match.lastindex >= 2 else ""
        days = 0
        if "28 days" in interval_str or "4 weeks" in interval_str:
            days = 28
        elif "8 weeks" in interval_str:
            days = 56
        elif "1 week" in interval_str or "7 days" in interval_str:
            days = 7
        
        if original_params and param_idx < len(original_params):
            param_value = original_params[param_idx]
            param_idx += 1
            
            if isinstance(param_value, date):
                # Calculate new date
                new_date = param_value - timedelta(days=days)
                new_params.append(new_date.isoformat())
                return "date(?)"
            else:
                new_params.append(param_value)
                return "date(?) - ?"
        
        return "date(?)"
    
    # Replace date arithmetic patterns
    query = re.sub(r"(%s)\s*-\s*INTERVAL\s+'([^']+)'", replace_interval_date, query)
    query = re.sub(r"(%s)\s*-\s*INTERVAL\s+'([^']+)'", replace_interval_date, query)
    
    # Handle remaining INTERVAL patterns
    def replace_interval(match):
        interval_str = match.group(0)
        if "28 days" in interval_str or "4 weeks" in interval_str:
            return "28"
        elif "8 weeks" in interval_str:
            return "56"
        elif "1 week" in interval_str or "7 days" in interval_str:
            return "7"
        return "0"
    
    query = re.sub(r"INTERVAL\s+'[^']+'", replace_interval, query)
    
    # Replace PostgreSQL functions
    query = query.replace("GREATEST", "MAX")
    query = query.replace("JSONB", "TEXT")
    query = query.replace("NULLS LAST", "")  # SQLite doesn't support this, but it's optional
    
    # Convert remaining %s to ? for SQLite
    remaining_params = []
    if original_params:
        # Add any params we haven't processed yet
        for i in range(param_idx, len(original_params)):
            remaining_params.append(original_params[i])
    
    # Replace %s with ? for remaining parameters
    param_count = query.count("%s")
    if param_count > 0:
        query_parts = query.split("%s")
        if len(query_parts) == param_count + 1:
            query = "?".join(query_parts)
            new_params.extend(remaining_params)
    
    # Clean up query
    query = re.sub(r"\s+", " ", query)  # Normalize whitespace
    
    with get_db_cursor() as cur:
        if new_params or remaining_params:
            cur.execute(query, tuple(new_params) if new_params else tuple(remaining_params))
        else:
            cur.execute(query)
        
        if fetch:
            rows = cur.fetchall()
            # Convert Row objects to dicts
            return [dict(row) for row in rows]
        return None

