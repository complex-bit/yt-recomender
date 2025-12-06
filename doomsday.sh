#!/bin/bash

# Doomsday script for WhyExplore YouTube Recommender
# Starts all services: backend, frontend, and auth service

set -e

echo "🎬 Starting WhyExplore - The Complete YouTube Discovery Experience..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i ":$1" > /dev/null 2>&1
}

# Function to check if service is healthy
check_service_health() {
    local url=$1
    local name=$2
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is already running and healthy${NC}"
        return 0
    else
        return 1
    fi
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites and running services...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"

# Check if services are already running
BACKEND_RUNNING=false
AUTH_RUNNING=false
FRONTEND_RUNNING=false

if check_service_health "http://localhost:5000/health" "Backend"; then
    BACKEND_RUNNING=true
fi

if check_service_health "http://localhost:5001" "Auth Service"; then
    AUTH_RUNNING=true
fi

if check_service_health "http://localhost:3000" "Frontend"; then
    FRONTEND_RUNNING=true
fi

if [ "$BACKEND_RUNNING" = true ] && [ "$AUTH_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo -e "${GREEN}🎉 All WhyExplore services are already running!${NC}"
    echo -e "${CYAN}🌐 Frontend: http://localhost:3000${NC}"
    echo -e "${BLUE}🔧 Backend:  http://localhost:5000${NC}"
    echo -e "${PURPLE}🔐 Auth:     http://localhost:5001${NC}"
    echo -e "${YELLOW}✨ Ready to explore! Press Ctrl+C to stop monitoring.${NC}"

    # Just monitor the services
    while true; do
        sleep 5
        if ! port_in_use 3000 || ! port_in_use 5000 || ! port_in_use 5001; then
            echo -e "${YELLOW}⚠️  One or more services stopped. Exiting monitor.${NC}"
            break
        fi
    done
    exit 0
fi

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down all WhyExplore services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null
    wait
    echo -e "${GREEN}✅ All services stopped. Thanks for using WhyExplore! 🎬${NC}"
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Only setup services that aren't running
if [ "$BACKEND_RUNNING" = false ]; then
    echo -e "${BLUE}📦 Setting up backend dependencies...${NC}"
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✅ Created backend virtual environment${NC}"
        INSTALL_BACKEND=true
    elif [ ! -f "venv/pyvenv.cfg" ] || [ requirements.txt -nt "venv/pyvenv.cfg" ]; then
        echo -e "${YELLOW}📦 Backend dependencies need updating...${NC}"
        INSTALL_BACKEND=true
    else
        echo -e "${GREEN}✅ Backend dependencies up to date${NC}"
        INSTALL_BACKEND=false
    fi

    if [ "$INSTALL_BACKEND" = true ]; then
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Backend dependencies installed${NC}"
    fi
    cd ..
fi

if [ "$AUTH_RUNNING" = false ]; then
    echo -e "${PURPLE}🔐 Setting up auth service dependencies...${NC}"
    cd auth
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✅ Created auth virtual environment${NC}"
        INSTALL_AUTH=true
    else
        echo -e "${GREEN}✅ Auth virtual environment exists${NC}"
        INSTALL_AUTH=false
    fi

    if [ "$INSTALL_AUTH" = true ]; then
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        # Install auth dependencies
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            pip install flask google-auth-oauthlib google-api-python-client python-dotenv google-cloud-secret-manager
        fi
        echo -e "${GREEN}✅ Auth service dependencies installed${NC}"
    fi
    cd ..
fi

if [ "$FRONTEND_RUNNING" = false ]; then
    echo -e "${CYAN}🎨 Setting up frontend dependencies...${NC}"
    cd web_platform
    if [ ! -d "node_modules" ] || [ package.json -nt "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing/updating frontend dependencies...${NC}"
        npm install
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ Frontend dependencies up to date${NC}"
    fi
    cd ..
fi

# Start services that aren't running
echo -e "\n${YELLOW}🚀 Starting needed WhyExplore services...${NC}"

# Start backend if not running
if [ "$BACKEND_RUNNING" = false ]; then
    echo -e "${BLUE}Starting backend server on http://localhost:5000...${NC}"
    cd backend
    source venv/bin/activate
    python app.py &
    BACKEND_PID=$!
    cd ..
    sleep 2
else
    echo -e "${BLUE}⏭️  Backend already running, skipping...${NC}"
fi

# Start auth service if not running
if [ "$AUTH_RUNNING" = false ]; then
    echo -e "${PURPLE}Starting auth service on http://localhost:5001...${NC}"
    cd auth
    source venv/bin/activate
    python app.py &
    AUTH_PID=$!
    cd ..
    sleep 2
else
    echo -e "${PURPLE}⏭️  Auth service already running, skipping...${NC}"
fi

# Start frontend if not running
if [ "$FRONTEND_RUNNING" = false ]; then
    echo -e "${CYAN}Starting frontend on http://localhost:3000...${NC}"
    cd web_platform
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    sleep 3
else
    echo -e "${CYAN}⏭️  Frontend already running, skipping...${NC}"
fi

echo -e "\n${GREEN}🎉 WhyExplore is now running! 🎬${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${CYAN}🌐 Frontend (Main App): http://localhost:3000${NC}"
echo -e "${BLUE}🔧 Backend API:        http://localhost:5000${NC}"
echo -e "${PURPLE}🔐 Auth Service:       http://localhost:5001${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}✨ Open http://localhost:3000 to start exploring!${NC}"
echo -e "${YELLOW}🛑 Press Ctrl+C to stop all services${NC}"

# Wait for services
wait