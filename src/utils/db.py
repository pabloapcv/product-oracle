"""
Database connection and helper utilities.
"""
import os
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from psycopg2.pool import ThreadedConnectionPool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool (initialized on first use)
_connection_pool = None


def get_db_connection():
    """
    Get database connection from environment variables.
    
    Returns:
        psycopg2 connection object
    """
    global _connection_pool
    
    if _connection_pool is None:
        try:
            _connection_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "winner_engine"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
            )
        except Exception as e:
            logger.warning(f"Connection pool failed, using direct connection: {e}")
            return psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "winner_engine"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
            )
    
    try:
        return _connection_pool.getconn()
    except Exception:
        # Fallback to direct connection
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "winner_engine"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )


@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor.
    
    Yields:
        psycopg2 cursor with RealDictCursor
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if hasattr(conn, 'pool') and conn.pool:
            _connection_pool.putconn(conn)
        else:
            conn.close()


def execute_query(query: str, params: Optional[tuple] = None, fetch: bool = True):
    """
    Execute a query and return results.
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, else None
    """
    with get_db_cursor() as cur:
        cur.execute(query, params)
        if fetch:
            return cur.fetchall()
        return None


def execute_many(query: str, params_list: List[tuple], fetch: bool = False):
    """
    Execute a query with many parameter sets.
    
    Args:
        query: SQL query string
        params_list: List of parameter tuples
        fetch: Whether to fetch results
        
    Returns:
        Query results if fetch=True, else None
    """
    with get_db_cursor() as cur:
        execute_values(cur, query, params_list)
        if fetch:
            return cur.fetchall()
        return None


def insert_jsonb(table: str, data: Dict[str, Any], conflict_cols: Optional[List[str]] = None):
    """
    Insert or update a row with JSONB data.
    
    Args:
        table: Table name
        data: Dictionary of column: value
        conflict_cols: Columns for ON CONFLICT (for upsert)
    """
    columns = list(data.keys())
    placeholders = ["%s"] * len(columns)
    values = [data[col] for col in columns]
    
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    
    if conflict_cols:
        update_cols = [f"{col} = EXCLUDED.{col}" for col in columns if col not in conflict_cols]
        query += f" ON CONFLICT ({', '.join(conflict_cols)}) DO UPDATE SET {', '.join(update_cols)}"
    
    execute_query(query, tuple(values), fetch=False)

