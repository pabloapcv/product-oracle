"""
Query helper utilities for SQLite/PostgreSQL compatibility.
"""
import os

USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

def get_param_placeholder():
    """Get parameter placeholder for current database."""
    return "?" if USE_SQLITE else "%s"

def convert_any_clause(field: str, values: list) -> tuple:
    """
    Convert PostgreSQL ANY(%s) to SQLite IN (?, ?, ...).
    
    Returns:
        (sql_clause, params_tuple)
    """
    if USE_SQLITE:
        placeholders = ",".join(["?"] * len(values))
        return f"{field} IN ({placeholders})", tuple(values)
    else:
        return f"{field} = ANY(%s)", (values,)

def convert_like_any(field: str, patterns: list) -> tuple:
    """
    Convert PostgreSQL ILIKE ANY(%s) to SQLite LIKE OR LIKE.
    
    Returns:
        (sql_clause, params_tuple)
    """
    if USE_SQLITE:
        conditions = " OR ".join([f"{field} LIKE ?" for _ in patterns])
        return f"({conditions})", tuple(patterns)
    else:
        return f"{field} ILIKE ANY(%s)", (patterns,)

def convert_date_interval(date_param, interval_str: str) -> tuple:
    """
    Convert PostgreSQL date - INTERVAL to SQLite date arithmetic.
    
    Returns:
        (sql_clause, date_value)
    """
    from datetime import timedelta, date
    
    # Parse interval
    days = 0
    if "28 days" in interval_str or "4 weeks" in interval_str:
        days = 28
    elif "8 weeks" in interval_str:
        days = 56
    elif "1 week" in interval_str or "7 days" in interval_str:
        days = 7
    
    if USE_SQLITE:
        if isinstance(date_param, date):
            new_date = date_param - timedelta(days=days)
            return "date(?)", new_date.isoformat()
        else:
            return "date(?) - ?", (date_param, days)
    else:
        return f"{get_param_placeholder()} - INTERVAL '{interval_str}'", date_param

