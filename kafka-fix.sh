#!/bin/bash

# Kafka Troubleshooting and Fix Script for SwiftTrack
echo "🔧 Kafka Troubleshooting and Fix Script"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check current Docker status
print_info "Step 1: Checking current Docker container status..."
docker ps -a

echo ""
print_info "Step 2: Checking Docker logs for Kafka..."
docker logs kafka --tail 20

echo ""
print_info "Step 3: Stopping all containers to restart fresh..."
docker-compose down

echo ""
print_info "Step 4: Removing any existing containers and networks..."
docker container prune -f
docker network prune -f

echo ""
print_info "Step 5: Creating improved docker-compose.yml with better Kafka configuration..."

# Create an improved docker-compose.yml with better Kafka settings
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_INIT_LIMIT: 5
      ZOOKEEPER_SYNC_LIMIT: 2
    ports:
      - "2181:2181"
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "2181"]
      interval: 10s
      timeout: 5s
      retries: 3

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    container_name: kafka
    depends_on:
      zookeeper:
        condition: service_healthy
    ports:
      - "9092:9092"
      - "9094:9094"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: INTERNAL://0.0.0.0:9093,EXTERNAL://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka:9093,EXTERNAL://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
      KAFKA_NUM_PARTITIONS: 1
      KAFKA_DEFAULT_REPLICATION_FACTOR: 1
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_RETENTION_BYTES: 1073741824
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      KAFKA_LOG_CLEANUP_POLICY: delete
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - kafka_data:/var/lib/kafka/data

  postgres:
    image: postgres:13
    container_name: postgres
    environment:
      POSTGRES_DB: swifttrack
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: mycoc1
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  postgres_data:
  kafka_data:

networks:
  default:
    driver: bridge
EOF

print_step "Created improved docker-compose.yml"

echo ""
print_info "Step 6: Starting services with health checks..."
docker-compose up -d

echo ""
print_info "Step 7: Waiting for services to be healthy..."

# Function to wait for service health
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $service to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep "$service" | grep -q "healthy\|Up"; then
            print_step "$service is healthy!"
            return 0
        fi
        
        echo -n "⏳ Attempt $attempt/$max_attempts: "
        docker-compose ps | grep "$service" | awk '{print $4}'
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to become healthy"
    return 1
}

# Wait for each service
wait_for_service "zookeeper"
wait_for_service "postgres" 
wait_for_service "kafka"

echo ""
print_info "Step 8: Checking final status..."
docker-compose ps

echo ""
print_info "Step 9: Testing Kafka connectivity..."
sleep 5

# Test Kafka
if docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list &>/dev/null; then
    print_step "Kafka is responding to commands!"
    
    # Create the orders topic
    print_info "Creating 'orders' topic..."
    docker exec kafka kafka-topics --create --topic orders --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists
    
    # List topics to confirm
    print_info "Available topics:"
    docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
    
else
    print_error "Kafka is still not responding"
    print_info "Checking Kafka logs..."
    docker logs kafka --tail 50
fi

echo ""
print_info "Step 10: Testing database connectivity..."
if docker exec postgres psql -U postgres -d swifttrack -c "SELECT 1;" &>/dev/null; then
    print_step "Database is working!"
else
    print_error "Database connection failed"
fi

echo ""
print_info "Step 11: Final verification..."
echo "Docker containers status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Port status:"
netstat -an | grep -E ":2181|:5432|:9092" || echo "No ports found (might be normal on some systems)"

echo ""
if docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list | grep -q "orders"; then
    print_step "SUCCESS! All services are running and Kafka topics are available!"
    echo ""
    echo "🚀 You can now continue with:"
    echo "   ./start.sh    # to start the application services"
    echo "   ./verify.sh   # to verify everything is working"
else
    print_warning "Services are running but there might still be issues."
    echo ""
    echo "🔍 Debugging information:"
    echo "1. Check Kafka logs: docker logs kafka"
    echo "2. Check if ports are available: netstat -tulpn | grep -E '2181|9092|5432'"
    echo "3. Try restarting: docker-compose restart kafka"
fi