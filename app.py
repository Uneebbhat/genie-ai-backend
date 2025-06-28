from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import os
from dotenv import load_dotenv
from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
# Remove the following line:
# client = genai.Client()

load_dotenv()  # pulls in .env variables

client = genai.Client(api_key="AIzaSyDk7QwgTEsSJIAMidpHsufuO-6BP_DagrM")

app = Flask(__name__)

# Configure Gemini
# genai.configure(api_key=)
# genai.configure(
#     api_key=os.getenv("AIzaSyDk7QwgTEsSJIAMidpHsufuO-6BP_DagrM"),   # or hard-code while testing
#     api_version="v1"                       # ← forces the stable v1 endpoint
# )

MODEL_ID = "gemini-1.5-flash" 

# --- MongoDB ---------------------------------------------------------------
client = MongoClient("mongodb+srv://uneeb:41o4yvMpBUimnEol@cluster0.7llxmx1.mongodb.net/genie?retryWrites=true&w=majority&appName=Cluster")
db = client["mydatabase"]
users_collection = db["users"]


# We'll reuse one GenerativeModel instance process-wide
# MODEL = genai.GenerativeModel("gemini-2.5-pro")   # or "gemini-2.5-flash"
chat_sessions = {}

# ---------------------------------------------------------------------------
#  AUTH
# ---------------------------------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    username = data.get("username")
    email    = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"error": "Missing username, email, or password"}), 400

    if users_collection.find_one({"$or": [{"username": username},
                                          {"email": email}]}):
        return jsonify({"error": "Username or email already exists"}), 409

    users_collection.insert_one({
        "username": username,
        "email":    email,
        "password": generate_password_hash(password)
    })
    return jsonify({"message": "User signed up successfully",
                    "username": username,
                    "email":    email}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid password'}), 401

    return jsonify({
        'message': 'Login successful',
        'username': user['username'],
        'email': user['email']
    }), 200


# ---------------------------------------------------------------------------
#  CHAT WITH GEMINI  (replace old /chat)
# ---------------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_text = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not user_text:
        return jsonify({"error": "Message is required"}), 400

    MODEL_ID = "gemini-2.0-flash"

    # Retrieve or start a chat session
    if session_id and session_id in chat_sessions:
        chat = chat_sessions.get(session_id)
        if not chat:
            chat = client.chats.create(model=MODEL_ID)
            session_id = str(uuid4())
            chat_sessions[session_id] = chat
    else:
        chat = client.chats.create(model=MODEL_ID)
        session_id = str(uuid4())
        chat_sessions[session_id] = chat

    # Send message to Gemini
    try:
        gemini_reply = chat.send_message(user_text)
        assistant_text = gemini_reply.text
    except Exception as err:
        return jsonify({"error": f"Gemini API error: {err}"}), 502

    return jsonify({
        "response": assistant_text,
        "session_id": session_id
    }), 200
    


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Never enable debug in production
    app.run(host="0.0.0.0", port=5000, debug=True)
