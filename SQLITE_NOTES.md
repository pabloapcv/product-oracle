# SQLite Compatibility Notes

## Status

SQLite support is **partially implemented** for development/demo purposes. Some complex PostgreSQL queries (especially those using `ANY(%s)` and `ILIKE ANY(%s)`) require additional conversion work.

## Recommendation

**For production use, PostgreSQL is strongly recommended.** The system is designed for PostgreSQL and all features work correctly with it.

## Current SQLite Support

✅ **Working:**
- Basic CRUD operations
- Simple SELECT queries
- Entity management
- Seed data insertion

⚠️ **Needs Work:**
- Complex queries with `ANY(%s)` arrays
- `ILIKE ANY(%s)` pattern matching
- Date arithmetic with INTERVAL
- Some feature computation queries

## Quick Fix for Demo

For demonstration purposes, you can:
1. Use the `demo.py` script (no database required)
2. Use `demo_features.py` for feature walkthrough
3. Set up PostgreSQL for full functionality

## PostgreSQL Setup

See `SETUP.md` for PostgreSQL installation and setup instructions.

