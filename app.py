import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json

app = Flask(__name__)

# Configure CORS for your deployed frontend domain.
# Replace 'https://your-app-name.onrender.com' with the URL of your deployed frontend.
# The '*' allows all origins, which is fine for local testing but less secure for production.
CORS(app, origins='*')

# Simple in-memory storage for development purposes. In a real app, use a database.
users = {}
workouts = {}

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    if username in users:
        return jsonify({"success": False, "message": "Username already exists"}), 409

    # Store a hashed password for security
    hashed_password = generate_password_hash(password)
    users[username] = {"password": hashed_password}
    return jsonify({"success": True, "message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login_user():
    """Log in an existing user."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user_data = users.get(username)
    if user_data and check_password_hash(user_data['password'], password):
        return jsonify({"success": True, "message": "Login successful"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/add_workout', methods=['POST'])
def add_workout():
    """Add a new workout for a user."""
    data = request.json
    username = data.get('username')
    activity_type = data.get('activityType')
    duration = data.get('duration')
    calories = data.get('calories')

    if not all([username, activity_type, duration, calories]):
        return jsonify({"success": False, "message": "Missing workout data"}), 400

    workout_id = str(uuid.uuid4())
    workout_entry = {
        "id": workout_id,
        "username": username,
        "activityType": activity_type,
        "duration": duration,
        "calories": calories,
        "timestamp": workout_entry.get('timestamp', datetime.utcnow().isoformat() + 'Z')
    }
    
    if username not in workouts:
        workouts[username] = []
    workouts[username].append(workout_entry)
    
    return jsonify({"success": True, "message": "Workout added successfully", "id": workout_id}), 201

@app.route('/get_workouts', methods=['GET'])
def get_workouts():
    """Retrieve all workouts for a user."""
    username = request.args.get('username')
    user_workouts = workouts.get(username, [])
    return jsonify({"success": True, "workouts": user_workouts}), 200

@app.route('/delete_workout/<workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """Delete a specific workout."""
    username = request.json.get('username')
    if username not in workouts:
        return jsonify({"success": False, "message": "User not found"}), 404

    initial_count = len(workouts[username])
    workouts[username] = [w for w in workouts[username] if w['id'] != workout_id]
    
    if len(workouts[username]) < initial_count:
        return jsonify({"success": True, "message": "Workout deleted successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Workout not found"}), 404

# Use Gunicorn for production instead of Flask's built-in server.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
