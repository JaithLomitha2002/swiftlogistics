import requests

def process_order(order_data):
    # Mock REST request
    url = 'https://jsonplaceholder.typicode.com/posts'  # Fake endpoint
    print(f"Calling REST endpoint for order: {order_data}")
    # This is a mock, so we won't actually send a real request
    # response = requests.post(url, json=order_data)
    return {'status': 'success', 'adapter': 'ROS'}
