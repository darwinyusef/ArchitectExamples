#!/bin/bash
# Quick Start Script - Validates and starts AI Goals Tracker V2

set -e  # Exit on error

echo "=========================================="
echo "AI Goals Tracker V2 - Quick Start"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}✗ Python 3.11+ required. Current: $PYTHON_VERSION${NC}"
    echo -e "${YELLOW}  → Use Docker instead: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if .env exists
echo ""
echo "2. Checking .env file..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠  .env file not found${NC}"
    if [ -f .env.example ]; then
        echo "   Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW}   → Please edit .env and add your OPENAI_API_KEY${NC}"
        exit 1
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ .env file exists${NC}"

# Check OPENAI_API_KEY
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${RED}✗ OPENAI_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}  → Please add your OpenAI API key to .env${NC}"
    exit 1
fi
echo -e "${GREEN}✓ OPENAI_API_KEY configured${NC}"

# Check Poetry
echo ""
echo "3. Checking Poetry..."
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}✗ Poetry not installed${NC}"
    echo -e "${YELLOW}  → Install: curl -sSL https://install.python-poetry.org | python3 -${NC}"
    echo -e "${YELLOW}  → Or use Docker: docker-compose up -d${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Poetry installed${NC}"

# Install dependencies
echo ""
echo "4. Installing dependencies..."
poetry install --no-interaction
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Validate imports
echo ""
echo "5. Validating imports..."
poetry run python scripts/validate_imports.py
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Import validation failed${NC}"
    exit 1
fi

# Check PostgreSQL
echo ""
echo "6. Checking PostgreSQL connection..."
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo -e "${YELLOW}⚠  PostgreSQL not running on localhost:5432${NC}"
    echo -e "${YELLOW}  → Start with: docker-compose up -d postgres${NC}"
    echo ""
    read -p "Start PostgreSQL now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ..
        docker-compose up -d postgres
        echo "Waiting for PostgreSQL to be ready..."
        sleep 5
        cd backend
    else
        exit 1
    fi
fi
echo -e "${GREEN}✓ PostgreSQL is running${NC}"

# Check Redis
echo ""
echo "7. Checking Redis connection..."
REDIS_URL=$(grep REDIS_URL .env | cut -d'=' -f2)
echo "   Redis URL: $REDIS_URL"
if [[ $REDIS_URL == *"localhost"* ]] || [[ $REDIS_URL == *"127.0.0.1"* ]]; then
    if ! redis-cli ping &> /dev/null; then
        echo -e "${YELLOW}⚠  Redis not running on localhost${NC}"
        echo -e "${YELLOW}  → Start with: docker-compose up -d redis${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Redis is accessible${NC}"

# Run migrations
echo ""
echo "8. Running database migrations..."
poetry run alembic upgrade head
echo -e "${GREEN}✓ Migrations complete${NC}"

# All checks passed
echo ""
echo "=========================================="
echo -e "${GREEN}✅ All checks passed!${NC}"
echo "=========================================="
echo ""
echo "Starting server..."
echo "  → API: http://localhost:8000"
echo "  → Docs: http://localhost:8000/docs"
echo "  → Admin: http://localhost:8000/api/v1/admin/rate-limits/config"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
