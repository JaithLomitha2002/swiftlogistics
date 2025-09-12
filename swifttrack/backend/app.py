from flask import Flask
from flask_jwt_extended import JWTManager
from .routes import api_bp
from .socketio import socketio

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production
jwt = JWTManager(app)

app.register_blueprint(api_bp)
socketio.init_app(app)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
