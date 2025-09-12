from zeep import Client

def process_order(order_data):
    # Mock SOAP request
    wsdl = 'http://www.webservicex.net/geoipservice.asmx?WSDL'  # Example WSDL
    client = Client(wsdl)
    # This is a mock, so we won't actually send a real request
    print(f"Sending SOAP request for order: {order_data}")
    return {'status': 'success', 'adapter': 'CMS'}
