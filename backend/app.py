from flask import Flask
from flask_cors import CORS

# Import our custom modules
from database import init_db
from routes_auth import auth_bp
from routes_main import main_bp
from dotenv import load_dotenv

app = Flask(__name__)


# 🛡️ BULLETPROOF CORS SETUP
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize the Database
init_db()

# Register the Blueprints (Plug in the mini-apps)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    print("🚀 Starting Lexifyy Server...")
    app.run(debug=False, port=5000)