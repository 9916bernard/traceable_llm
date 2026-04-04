#!/bin/bash
# Startup script for Traceable LLM Verification System
# Starts both backend (Flask) and frontend (Next.js)

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Traceable LLM Verification System ===${NC}"
echo ""

# --- Check root .env exists ---
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}[!] No .env found at project root. Create one with your API keys.${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Using root .env (backend loads it automatically)${NC}"

# --- Generate frontend .env.local from root .env ---
# Next.js only reads NEXT_PUBLIC_* vars from its own .env.local
grep '^NEXT_PUBLIC_' "$PROJECT_DIR/.env" > "$PROJECT_DIR/frontend/.env.local" 2>/dev/null
echo -e "${GREEN}[+] Generated frontend/.env.local from root .env${NC}"

# --- Install backend dependencies ---
echo ""
echo -e "${GREEN}[1/3] Installing backend dependencies...${NC}"
cd "$PROJECT_DIR/backend"
if [ ! -d ".venv" ]; then
    echo "    Creating Python virtual environment..."
    uv venv
fi
uv pip install -r requirements.txt

# --- Install frontend dependencies ---
echo ""
echo -e "${GREEN}[2/3] Installing frontend dependencies...${NC}"
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "    node_modules already exists, skipping."
fi

# --- Start services ---
echo ""
echo -e "${GREEN}[3/3] Starting services...${NC}"
echo ""

# Cleanup function to kill background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

# Start backend
cd "$PROJECT_DIR/backend"
echo -e "${GREEN}  Backend  -> http://localhost:5001${NC}"
uv run python app.py --port 5001 &
BACKEND_PID=$!

# Start frontend
cd "$PROJECT_DIR/frontend"
echo -e "${GREEN}  Frontend -> http://localhost:3000${NC}"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}Both services are running. Press Ctrl+C to stop.${NC}"
echo ""

# Wait for either process to exit
wait
