#!/usr/bin/env python3
"""Create entity aliases to link seed data to entities."""
import os
os.environ["USE_SQLITE"] = "true"

from src.utils.db import execute_query
from src.utils.entity_resolution import create_entity_alias, get_entity_by_id

# Map seed data to entities
mappings = [
    ("portable mini blender", "B08XYZ1234", "amazon"),
    ("portable mini blender", "portable blender", "tiktok"),
    ("phone stand desk mount", "B09ABC5678", "amazon"),
    ("phone stand desk mount", "phone stand", "tiktok"),
    ("yoga mat bag", "B07DEF9012", "amazon"),
    ("yoga mat bag", "yoga mat bag", "tiktok"),
    ("car phone mount", "B06GHI3456", "amazon"),
    ("car phone mount", "car phone mount", "tiktok"),
    ("wireless earbuds", "B05JKL7890", "amazon"),
    ("wireless earbuds", "wireless earbuds", "tiktok"),
    ("silicone baking mats", "B04MNO1234", "amazon"),
    ("silicone baking mats", "silicone baking mats", "tiktok"),
    ("resistance bands set", "B03PQR5678", "amazon"),
    ("resistance bands set", "resistance bands", "tiktok"),
    ("laptop stand", "B02STU9012", "amazon"),
    ("laptop stand", "laptop stand", "tiktok"),
]

print("Creating entity aliases...")
for entity_name, alias_text, source in mappings:
    # Find entity by name
    entities = execute_query(
        "SELECT entity_id FROM entities WHERE canonical_name = ?",
        (entity_name,)
    )
    if entities:
        entity_id = entities[0]['entity_id']
        create_entity_alias(entity_id, alias_text, source, 1.0)
        print(f"  ✓ {entity_name} -> {alias_text} ({source})")
    else:
        print(f"  ✗ Entity not found: {entity_name}")

print("\n✅ Alias creation complete!")

