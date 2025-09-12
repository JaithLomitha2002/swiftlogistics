from kafka import KafkaProducer
import json

def publish_order_message(message: dict):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send('orders', message)
    producer.flush()
    producer.close()
