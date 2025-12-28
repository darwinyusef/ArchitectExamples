#!/bin/bash
# Complete Setup Script for AI Goals Tracker V2 + VSCode Extension
# This script sets up both backend and extension

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo "AI Goals Tracker V2 - Complete Setup"
echo -e "========================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "v2extension" ] || [ ! -d "v1extension" ]; then
    echo -e "${RED}Error: Must run from root directory (extensionvscode)${NC}"
    exit 1
fi

# ============================================================================
# Part 1: Backend Setup
# ============================================================================

echo -e "${BLUE}[1/5] Setting up Backend...${NC}"
cd v2extension

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo -e "${YELLOW}Please start Docker Desktop and try again${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"

    cat > .env << 'EOF'
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-key-here

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Redis (remote or local)
REDIS_URL=redis://64.23.150.221:6379/0

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker
EOF

    echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
    echo ""
    read -p "Press Enter after adding your OpenAI API key to .env..."
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${RED}✗ OPENAI_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}Please edit .env and add your OpenAI API key${NC}"
    exit 1
fi
echo -e "${GREEN}✓ .env configured${NC}"

# Start backend services
echo ""
echo -e "${BLUE}Starting backend services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if backend is healthy
echo "Checking backend health..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Check logs: docker-compose logs backend"
    exit 1
fi

# Test backend API
echo ""
echo -e "${BLUE}Testing backend API...${NC}"
response=$(curl -s http://localhost:8000/health)
echo "Response: $response"

if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend API is working${NC}"
else
    echo -e "${RED}✗ Backend API test failed${NC}"
    exit 1
fi

cd ..

# ============================================================================
# Part 2: Extension Setup
# ============================================================================

echo ""
echo -e "${BLUE}[2/5] Setting up VSCode Extension...${NC}"
cd v1extension

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "Install from: https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version)${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm --version)${NC}"

# Install dependencies
echo ""
echo -e "${BLUE}Installing extension dependencies...${NC}"
npm install

# Compile TypeScript
echo ""
echo -e "${BLUE}Compiling TypeScript...${NC}"
npm run compile

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Extension compiled successfully${NC}"
else
    echo -e "${RED}✗ Extension compilation failed${NC}"
    exit 1
fi

cd ..

# ============================================================================
# Part 3: Verification
# ============================================================================

echo ""
echo -e "${BLUE}[3/5] Verifying Setup...${NC}"

# Check backend services
echo ""
echo "Backend Services:"
cd v2extension
docker-compose ps

# Check PostgreSQL
if docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL might not be ready yet${NC}"
fi

# Check pgvector extension
if docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -c "SELECT extname FROM pg_extension WHERE extname = 'vector'" | grep -q "vector"; then
    echo -e "${GREEN}✓ pgvector extension installed${NC}"
else
    echo -e "${YELLOW}⚠️  pgvector extension not found${NC}"
    echo "Creating extension..."
    docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is ready (local)${NC}"
else
    echo -e "${YELLOW}⚠️  Using remote Redis${NC}"
fi

cd ..

# ============================================================================
# Part 4: Configuration
# ============================================================================

echo ""
echo -e "${BLUE}[4/5] Creating VSCode Configuration...${NC}"

# Create .vscode/settings.json for the workspace
mkdir -p .vscode

cat > .vscode/settings.json << 'EOF'
{
  "aiGoalsTracker.backendApiUrl": "http://localhost:8000",
  "aiGoalsTracker.backendWsUrl": "ws://localhost:8000/api/v1/ws",
  "aiGoalsTracker.enableBackend": true,
  "aiGoalsTracker.enableWebSocket": true,
  "aiGoalsTracker.syncInterval": 30,
  "aiGoalsTracker.userId": ""
}
EOF

echo -e "${GREEN}✓ VSCode settings created${NC}"

# ============================================================================
# Part 5: Summary
# ============================================================================

echo ""
echo -e "${BLUE}[5/5] Setup Complete!${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup Successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo "📋 Summary:"
echo ""
echo "Backend Services (v2extension):"
echo "  • API:      http://localhost:8000"
echo "  • Docs:     http://localhost:8000/docs"
echo "  • RabbitMQ: http://localhost:15672 (guest/guest)"
echo "  • MinIO:    http://localhost:9001 (minioadmin/minioadmin)"
echo ""

echo "VSCode Extension (v1extension):"
echo "  • Compiled: ✓"
echo "  • Config:   .vscode/settings.json"
echo ""

echo "🚀 Next Steps:"
echo ""
echo "1. Test the backend:"
echo "   curl http://localhost:8000/health"
echo ""

echo "2. Create a test goal:"
echo "   curl -X POST http://localhost:8000/api/v1/goals \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"title\":\"Test Goal\",\"description\":\"Testing\",\"user_id\":\"test-user\"}'"
echo ""

echo "3. Run the VSCode extension:"
echo "   cd v1extension"
echo "   code ."
echo "   # Press F5 to start debugging"
echo ""

echo "4. In the new VSCode window:"
echo "   • Open the 'AI Goals Tracker' view in Activity Bar"
echo "   • You should see: '✅ Connected to backend'"
echo "   • Try adding a goal!"
echo ""

echo "📖 Documentation:"
echo "  • Backend:     v2extension/README.md"
echo "  • Rate Limits: v2extension/backend/RATE_LIMITING.md"
echo "  • Integration: v1extension/INTEGRATION_GUIDE.md"
echo "  • Docker:      v2extension/DOCKER_SETUP.md"
echo ""

echo "🛠️  Useful Commands:"
echo "  • View logs:      cd v2extension && docker-compose logs -f"
echo "  • Stop backend:   cd v2extension && docker-compose down"
echo "  • Restart:        cd v2extension && docker-compose restart backend"
echo ""

echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "  • Make sure your OPENAI_API_KEY is set in v2extension/.env"
echo "  • The extension needs VSCode 1.75+ to run"
echo "  • First time running may take a few minutes"
echo ""

echo -e "${GREEN}Happy coding! 🎉${NC}"
