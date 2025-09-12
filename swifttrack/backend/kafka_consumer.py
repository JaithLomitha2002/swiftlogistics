
from kafka import KafkaConsumer
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import DeliveryStatus
import datetime
from adapters.cms_adapter import process_order as cms_process_order
from adapters.ros_adapter import process_order as ros_process_order
from adapters.wms_adapter import process_order as wms_process_order
from backend.socketio import socketio

DATABASE_URL = 'postgresql+psycopg2://postgres:mycoc1@localhost:5432/swifttrack'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def consume_order_messages():
    consumer = KafkaConsumer(
        'orders',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    for message in consumer:
        order_data = message.value
        print(f"Received: {order_data}")
        # Call adapters
        cms_result = cms_process_order(order_data)
        ros_result = ros_process_order(order_data)
        wms_result = wms_process_order(order_data)
        # Update DB
        session = Session()
        status = DeliveryStatus(order_id=order_data['order_id'], status='Processed', updated_at=datetime.datetime.utcnow())
        session.add(status)
        session.commit()
        session.close()
        # Emit status update
        socketio.emit('status_update', {'order_id': order_data['order_id'], 'status': 'Processed'})
