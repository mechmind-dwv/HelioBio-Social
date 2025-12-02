#!/bin/bash

# HelioBio-Social Quickstart Script
# Automated setup for the complete project

set -e  # Exit on error

echo "=================================="
echo "🌞 HelioBio-Social Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo -e "${RED}✗ Python 3.9+ required but not installed${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}✗ Node.js 16+ required but not installed${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${YELLOW}⚠ Docker not found - will use local setup${NC}"; DOCKER_AVAILABLE=false; }

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo -e "${GREEN}✓ Node.js v$(node --version)${NC}"

# Create directory structure
echo ""
echo "Creating project structure..."
mkdir -p backend/api/v1
mkdir -p backend/connectors/solar
mkdir -p backend/connectors/health
mkdir -p backend/analytics
mkdir -p backend/ml
mkdir -p backend/database/models
mkdir -p backend/tests
mkdir -p frontend/src/pages
mkdir -p frontend/src/components
mkdir -p frontend/src/services
mkdir -p frontend/public
mkdir -p analysis/notebooks
mkdir -p analysis/scripts
mkdir -p data/raw
mkdir -p data/processed
mkdir -p docs
mkdir -p deployment
mkdir -p .github/workflows

echo -e "${GREEN}✓ Directory structure created${NC}"

# Setup environment file
echo ""
echo "Creating environment configuration..."
if [ ! -f .env ]; then
    cat > .env << EOF
# HelioBio-Social Environment Configuration

# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql+asyncpg://heliobio:heliobio@localhost:5432/heliobio

# Redis
REDIS_URL=redis://localhost:6379/0

# External APIs
NOAA_API_KEY=
NASA_API_KEY=DEMO_KEY
WHO_API_URL=https://ghoapi.azureedge.net/api

# API Keys (add your own)
GOOGLE_TRENDS_API_KEY=

# Analysis
CORRELATION_MIN_OBSERVATIONS=30
ALPHA_LEVEL=0.05
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your API keys${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping${NC}"
fi

# Backend setup
echo ""
echo "Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

source venv/bin/activate || source venv/Scripts/activate 2>/dev/null

echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Initialize database (if PostgreSQL is running)
if command -v psql >/dev/null 2>&1; then
    echo "Initializing database..."
    python setup_db.py 2>/dev/null || echo -e "${YELLOW}⚠ Database setup skipped (may need manual setup)${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not found - database setup skipped${NC}"
fi

cd ..

# Frontend setup
echo ""
echo "Setting up React frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ node_modules exists, skipping npm install${NC}"
fi

cd ..

# Analysis setup
echo ""
echo "Setting up Jupyter analysis environment..."
cd analysis

if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
jupyter
jupyterlab
numpy
pandas
scipy
matplotlib
seaborn
statsmodels
scikit-learn
EOF
fi

pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Analysis environment ready${NC}"

cd ..

# Create start scripts
echo ""
echo "Creating start scripts..."

# Backend start script
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate || source venv/Scripts/activate
uvicorn main:app --reload --port 8000
EOF
chmod +x start_backend.sh

# Frontend start script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm start
EOF
chmod +x start_frontend.sh

# Jupyter start script
cat > start_jupyter.sh << 'EOF'
#!/bin/bash
cd analysis
source ../backend/venv/bin/activate || source ../backend/venv/Scripts/activate
jupyter lab --no-browser
EOF
chmod +x start_jupyter.sh

# All-in-one start script
cat > start_all.sh << 'EOF'
#!/bin/bash
echo "Starting HelioBio-Social..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Jupyter: http://localhost:8888"
echo ""

# Start backend in background
./start_backend.sh &
BACKEND_PID=$!

# Start frontend in background
./start_frontend.sh &
FRONTEND_PID=$!

# Start Jupyter in foreground
./start_jupyter.sh

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
EOF
chmod +x start_all.sh

echo -e "${GREEN}✓ Start scripts created${NC}"

# Docker setup
if [ "$DOCKER_AVAILABLE" != "false" ]; then
    echo ""
    echo "Docker is available. You can also use:"
    echo "  docker-compose up -d"
fi

# Summary
echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Quick Start Options:"
echo ""
echo "1. Start everything with Docker:"
echo "   docker-compose up -d"
echo ""
echo "2. Start manually:"
echo "   ./start_backend.sh   # Terminal 1 - API on :8000"
echo "   ./start_frontend.sh  # Terminal 2 - UI on :3000"
echo "   ./start_jupyter.sh   # Terminal 3 - Jupyter on :8888"
echo ""
echo "3. Start all together:"
echo "   ./start_all.sh"
echo ""
echo "Access points:"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Dashboard: http://localhost:3000"
echo "  • Jupyter Lab: http://localhost:8888"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Start the services"
echo "  3. Open http://localhost:3000"
echo ""
echo "Documentation: ./docs/README.md"
echo "GitHub: https://github.com/your-username/HelioBio-Social"
echo ""
echo "🌞 Happy researching! 🌍"
echo "=================================="
