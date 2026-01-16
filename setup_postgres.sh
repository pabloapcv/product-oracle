#!/bin/bash
# PostgreSQL Setup Script for Winner Engine

set -e

echo "=========================================="
echo "Winner Engine - PostgreSQL Setup"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    echo ""
    echo "To install PostgreSQL on macOS:"
    echo "  brew install postgresql@14"
    echo "  brew services start postgresql@14"
    echo ""
    echo "Then run this script again."
    exit 0
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux"
    echo ""
    echo "Installing PostgreSQL..."
    
    # Update package list
    sudo apt-get update
    
    # Install PostgreSQL
    sudo apt-get install -y postgresql postgresql-contrib
    
    # Start PostgreSQL
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    echo "PostgreSQL installed and started"
else
    echo "Unsupported OS. Please install PostgreSQL manually."
    exit 1
fi

# Create database and user
echo ""
echo "Creating database and user..."

sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE winner_engine;

-- Create user
CREATE USER winner_user WITH PASSWORD 'winner_password_change_me';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE winner_engine TO winner_user;

-- Connect to database and grant schema privileges
\c winner_engine
GRANT ALL ON SCHEMA public TO winner_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO winner_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO winner_user;

\q
EOF

echo "Database created successfully!"
echo ""
echo "Running migrations..."

# Run migrations
psql -h localhost -U winner_user -d winner_engine -f sql/001_init.sql

echo ""
echo "=========================================="
echo "✅ PostgreSQL setup complete!"
echo "=========================================="
echo ""
echo "Set these environment variables:"
echo "  export DB_HOST=localhost"
echo "  export DB_NAME=winner_engine"
echo "  export DB_USER=winner_user"
echo "  export DB_PASSWORD=winner_password_change_me"
echo ""
echo "⚠️  IMPORTANT: Change the password in production!"

