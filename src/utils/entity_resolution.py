"""
Entity resolution utilities for mapping aliases to canonical entities.
"""
import logging
import uuid
from typing import Optional, List, Dict
from src.utils.db import execute_query, get_db_cursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_entity(
    canonical_name: str,
    entity_type: str = "concept",
    category_primary: Optional[str] = None
) -> str:
    """
    Create a new entity and return its ID.
    
    Args:
        canonical_name: Canonical name for the entity
        entity_type: Type ('concept', 'keyword_cluster', 'brand', 'store')
        category_primary: Primary category
        
    Returns:
        Entity ID (UUID string)
    """
    entity_id = str(uuid.uuid4())
    
    query = """
        INSERT INTO entities (entity_id, entity_type, canonical_name, category_primary)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (entity_id) DO NOTHING
        RETURNING entity_id
    """
    
    result = execute_query(query, (entity_id, entity_type, canonical_name, category_primary))
    
    if result:
        logger.info(f"Created entity: {canonical_name} ({entity_id})")
        return result[0]['entity_id']
    else:
        # Entity already exists, find it
        query = "SELECT entity_id FROM entities WHERE canonical_name = %s AND entity_type = %s"
        result = execute_query(query, (canonical_name, entity_type))
        if result:
            return result[0]['entity_id']
        return entity_id


def find_entity_by_alias(alias_text: str, source: str) -> Optional[str]:
    """
    Find entity ID by alias text and source.
    
    Args:
        alias_text: Alias text to search for
        source: Source ('amazon', 'tiktok', 'shopify', 'manual')
        
    Returns:
        Entity ID if found, else None
    """
    query = """
        SELECT entity_id, confidence
        FROM entity_aliases
        WHERE source = %s AND alias_text = %s
        ORDER BY confidence DESC
        LIMIT 1
    """
    
    result = execute_query(query, (source, alias_text))
    if result:
        return result[0]['entity_id']
    return None


def create_entity_alias(
    entity_id: str,
    alias_text: str,
    source: str,
    confidence: float = 1.0
) -> None:
    """
    Create a new entity alias mapping.
    
    Args:
        entity_id: Entity UUID
        alias_text: Alias text
        source: Source
        confidence: Confidence score (0-1)
    """
    query = """
        INSERT INTO entity_aliases (entity_id, source, alias_text, confidence)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (source, alias_text) 
        DO UPDATE SET confidence = GREATEST(entity_aliases.confidence, EXCLUDED.confidence)
    """
    
    execute_query(query, (entity_id, source, alias_text, confidence), fetch=False)
    logger.debug(f"Created alias: {alias_text} -> {entity_id} ({source})")


def get_or_create_entity_for_alias(
    alias_text: str,
    source: str,
    entity_type: str = "concept",
    category_primary: Optional[str] = None,
    confidence: float = 0.8
) -> str:
    """
    Get existing entity or create new one for an alias.
    
    Args:
        alias_text: Alias text
        source: Source
        entity_type: Entity type if creating new
        category_primary: Category if creating new
        confidence: Confidence for alias mapping
        
    Returns:
        Entity ID
    """
    # Try to find existing entity
    entity_id = find_entity_by_alias(alias_text, source)
    
    if entity_id:
        return entity_id
    
    # Create new entity with alias text as canonical name
    entity_id = create_entity(alias_text, entity_type, category_primary)
    create_entity_alias(entity_id, alias_text, source, confidence)
    
    return entity_id


def get_entity_by_id(entity_id: str) -> Optional[Dict]:
    """
    Get entity details by ID.
    
    Args:
        entity_id: Entity UUID
        
    Returns:
        Entity dictionary or None
    """
    query = "SELECT * FROM entities WHERE entity_id = %s"
    result = execute_query(query, (entity_id,))
    if result:
        return dict(result[0])
    return None


def list_entities(entity_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    List entities, optionally filtered by type.
    
    Args:
        entity_type: Optional entity type filter
        limit: Maximum number of results
        
    Returns:
        List of entity dictionaries
    """
    if entity_type:
        query = "SELECT * FROM entities WHERE entity_type = %s ORDER BY created_at DESC LIMIT %s"
        return [dict(row) for row in execute_query(query, (entity_type, limit))]
    else:
        query = "SELECT * FROM entities ORDER BY created_at DESC LIMIT %s"
        return [dict(row) for row in execute_query(query, (limit,))]

