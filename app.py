from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Get environment variables
GEMINI_API_KEY = "AIzaSyDk7QwgTEsSJIAMidpHsufuO-6BP_DagrM"
MONGO_URI = "mongodb+srv://uneeb:n9QDgw4SwY8dUbvD@cluster0.7llxmx1.mongodb.net/mydatabase?retryWrites=true&w=majority&appName=Cluster0"
DEBUG_MODE = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Validate critical env variables
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in environment.")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set in environment.")

# Initialize Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# MongoDB configuration
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["mydatabase"]
users_collection = db["users"]

# Chat sessions storage
chat_sessions = {}
MODEL_ID = "gemini-1.5-flash"

# -----------------------------------------------------------------------------
# Signup Route
# -----------------------------------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Missing username, email, or password"}), 400

    if users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
        return jsonify({"error": "Username or email already exists"}), 409

    users_collection.insert_one({
        "username": username,
        "email": email,
        "password": generate_password_hash(password)
    })

    return jsonify({
        "message": "User signed up successfully",
        "username": username,
        "email": email
    }), 201

# -----------------------------------------------------------------------------
# Login Route
# -----------------------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid password"}), 401

    return jsonify({
        "message": "Login successful",
        "username": user["username"],
        "email": user["email"]
    }), 200

# -----------------------------------------------------------------------------
# Chat with Gemini API
# -----------------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_text = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not user_text:
        return jsonify({"error": "Message is required"}), 400

    # Reuse or start new chat session
    chat = chat_sessions.get(session_id) if session_id in chat_sessions else None
    if not chat:
        chat = gemini_client.chats.create(model=MODEL_ID)
        session_id = str(uuid4())
        chat_sessions[session_id] = chat

    # Send user message to Gemini
    try:
        gemini_reply = chat.send_message(user_text)
        assistant_text = gemini_reply.text
    except Exception as err:
        return jsonify({"error": f"Gemini API error: {err}"}), 502

    return jsonify({
        "response": assistant_text,
        "session_id": session_id
    }), 200

# -----------------------------------------------------------------------------
# Update Profile
# -----------------------------------------------------------------------------
@app.route("/update-profile", methods=["POST"])
def update_profile():
    data = request.get_json(force=True)
    current_email = data.get("email")
    new_name = data.get("name")
    new_email = data.get("new_email")
    new_password = data.get("password")

    if not current_email:
        return jsonify({"error": "Email is required to identify user"}), 400

    user = users_collection.find_one({"email": current_email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    update_fields = {}
    if new_name:
        update_fields["username"] = new_name
    if new_email:
        update_fields["email"] = new_email
    if new_password:
        update_fields["password"] = generate_password_hash(new_password)

    if not update_fields:
        return jsonify({"error": "No update data provided"}), 400

    users_collection.update_one({"email": current_email}, {"$set": update_fields})
    return jsonify({"message": "Profile updated successfully"}), 200

# -----------------------------------------------------------------------------
# Get All Users (For Testing/Admin Only)
# -----------------------------------------------------------------------------
@app.route("/users", methods=["GET"])
def get_all_users():
    users = users_collection.find({}, {"_id": 0, "username": 1, "email": 1, "password": 1})
    print({
        "users": list(users),
        "count": users_collection.count_documents({})
    })
    return jsonify({
        "users": list(users),
        "count": users_collection.count_documents({})
    }), 200

# -----------------------------------------------------------------------------
# Run the Flask App
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=DEBUG_MODE)