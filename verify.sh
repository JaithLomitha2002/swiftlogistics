#!/bin/bash

# SwiftTrack Setup Verification Script
echo "🔍 SwiftTrack Middleware Architecture - Setup Verification"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local service_name=$1
    local url=$2
    local expected_text=$3
    
    echo -n "Checking $service_name... "
    
    if curl -s "$url" | grep -q "$expected_text"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Function to check port
check_port() {
    local port=$1
    local service=$2
    
    echo -n "Checking port $port ($service)... "
    
    if netstat -tulpn 2>/dev/null | grep -q ":$port " || lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${GREEN}✅ OPEN${NC}"
        return 0
    else
        echo -e "${RED}❌ CLOSED${NC}"
        return 1
    fi
}

# Check if Docker services are running
echo "🐳 Checking Docker Services:"
echo "=============================="

if docker ps | grep -q "kafka"; then
    echo -e "Kafka: ${GREEN}✅ Running${NC}"
else
    echo -e "Kafka: ${RED}❌ Not running${NC}"
fi

if docker ps | grep -q "postgres"; then
    echo -e "PostgreSQL: ${GREEN}✅ Running${NC}"
else
    echo -e "PostgreSQL: ${RED}❌ Not running${NC}"
fi

if docker ps | grep -q "zookeeper"; then
    echo -e "Zookeeper: ${GREEN}✅ Running${NC}"
else
    echo -e "Zookeeper: ${RED}❌ Not running${NC}"
fi

echo ""

# Check ports
echo "🔌 Checking Ports:"
echo "=================="
check_port 5000 "Flask API"
check_port 3000 "Frontend"
check_port 9092 "Kafka"
check_port 5432 "PostgreSQL"

echo ""

# Check HTTP endpoints
echo "🌐 Checking HTTP Endpoints:"
echo "============================"
check_service "Backend Health" "http://localhost:5000/health" "healthy"
check_service "Backend API" "http://localhost:5000/api/health" "running"

echo ""

# Test Kafka connectivity
echo "📡 Testing Kafka:"
echo "================="
if docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | grep -q "orders"; then
    echo -e "Kafka topics: ${GREEN}✅ 'orders' topic exists${NC}"
else
    echo -e "Kafka topics: ${YELLOW}⚠️  'orders' topic not found${NC}"
fi

echo ""

# Test database connectivity
echo "🗄️ Testing Database:"
echo "===================="
if docker exec postgres psql -U postgres -d swifttrack -c "SELECT 1;" >/dev/null 2>&1; then
    echo -e "Database connection: ${GREEN}✅ OK${NC}"
else
    echo -e "Database connection: ${RED}❌ FAILED${NC}"
fi

echo ""

# Test order submission
echo "🧪 Testing Order Submission:"
echo "============================"
response=$(curl -s -X POST "http://localhost:5000/api/orders" \
    -H "Content-Type: application/json" \
    -d '{"client":"Test Client","description":"Test Order","amount":100}' 2>/dev/null)

if echo "$response" | grep -q "order_id"; then
    echo -e "Order submission: ${GREEN}✅ OK${NC}"
    order_id=$(echo "$response" | grep -o '"order_id":"[^"]*"' | cut -d'"' -f4)
    echo "Test order ID: $order_id"
else
    echo -e "Order submission: ${RED}❌ FAILED${NC}"
    echo "Response: $response"
fi

echo ""

# Summary
echo "📋 Summary:"
echo "==========="
echo "If all checks show ✅, your SwiftTrack middleware system is working correctly!"
echo ""
echo "🚀 Quick Start:"
echo "- Visit: http://localhost:3000"
echo "- Submit a test order"
echo "- Check real-time tracking"
echo ""
echo "📊 Monitoring:"
echo "- Backend logs: tail -f swifttrack/logs/flask-api.log"
echo "- Consumer logs: tail -f swifttrack/logs/kafka-consumer.log"
echo "- Frontend logs: tail -f swifttrack/logs/frontend.log"
