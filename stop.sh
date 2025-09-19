#!/bin/bash

# SwiftTrack Stop Script
echo "🛑 Stopping SwiftTrack services..."

# Function to stop a service
stop_service() {
    local name=$1
    local pid_file="swifttrack/logs/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $name (PID: $pid)..."
            kill "$pid"
            
            # Wait for graceful shutdown
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚡ Force killing $name..."
                kill -9 "$pid"
            fi
            
            rm -f "$pid_file"
            echo "✅ $name stopped"
        else
            echo "⚠️  $name was not running"
            rm -f "$pid_file"
        fi
    else
        echo "⚠️  No PID file found for $name"
    fi
}

# Stop application services
stop_service "frontend"
stop_service "kafka-consumer" 
stop_service "flask-api"

# Stop Docker services
echo "🐳 Stopping Docker services..."
docker-compose down

# Kill any remaining processes on our ports
echo "🧹 Cleaning up remaining processes..."

kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "🛑 Killing processes on port $port: $pids"
        echo $pids | xargs kill -9 2>/dev/null
    fi
}

kill_port 3000
kill_port 5000

echo "✅ All services stopped!"
echo ""
echo "To restart: ./start.sh"
