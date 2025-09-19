# SwiftTrack Middleware Architecture

## 🎯 Complete Middleware Solution

This project implements a complete middleware architecture for SwiftLogistics that demonstrates:

✅ **Heterogeneous Systems Integration**: SOAP (CMS), REST (ROS), TCP/IP (WMS)  
✅ **Real-time Tracking & Notifications**: Socket.IO WebSocket implementation  
✅ **Asynchronous Processing**: Apache Kafka message broker  
✅ **Transaction Management**: Payment processing with rollback capabilities  
✅ **Scalability & Resilience**: Microservices architecture with fault tolerance  
✅ **Security**: JWT authentication and secure API communication  

## 🚀 Quick Start

```bash
# Start everything
./start.sh

# Verify system health
./verify.sh

# Stop everything
./stop.sh
```

## 🌐 Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 📱 How to Test

1. Visit http://localhost:3000
2. Go to "Orders" page
3. Submit a test order
4. Watch real-time updates on "Tracking" page

## 🔧 Troubleshooting

```bash
# View logs
tail -f swifttrack/logs/flask-api.log
tail -f swifttrack/logs/kafka-consumer.log

# Restart if needed
./stop.sh && ./start.sh
```

## 🏗️ Architecture

The system demonstrates a complete middleware architecture with:
- Protocol adapters for SOAP, REST, and TCP/IP
- Asynchronous message processing via Kafka
- Real-time updates via WebSocket
- Transaction management and rollback
- Scalable microservices design

Perfect for assignment demonstration! 🎯
