
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins='*')

# Example event
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# Function to emit status updates
def emit_status_update(order_id, status):
    socketio.emit('status_update', {'order_id': order_id, 'status': status})

# Function to emit payment status
def emit_payment_status(order_id, payment_status):
    socketio.emit('payment_status', {'order_id': order_id, 'payment_status': payment_status})
