import os
import sys
from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Add the parent directory to the path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from routes import api_bp
    from socketio import socketio
except ImportError:
    print("❌ Import error: Make sure all required files are in place")
    sys.exit(1)

def create_app():
    """Application factory pattern for better organization"""
    app = Flask(__name__)
    
    # Configuration
    app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # Initialize extensions
    jwt = JWTManager(app)
    CORS(app, origins=["http://localhost:3000"])
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Serve static files from frontend build (for production)
    @app.route('/')
    def serve_frontend():
        try:
            return send_from_directory('../frontend/dist', 'index.html')
        except:
            return {"message": "SwiftTrack API is running", "frontend": "not built"}, 200
    
    @app.route('/<path:path>')
    def serve_static(path):
        try:
            return send_from_directory('../frontend/dist', path)
        except:
            return {"error": "File not found"}, 404
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {
            "status": "healthy",
            "service": "SwiftTrack Middleware API",
            "version": "1.0.0"
        }
    
    # Initialize Socket.IO
    socketio.init_app(app, cors_allowed_origins="*")
    
    return app

def main():
    """Main application entry point"""
    print("🚀 Starting SwiftTrack Middleware API...")
    print("========================================")
    
    # Create Flask app
    app = create_app()
    
    # Check if running in development mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🌐 Server starting on http://localhost:5000")
    print(f"🔧 Debug mode: {debug_mode}")
    print(f"📡 Socket.IO enabled for real-time updates")
    print("========================================")
    
    # Start the server
    try:
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=debug_mode,
            allow_unsafe_werkzeug=True  # For development only
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()
