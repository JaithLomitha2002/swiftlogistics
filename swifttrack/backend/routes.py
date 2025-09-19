from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.models import Base, User, Goods, Cart, CartItem, Order, OrderItem, Warehouse, DeliveryPerson, DeliveryStatus, Payment
    from backend.kafka_producer import publish_order_message
    from adapters.payment_adapter import process_payment
    from adapters.cms_adapter import process_order as cms_process_order
    from adapters.ros_adapter import process_order as ros_process_order  
    from adapters.wms_adapter import process_order as wms_process_order
    from backend.socketio import emit_status_update, emit_payment_status
except ImportError as e:
    print(f"❌ Import error in routes.py: {e}")

import datetime
import uuid

DATABASE_URL = 'postgresql+psycopg2://postgres:mycoc1@localhost:5432/swifttrack'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

api_bp = Blueprint('api', __name__)

# Registration endpoint
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    session = Session()
    try:
        if session.query(User).filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        user = User(name=name, email=email, password=password, role=role)
        session.add(user)
        session.commit()
        return jsonify({'message': 'Registration successful'})
    finally:
        session.close()

# Login endpoint
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    session = Session()
    try:
        user = session.query(User).filter_by(email=email, password=password).first()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'access_token': access_token, 'role': user.role})
    finally:
        session.close()

# Enhanced order submission with middleware orchestration
@api_bp.route('/orders', methods=['POST'])
def submit_order():
    """
    Middleware orchestration for order processing
    Integrates CMS, ROS, and WMS through adapters
    """
    data = request.get_json()
    client = data.get('client')
    description = data.get('description')
    amount = data.get('amount')
    
    if not all([client, description, amount]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate unique order ID
    order_id = str(uuid.uuid4())[:8]
    
    session = Session()
    try:
        # Create order record
        order = Order(
            id=order_id,
            user_id=1,  # Default user for demo
            created_at=datetime.datetime.utcnow(),
            status='pending'
        )
        session.add(order)
        session.commit()
        
        # Initial status
        status = DeliveryStatus(
            order_id=order_id,
            status='Order Created',
            updated_at=datetime.datetime.utcnow()
        )
        session.add(status)
        session.commit()
        
        # Emit initial status
        try:
            emit_status_update(order_id, 'Order Created')
        except:
            pass  # Continue even if Socket.IO fails
        
        # Process payment through payment adapter
        payment_result = process_payment(order_id, amount)
        try:
            emit_payment_status(order_id, payment_result['status'])
        except:
            pass
        
        if payment_result['status'] != 'success':
            session.delete(order)
            session.commit()
            return jsonify({'error': payment_result['message']}), 400
        
        # Record successful payment
        payment = Payment(
            order_id=order_id,
            amount=amount,
            status='success',
            created_at=datetime.datetime.utcnow()
        )
        session.add(payment)
        session.commit()
        
        # Publish to Kafka for asynchronous processing
        order_data = {
            'order_id': order_id,
            'client': client,
            'description': description,
            'amount': amount,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        
        try:
            publish_order_message(order_data)
        except Exception as e:
            print(f"⚠️  Kafka publish failed: {e}")
        
        return jsonify({
            'order_id': order_id,
            'status': 'Created',
            'payment': 'success',
            'message': 'Order submitted for processing'
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Order processing failed: {str(e)}'}), 500
    finally:
        session.close()

# Direct middleware test endpoints
@api_bp.route('/test/cms', methods=['POST'])
def test_cms_adapter():
    """Test CMS SOAP adapter directly"""
    data = request.get_json()
    try:
        result = cms_process_order(data)
        return jsonify({'cms_result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/test/ros', methods=['POST'])
def test_ros_adapter():
    """Test ROS REST adapter directly"""
    data = request.get_json()
    try:
        result = ros_process_order(data)
        return jsonify({'ros_result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/test/wms', methods=['POST'])
def test_wms_adapter():
    """Test WMS TCP/IP adapter directly"""
    data = request.get_json()
    try:
        result = wms_process_order(data)
        return jsonify({'wms_result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get order status
@api_bp.route('/status/<order_id>', methods=['GET'])
def get_order_status(order_id):
    session = Session()
    try:
        statuses = session.query(DeliveryStatus).filter_by(
            order_id=order_id
        ).order_by(DeliveryStatus.updated_at.desc()).all()
        
        if not statuses:
            return jsonify({'error': 'Order not found'}), 404
        
        status_history = [{
            'status': s.status,
            'timestamp': s.updated_at.isoformat()
        } for s in statuses]
        
        return jsonify({
            'order_id': order_id,
            'current_status': statuses[0].status,
            'history': status_history
        })
    finally:
        session.close()

# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    """System health check"""
    session = Session()
    try:
        # Test database connection
        session.execute('SELECT 1')
        db_status = 'healthy'
    except:
        db_status = 'unhealthy'
    finally:
        session.close()
    
    return jsonify({
        'status': 'running',
        'database': db_status,
        'adapters': {
            'cms': 'available',
            'ros': 'available', 
            'wms': 'available'
        }
    })

# System metrics endpoint
@api_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics for monitoring"""
    session = Session()
    try:
        # Count orders by status
        total_orders = session.query(Order).count()
        
        return jsonify({
            'orders': {
                'total': total_orders
            },
            'system': 'operational'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
