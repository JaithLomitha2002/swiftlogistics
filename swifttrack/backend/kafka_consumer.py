import sys
import os
import json
import time
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from kafka import KafkaConsumer
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from database.models import DeliveryStatus
    import datetime
    from adapters.cms_adapter import process_order as cms_process_order
    from adapters.ros_adapter import process_order as ros_process_order
    from adapters.wms_adapter import process_order as wms_process_order
    from backend.socketio import emit_status_update
except ImportError as e:
    print(f"❌ Import error in kafka_consumer.py: {e}")
    print("ℹ️  Some features may not work until Kafka is running")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = 'postgresql+psycopg2://postgres:mycoc1@localhost:5432/swifttrack'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class MiddlewareOrchestrator:
    """
    Middleware orchestrator that processes orders through all three systems
    Demonstrates heterogeneous systems integration and transaction management
    """
    
    def __init__(self):
        self.session = None
        
    def process_order_workflow(self, order_data):
        """
        Orchestrates the complete order processing workflow
        through CMS, ROS, and WMS systems
        """
        order_id = order_data['order_id']
        
        try:
            self.session = Session()
            
            # Step 1: Update status to processing
            self.update_status(order_id, "Processing Order")
            time.sleep(1)  # Simulate processing time
            
            # Step 2: Process through CMS (Client Management System)
            logger.info(f"Processing order {order_id} through CMS...")
            cms_result = cms_process_order(order_data)
            
            if cms_result.get('status') == 'success':
                self.update_status(order_id, "Client Information Validated")
                time.sleep(1)
            else:
                raise Exception("CMS processing failed")
            
            # Step 3: Process through WMS (Warehouse Management System)
            logger.info(f"Processing order {order_id} through WMS...")
            wms_result = wms_process_order(order_data)
            
            if wms_result.get('status') == 'success':
                self.update_status(order_id, "Package Prepared in Warehouse")
                time.sleep(1)
            else:
                raise Exception("WMS processing failed")
            
            # Step 4: Process through ROS (Route Optimization System)
            logger.info(f"Processing order {order_id} through ROS...")
            ros_result = ros_process_order(order_data)
            
            if ros_result.get('status') == 'success':
                self.update_status(order_id, "Route Optimized for Delivery")
                time.sleep(1)
            else:
                raise Exception("ROS processing failed")
            
            # Step 5: Final processing steps
            self.update_status(order_id, "Out for Delivery")
            time.sleep(2)
            
            self.update_status(order_id, "Delivered Successfully")
            
            logger.info(f"Order {order_id} processed successfully through all systems")
            
            # Compile results
            return {
                'order_id': order_id,
                'status': 'completed',
                'cms_result': cms_result,
                'wms_result': wms_result,
                'ros_result': ros_result,
                'processed_at': datetime.datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing order {order_id}: {str(e)}")
            self.update_status(order_id, f"Processing Failed: {str(e)}")
            
            # Transaction rollback simulation
            self.update_status(order_id, "Order Cancelled - Refund Initiated")
            
            return {
                'order_id': order_id,
                'status': 'failed',
                'error': str(e),
                'failed_at': datetime.datetime.utcnow().isoformat()
            }
        
        finally:
            if self.session:
                self.session.close()
    
    def update_status(self, order_id, status_text):
        """Update order status in database and emit real-time update"""
        try:
            status = DeliveryStatus(
                order_id=order_id,
                status=status_text,
                updated_at=datetime.datetime.utcnow()
            )
            self.session.add(status)
            self.session.commit()
            
            # Emit real-time update to frontend
            try:
                emit_status_update(order_id, status_text)
            except:
                pass  # Continue even if Socket.IO fails
            
            logger.info(f"Order {order_id} status updated to: {status_text}")
            
        except Exception as e:
            logger.error(f"Failed to update status for order {order_id}: {str(e)}")
            if self.session:
                self.session.rollback()

def consume_order_messages():
    """
    Main Kafka consumer function
    Demonstrates asynchronous message processing
    """
    
    try:
        # Initialize middleware orchestrator
        orchestrator = MiddlewareOrchestrator()
        
        # Configure Kafka consumer
        consumer = KafkaConsumer(
            'orders',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='swifttrack-middleware'
        )
        
        logger.info("Kafka consumer started. Waiting for messages...")
        
        for message in consumer:
            order_data = message.value
            logger.info(f"Received order: {order_data}")
            
            # Process through middleware orchestrator
            result = orchestrator.process_order_workflow(order_data)
            
            logger.info(f"Order processing result: {result}")
            
    except ImportError:
        logger.error("Kafka not available - install kafka-python: pip install kafka-python")
    except Exception as e:
        logger.error(f"Consumer error: {str(e)}")
        logger.info("Make sure Kafka is running: docker-compose up -d")

if __name__ == '__main__':
    consume_order_messages()
