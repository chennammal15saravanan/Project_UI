from flask import Flask, render_template, request, redirect, url_for, session, jsonify


from flask_cors import CORS
from supabase import create_client, Client
import bcrypt
import uuid
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)
app.secret_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwemp3ZnJkcW13dnBpZXlzdmJvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTYyMDMxOCwiZXhwIjoyMDY1MTk2MzE4fQ.5Zjkse9VfI_aHdtot9b2aFe46a0OvZZe8gVPUAF8Ric'  # 🔐 Replace with a strong random string

# Supabase setup
SUPABASE_URL = "https://fpzjwfrdqmwvpieysvbo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwemp3ZnJkcW13dnBpZXlzdmJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk2MjAzMTgsImV4cCI6MjA2NTE5NjMxOH0.oz3mhk_PAWuodODGIHFUEv93quWQRhMwe6agBmDD2vU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# UUID validation
def is_valid_uuid(val):
    return bool(re.fullmatch(
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', val
    ))
# HOME PAGE
@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/auth')
def index():
    return render_template('index.html')


@app.route('/train.html')
def train_page():
    return render_template('train.html')
@app.route('/mybots')
def bot_dashboard():
    return render_template('botDisplay.html')








@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({'message': 'All fields are required'}), 400

        # Check for existing user
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'message': 'User already exists'}), 400

        # Create user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = str(uuid.uuid4())
        if not is_valid_uuid(user_id):
            return jsonify({'message': 'Invalid user ID'}), 500

        new_user = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'password': hashed_password,
            'registration_time': datetime.utcnow().isoformat()
        }

        supabase.table('users').insert(new_user).execute()
        return jsonify({'message': 'Registration successful', 'user_id': user_id}), 200

    except Exception as e:
        print(f"[REGISTER ERROR] {str(e)}")
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        # Fetch user from Supabase
        user_response = supabase.table('users').select('*').eq('email', email).execute()

        if not user_response.data:
            return jsonify({'message': 'User not found'}), 404

        user_data = user_response.data[0]

        # Validate password
        if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
            return jsonify({'message': 'Incorrect password'}), 401

        # Update last login
        login_time = datetime.utcnow().isoformat()
        supabase.table('users').update({'last_login': login_time}).eq('email', email).execute()

        # ✅ Return success with redirect to train page (static or template)
        return jsonify({
            'message': 'Login successful!',
            'redirect': '/train.html'  # or '/train' if using render_template
        }), 200

    except Exception as e:
        print(f"[LOGIN ERROR] {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('homepage'))  # or the correct home route

    


   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
