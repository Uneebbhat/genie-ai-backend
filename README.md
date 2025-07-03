# Genie AI Backend

This is the backend for Genie AI, a Flask-based REST API that provides user authentication, chat with Google Gemini, and user profile management. It uses MongoDB for data storage and integrates with the Google Gemini API for AI-powered chat.

---

## Features

- **User Signup & Login**: Secure authentication with hashed passwords.
- **Chat Endpoint**: Interact with Google Gemini via a RESTful API.
- **Profile Update**: Change username, email, or password.
- **MongoDB Integration**: Stores user data securely.
- **Environment-based Configuration**: Secrets and keys are loaded from environment variables.

---

## Requirements

- Python 3.8+
- MongoDB Atlas (or local MongoDB)
- Google Gemini API Key

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd backend
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   Create a `.env` file in the `backend` directory with the following content:

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGO_URI=your_mongodb_connection_string_here
   FLASK_DEBUG=True
   ```

   - Replace `your_gemini_api_key_here` with your actual Gemini API key.
   - Replace `your_mongodb_connection_string_here` with your MongoDB URI.

---

## Running the Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`.

---

## API Endpoints

### Signup

- **POST** `/signup`
- **Body:** `{ "username": "name", "email": "email", "password": "password" }`

### Login

- **POST** `/login`
- **Body:** `{ "email": "email", "password": "password" }`

### Chat

- **POST** `/chat`
- **Body:** `{ "message": "your message", "session_id": "optional-session-id" }`

### Update Profile

- **POST** `/update-profile`
- **Body:**
  - To update name or password:
    ```json
    { "email": "current_email", "name": "new_name", "password": "new_password" }
    ```
  - To update email:
    ```json
    { "email": "current_email", "new_email": "new_email" }
    ```

### Get All Users (for testing/admin)

- **GET** `/users`

---

## Notes

- **Security:** Never commit your real API keys or database URIs to version control.
- **Debug Mode:** Set `FLASK_DEBUG=False` in production.
- **Testing:** The `/users` endpoint is for testing/admin only. Remove or secure it before deploying.

---

## License

MIT

---

## Contact

For questions or support, please contact [Your Name] at [your.email@example.com].
