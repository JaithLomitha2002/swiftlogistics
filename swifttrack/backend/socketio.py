from flask_socketio import SocketIO, emit
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Socket.IO
socketio = SocketIO(cors_allowed_origins='*')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to Socket.IO')
    emit('connection_status', {'status': 'connected', 'message': 'Real-time updates active'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from Socket.IO')

# Function to emit status updates
def emit_status_update(order_id, status):
    """Emit order status update to all connected clients"""
    try:
        socketio.emit('status_update', {
            'order_id': order_id, 
            'status': status,
            'timestamp': str(datetime.datetime.utcnow())
        })
        logger.info(f'Emitted status update for order {order_id}: {status}')
    except Exception as e:
        logger.error(f'Failed to emit status update: {e}')

# Function to emit payment status
def emit_payment_status(order_id, payment_status):
    """Emit payment status update to all connected clients"""
    try:
        socketio.emit('payment_status', {
            'order_id': order_id, 
            'payment_status': payment_status,
            'timestamp': str(datetime.datetime.utcnow())
        })
        logger.info(f'Emitted payment status for order {order_id}: {payment_status}')
    except Exception as e:
        logger.error(f'Failed to emit payment status: {e}')

# Function to emit system notifications
def emit_system_notification(message, type='info'):
    """Emit system-wide notifications"""
    try:
        socketio.emit('system_notification', {
            'message': message,
            'type': type,
            'timestamp': str(datetime.datetime.utcnow())
        })
        logger.info(f'Emitted system notification: {message}')
    except Exception as e:
        logger.error(f'Failed to emit system notification: {e}')
