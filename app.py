from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import uuid

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all domains, which is needed for a simple setup where the
# frontend is served from a different origin (e.g., a local file)
CORS(app)

# --- Simple In-Memory "Database" ---
# NOTE: For a production application, you should use a real database
# like PostgreSQL, MySQL, or MongoDB, and a proper authentication system.
# This is for demonstration purposes only.
users = {}
workouts = {}

@app.route('/register', methods=['POST'])
def register():
    """
    Endpoint for user registration.
    Expects a JSON payload with 'username' and 'password'.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required."}), 400

    if username in users:
        return jsonify({"success": False, "message": "Username already exists."}), 409

    # In a real app, you would hash the password before storing it
    users[username] = {"password": password}
    workouts[username] = []  # Initialize an empty workout list for the new user

    return jsonify({"success": True, "message": "User registered successfully."}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint for user login.
    Expects a JSON payload with 'username' and 'password'.
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username not in users or users[username]["password"] != password:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

    return jsonify({"success": True, "message": "Login successful."}), 200

@app.route('/add_workout', methods=['POST'])
def add_workout():
    """
    Endpoint to add a new workout for a user.
    Expects a JSON payload with 'username', 'activityType', 'duration', and 'calories'.
    """
    data = request.json
    username = data.get('username')
    activity_type = data.get('activityType')
    duration = data.get('duration')
    calories = data.get('calories')

    if not all([username, activity_type, duration, calories]):
        return jsonify({"success": False, "message": "Missing workout data."}), 400

    if username not in users:
        return jsonify({"success": False, "message": "User not found."}), 404

    # Create a unique ID for the workout
    workout_id = str(uuid.uuid4())
    workout = {
        "id": workout_id,
        "activityType": activity_type,
        "duration": duration,
        "calories": calories,
        "timestamp": datetime.datetime.now().isoformat()
    }

    workouts[username].append(workout)

    return jsonify({"success": True, "message": "Workout added successfully."}), 201

@app.route('/get_workouts', methods=['GET'])
def get_workouts():
    """
    Endpoint to retrieve all workouts for a specific user.
    Expects a 'username' query parameter.
    """
    username = request.args.get('username')

    if not username:
        return jsonify({"success": False, "message": "Username is required."}), 400

    if username not in workouts:
        return jsonify({"success": False, "message": "User not found."}), 404

    user_workouts = workouts.get(username, [])

    return jsonify({"success": True, "workouts": user_workouts}), 200

@app.route('/delete_workout/<string:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """
    Endpoint to delete a workout for a user.
    Expects 'workout_id' in the URL and 'username' in the JSON body.
    """
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({"success": False, "message": "Username is required."}), 400

    if username not in workouts:
        return jsonify({"success": False, "message": "User not found."}), 404

    # Find the workout to delete by its ID
    initial_count = len(workouts[username])
    workouts[username] = [w for w in workouts[username] if w['id'] != workout_id]

    if len(workouts[username]) == initial_count:
        return jsonify({"success": False, "message": "Workout not found."}), 404

    return jsonify({"success": True, "message": "Workout deleted successfully."}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
