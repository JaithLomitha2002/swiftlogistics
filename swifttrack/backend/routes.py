
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, User, Goods, Cart, CartItem, Order, OrderItem, Warehouse, DeliveryPerson, DeliveryStatus, Payment
from .kafka_producer import publish_order_message
from adapters.payment_adapter import process_payment
import datetime

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
    if session.query(User).filter_by(email=email).first():
        session.close()
        return jsonify({'error': 'Email already registered'}), 400
    user = User(name=name, email=email, password=password, role=role)
    session.add(user)
    session.commit()
    session.close()
    return jsonify({'message': 'Registration successful'})

# Login endpoint
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    session = Session()
    user = session.query(User).filter_by(email=email, password=password).first()
    if not user:
        session.close()
        return jsonify({'error': 'Invalid credentials'}), 401
    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    session.close()
    return jsonify({'access_token': access_token, 'role': user.role})

# Example protected endpoint for role-based access
def role_required(roles):
    def wrapper(fn):
        def decorator(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity or identity.get('role') not in roles:
                return jsonify({'error': 'Unauthorized'}), 403
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return jwt_required()(decorator)
    return wrapper

# Seller: add goods
@api_bp.route('/goods', methods=['POST'])
@role_required(['seller'])
def add_goods():
    data = request.get_json()
    identity = get_jwt_identity()
    session = Session()
    goods = Goods(
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        quantity=data.get('quantity'),
        seller_id=identity['id']
    )
    session.add(goods)
    session.commit()
    session.close()
    return jsonify({'message': 'Goods added'})

# User: add to cart
@api_bp.route('/cart', methods=['POST'])
@role_required(['user'])
def add_to_cart():
    data = request.get_json()
    identity = get_jwt_identity()
    session = Session()
    cart = session.query(Cart).filter_by(user_id=identity['id']).first()
    if not cart:
        cart = Cart(user_id=identity['id'])
        session.add(cart)
        session.commit()
    cart_item = CartItem(cart_id=cart.id, goods_id=data.get('goods_id'), quantity=data.get('quantity'))
    session.add(cart_item)
    session.commit()
    session.close()
    return jsonify({'message': 'Added to cart'})

# User: buy (create order from cart)
@api_bp.route('/buy', methods=['POST'])
@role_required(['user'])
def buy():
    identity = get_jwt_identity()
    session = Session()
    cart = session.query(Cart).filter_by(user_id=identity['id']).first()
    if not cart or not cart.items:
        session.close()
        return jsonify({'error': 'Cart is empty'}), 400
    order = Order(user_id=identity['id'], created_at=datetime.datetime.utcnow(), status='pending')
    session.add(order)
    session.commit()
    total = 0
    for item in cart.items:
        order_item = OrderItem(order_id=order.id, goods_id=item.goods_id, quantity=item.quantity)
        session.add(order_item)
        goods = session.query(Goods).get(item.goods_id)
        if goods:
            total += goods.price * item.quantity
            goods.quantity -= item.quantity
    session.query(CartItem).filter_by(cart_id=cart.id).delete()
    session.commit()
    payment_result = process_payment(order.id, total)
    if payment_result['status'] != 'success':
        session.delete(order)
        session.commit()
        session.close()
        return jsonify({'error': payment_result['message']}), 400
    payment = Payment(order_id=order.id, amount=total, status='success', created_at=datetime.datetime.utcnow())
    session.add(payment)
    status = DeliveryStatus(order_id=order.id, status='Created', updated_at=datetime.datetime.utcnow())
    session.add(status)
    session.commit()
    publish_order_message({'order_id': order.id, 'user_id': identity['id']})
    session.close()
    return jsonify({'order_id': order.id, 'status': 'Created', 'payment': 'success'})

# Seller: update order status
@api_bp.route('/order/<int:order_id>/status', methods=['PUT'])
@role_required(['seller', 'warehouse', 'delivery'])
def update_order_status(order_id):
    data = request.get_json()
    status_text = data.get('status')
    session = Session()
    status = DeliveryStatus(order_id=order_id, status=status_text, updated_at=datetime.datetime.utcnow())
    session.add(status)
    session.commit()
    session.close()
    return jsonify({'message': 'Order status updated'})

# Warehouse: assign delivery person
@api_bp.route('/order/<int:order_id>/assign_delivery', methods=['POST'])
@role_required(['warehouse'])
def assign_delivery(order_id):
    data = request.get_json()
    delivery_person_id = data.get('delivery_person_id')
    session = Session()
    # Logic to assign delivery person to order (could be a field in Order or DeliveryStatus)
    # For simplicity, just update status
    status = DeliveryStatus(order_id=order_id, status='Assigned to delivery', updated_at=datetime.datetime.utcnow())
    session.add(status)
    session.commit()
    session.close()
    return jsonify({'message': 'Delivery person assigned'})

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
