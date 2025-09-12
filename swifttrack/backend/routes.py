
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Client, Order, DeliveryStatus, Payment
from .kafka_producer import publish_order_message
from adapters.payment_adapter import process_payment
import datetime

DATABASE_URL = 'postgresql+psycopg2://postgres:mycoc1@localhost:5432/swifttrack'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

api_bp = Blueprint('api', __name__)


@api_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    client_name = data.get('client')
    description = data.get('description')
    amount = data.get('amount', 100)  # Default amount if not provided
    session = Session()
    client = session.query(Client).filter_by(name=client_name).first()
    if not client:
        client = Client(name=client_name, email=f"{client_name}@example.com")
        session.add(client)
        session.commit()
    order = Order(client_id=client.id, description=description, created_at=datetime.datetime.utcnow())
    session.add(order)
    session.commit()
    # Call payment adapter
    payment_result = process_payment(order.id, amount)
    if payment_result['status'] != 'success':
        session.delete(order)
        session.commit()
        session.close()
        return jsonify({'error': payment_result['message']}), 400
    # Save payment record
    payment = Payment(order_id=order.id, amount=amount, status='success', created_at=datetime.datetime.utcnow())
    session.add(payment)
    # Initial status
    status = DeliveryStatus(order_id=order.id, status='Created', updated_at=datetime.datetime.utcnow())
    session.add(status)
    session.commit()
    # Send to Kafka
    publish_order_message({'order_id': order.id, 'client': client.name, 'description': description})
    session.close()
    return jsonify({'order_id': order.id, 'status': 'Created', 'payment': 'success'})

@api_bp.route('/status/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_status(order_id):
    session = Session()
    status = session.query(DeliveryStatus).filter_by(order_id=order_id).order_by(DeliveryStatus.updated_at.desc()).first()
    if status:
        result = {'order_id': order_id, 'status': status.status, 'updated_at': status.updated_at}
    else:
        result = {'error': 'Order not found'}
    session.close()
    return jsonify(result)
