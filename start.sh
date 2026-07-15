#!/bin/bash

echo "🚀 Starting CCI Coin Enterprise Platform..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies if needed
if ! pip show flask > /dev/null 2>&1; then
    echo "${YELLOW}Installing Python dependencies...${NC}"
    pip install -q flask flask-cors
fi

# Start the API server
echo "${GREEN}✅ Starting CCI Coin Production API Server...${NC}"
python3 api_production.py &
API_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${GREEN}🎉 CCI Coin Enterprise Platform is LIVE!${NC}"
echo ""
echo "📍 Access the platform:"
echo "   ${BLUE}Main Dashboard:${NC}     http://localhost:5000"
echo "   ${BLUE}CCI Token:${NC}          http://localhost:5000/cci.html"
echo "   ${BLUE}Merchant:${NC}           http://localhost:5000/merchant.html"
echo "   ${BLUE}Roadmap:${NC}            http://localhost:5000/roadmap.html"
echo "   ${BLUE}Governance:${NC}         http://localhost:5000/governance.html"
echo "   ${BLUE}Security:${NC}           http://localhost:5000/security.html"
echo "   ${BLUE}Future:${NC}             http://localhost:5000/future.html"
echo ""
echo "🪙  Token: CCI Coin (CCI)"
echo "💰 Supply: 1,000,000,000 CCI"
echo "⛓️  Network: Ethereum Mainnet"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '${YELLOW}Stopping CCI Coin Platform...${NC}'; kill $API_PID 2>/dev/null; exit 0" INT

# Keep script running
wait $API_PID
