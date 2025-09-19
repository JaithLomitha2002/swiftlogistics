#!/bin/bash

# SwiftTrack Middleware Architecture - Startup Script
echo "🚀 SwiftTrack Middleware Architecture Startup"
echo "=============================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -ti:$1 >/dev/null 2>&1
}

# Check prerequisites
echo "✅ Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.8+."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 16+."
    exit 1
fi

echo "✅ All prerequisites found!"

# Start Docker services
echo "🐳 Starting Docker services (Kafka, Zookeeper, PostgreSQL)..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if Kafka is ready
echo "🔍 Checking Kafka connectivity..."
timeout=30
while [ $timeout -gt 0 ]; do
    if docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list >/dev/null 2>&1; then
        echo "✅ Kafka is ready!"
        break
    fi
    echo "⏳ Waiting for Kafka... ($timeout seconds remaining)"
    sleep 1
    timeout=$((timeout - 1))
done

if [ $timeout -eq 0 ]; then
    echo "❌ Kafka failed to start properly"
    exit 1
fi

# Create Kafka topic
echo "📝 Creating Kafka topic 'orders'..."
docker exec kafka kafka-topics --create --topic orders --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd swifttrack

# Install backend dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r backend/requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
cd database
python3 db_init.py
cd ..

# Setup frontend
echo "🌐 Setting up frontend..."
cd frontend
echo "📦 Installing Node.js dependencies..."
npm install
cd ..

# Function to start services in background
start_service() {
    local name=$1
    local command=$2
    local dir=$3
    local log_file="logs/${name}.log"
    
    mkdir -p logs
    
    echo "🚀 Starting $name..."
    if [ -n "$dir" ]; then
        cd "$dir"
    fi
    
    nohup $command > "../$log_file" 2>&1 &
    local pid=$!
    echo $pid > "../logs/${name}.pid"
    
    if [ -n "$dir" ]; then
        cd ..
    fi
    
    echo "✅ $name started (PID: $pid, Log: $log_file)"
}

# Start all services
echo ""
echo "🚀 Starting SwiftTrack services..."
echo "=================================="

# Start backend API
start_service "flask-api" "python3 app.py" "backend"

# Wait a moment for Flask to start
sleep 3

# Start Kafka consumer
start_service "kafka-consumer" "python3 kafka_consumer.py" "backend"

# Start frontend
start_service "frontend" "npm run dev" "frontend"

# Wait for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service status
echo ""
echo "🔍 Service Status:"
echo "=================="

check_service() {
    local name=$1
    local port=$2
    local pid_file="logs/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            if [ -n "$port" ] && port_in_use $port; then
                echo "✅ $name: Running (PID: $pid, Port: $port)"
            elif [ -z "$port" ]; then
                echo "✅ $name: Running (PID: $pid)"
            else
                echo "⚠️  $name: Process running but port $port not accessible"
            fi
        else
            echo "❌ $name: Process not running"
        fi
    else
        echo "❌ $name: PID file not found"
    fi
}

check_service "flask-api" 5000
check_service "kafka-consumer" ""
check_service "frontend" 3000

echo ""
echo "🌐 Application URLs:"
echo "==================="
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:5000"
echo "Health:    http://localhost:5000/health"

echo ""
echo "📊 Docker Services:"
echo "=================="
docker-compose ps

echo ""
echo "📝 Log Files:"
echo "============="
echo "Flask API:      logs/flask-api.log"
echo "Kafka Consumer: logs/kafka-consumer.log" 
echo "Frontend:       logs/frontend.log"

echo ""
echo "🛠️  Management Commands:"
echo "======================="
echo "Stop all:       ./stop.sh"
echo "View logs:      tail -f logs/<service>.log"
echo "Restart:        ./stop.sh && ./start.sh"

echo ""
echo "🎉 SwiftTrack is now running!"
echo "Visit http://localhost:3000 to start using the application"
