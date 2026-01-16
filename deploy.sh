#!/bin/bash
# Winner Engine Deployment Script

set -e

echo "=========================================="
echo "Winner Engine - Deployment"
echo "=========================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Please install Docker Compose"
    exit 1
fi

echo "✅ Docker found"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
    echo "   nano .env"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "Configuration:"
echo "  Database: ${DB_NAME:-winner_engine}"
echo "  User: ${DB_USER:-winner_user}"
echo "  Host: ${DB_HOST:-localhost}"
echo ""

# Build and start services
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d postgres

echo ""
echo "Waiting for database to be ready..."
sleep 5

# Run migrations
echo ""
echo "Running database migrations..."
docker-compose exec -T postgres psql -U ${DB_USER:-winner_user} -d ${DB_NAME:-winner_engine} -f /docker-entrypoint-initdb.d/001_init.sql || {
    echo "⚠️  Migration may have already run, continuing..."
}

echo ""
echo "Starting pipeline service..."
docker-compose up -d

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Services running:"
docker-compose ps
echo ""
echo "View logs:"
echo "  docker-compose logs -f pipeline"
echo ""
echo "Run pipeline manually:"
echo "  docker-compose run --rm pipeline python -m src.pipeline --week_start 2026-01-12"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "View reports:"
echo "  ls -lh reports/"
echo ""

