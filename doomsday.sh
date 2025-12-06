#!/bin/bash

# Local start script for YouTube Recommender
# Runs backend and frontend without Docker

set -e

echo "🚀 Starting YouTube Recommender locally..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

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

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null
    wait
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Install backend dependencies
echo -e "${BLUE}Installing backend dependencies...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Created virtual environment${NC}"
fi

source venv/bin/activate

# Upgrade pip and install setuptools first to handle distutils issues
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd ../web_platform
npm install
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Start backend
echo -e "${BLUE}Starting backend server on http://localhost:5000...${NC}"
cd ../backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting frontend server on http://localhost:3000...${NC}"
cd ../web_platform
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}🎉 Both services started successfully!${NC}"
echo -e "${YELLOW}Backend:  http://localhost:5000${NC}"
echo -e "${YELLOW}Frontend: http://localhost:3000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"

# Wait for services
wait