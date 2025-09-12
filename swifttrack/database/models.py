from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    orders = relationship('Order', back_populates='client')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    description = Column(String, nullable=False)
    created_at = Column(DateTime)
    status = relationship('DeliveryStatus', back_populates='order')
    client = relationship('Client', back_populates='orders')


class DeliveryStatus(Base):
    __tablename__ = 'delivery_statuses'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    status = Column(String, nullable=False)
    updated_at = Column(DateTime)
    order = relationship('Order', back_populates='status')

# New Payment table
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime)
