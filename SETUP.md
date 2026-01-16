# Database Setup Guide

## Option 1: PostgreSQL (Recommended for Production)

### Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### Create Database

```bash
# Create database
createdb winner_engine

# Or using psql
psql postgres
CREATE DATABASE winner_engine;
\q
```

### Run Migrations

```bash
psql winner_engine -f sql/001_init.sql
```

### Set Environment Variables

```bash
export DB_HOST=localhost
export DB_NAME=winner_engine
export DB_USER=postgres
export DB_PASSWORD=your_password
```

Or create a `.env` file:
```
DB_HOST=localhost
DB_NAME=winner_engine
DB_USER=postgres
DB_PASSWORD=your_password
```

## Option 2: SQLite (For Development/Demo)

For quick testing without PostgreSQL, we can use SQLite. See `setup_sqlite.py` for a SQLite adapter.

## Option 3: Docker (Easiest)

```bash
# Run PostgreSQL in Docker
docker run --name winner-engine-db \
  -e POSTGRES_PASSWORD=winner123 \
  -e POSTGRES_DB=winner_engine \
  -p 5432:5432 \
  -d postgres:14

# Set environment
export DB_HOST=localhost
export DB_NAME=winner_engine
export DB_USER=postgres
export DB_PASSWORD=winner123

# Run migrations
psql -h localhost -U postgres -d winner_engine -f sql/001_init.sql
```

## Verify Setup

```bash
python3 -c "
from src.utils.db import get_db_connection
conn = get_db_connection()
print('✅ Database connection successful!')
conn.close()
"
```

