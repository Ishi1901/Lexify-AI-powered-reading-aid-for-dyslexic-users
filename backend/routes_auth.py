from flask import Blueprint, request, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Create the Blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    username, password = data.get('username'), data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    hashed_pw = generate_password_hash(password)
    try:
        with sqlite3.connect('lexify.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    username, password = data.get('username'), data.get('password')
    
    with sqlite3.connect('lexify.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password, font_size, font_color, tts_volume, tts_speed FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
    if user and check_password_hash(user[0], password):
        return jsonify({
            "message": "Login successful",
            "settings": {"font_size": user[1], "font_color": user[2], "tts_volume": user[3], "tts_speed": user[4]}
        }), 200
    return jsonify({"error": "Invalid username or password"}), 401

@auth_bp.route('/save_settings', methods=['POST', 'OPTIONS'])
def save_settings():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.json
    with sqlite3.connect('lexify.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET font_size = ?, font_color = ?, tts_volume = ?, tts_speed = ? WHERE username = ?
        """, (data.get('font_size'), data.get('font_color'), data.get('tts_volume'), data.get('tts_speed'), data.get('username')))
        conn.commit()
    return jsonify({"message": "Settings saved successfully!"}), 200