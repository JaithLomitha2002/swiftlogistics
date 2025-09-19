from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# User model with roles
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # user, seller, delivery, warehouse
    seller_goods = relationship('Goods', back_populates='seller')
    orders = relationship('Order', back_populates='user')
    deliveries = relationship('DeliveryPerson', back_populates='user')


# Goods model
class Goods(Base):
    __tablename__ = 'goods'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    seller_id = Column(Integer, ForeignKey('users.id'))
    seller = relationship('User', back_populates='seller_goods')
    orders = relationship('OrderItem', back_populates='goods')

# Cart model
class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    items = relationship('CartItem', back_populates='cart')

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    goods_id = Column(Integer, ForeignKey('goods.id'))
    quantity = Column(Integer, nullable=False)
    cart = relationship('Cart', back_populates='items')
    goods = relationship('Goods')

# Order model
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    status = Column(String, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order')
    delivery_statuses = relationship('DeliveryStatus', back_populates='order')
    payment = relationship('Payment', back_populates='order', uselist=False)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    goods_id = Column(Integer, ForeignKey('goods.id'))
    quantity = Column(Integer, nullable=False)
    order = relationship('Order', back_populates='items')
    goods = relationship('Goods', back_populates='orders')

# Warehouse model
class Warehouse(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    orders = relationship('Order', back_populates='warehouse')
    delivery_persons = relationship('DeliveryPerson', back_populates='warehouse')

# Delivery person model
class DeliveryPerson(Base):
    __tablename__ = 'delivery_persons'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    user = relationship('User', back_populates='deliveries')
    warehouse = relationship('Warehouse', back_populates='delivery_persons')

# Delivery status model
class DeliveryStatus(Base):
    __tablename__ = 'delivery_statuses'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    status = Column(String, nullable=False)  # e.g. started packaging, packaging done, handed over, delivered
    updated_at = Column(DateTime)
    order = relationship('Order', back_populates='delivery_statuses')


# Payment table
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime)
    order = relationship('Order', back_populates='payment')
