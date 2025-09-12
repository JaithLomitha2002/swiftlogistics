import random

def process_payment(order_id, amount):
    success = random.choice([True, False])
    if success:
        return {
            'order_id': order_id,
            'amount': amount,
            'status': 'success',
            'message': f'Payment of {amount} for order {order_id} processed successfully.'
        }
    else:
        return {
            'order_id': order_id,
            'amount': amount,
            'status': 'failure',
            'message': f'Payment of {amount} for order {order_id} failed.'
        }
