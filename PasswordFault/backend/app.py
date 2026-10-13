"""
Password Fault Detector - Flask Application
============================================
Exposes a REST API for evaluating password strength.
Strictly ensures zero password logging for security and privacy.
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from password_checker import check_password_strength

app = Flask(__name__)

# Enable CORS for cross-origin requests from the standalone frontend
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/", methods=["GET"])
def index():
    """Root info endpoint to verify server status."""
    return jsonify({
        "status": "online",
        "service": "Password Fault Detector API",
        "endpoints": {
            "POST /check-password": "Send JSON payload {'password': '<your-password>'}"
        }
    })


@app.route("/check-password", methods=["POST"])
def check_password_endpoint():
    """
    POST endpoint to analyze password strength.

    Expected JSON body:
        {
            "password": "string"
        }

    Returns:
        JSON response with requirement status, score, and strength classification.

    Note:
        Passwords are never printed or written to server logs.
    """
    if not request.is_json:
        return (
            jsonify({
                "error": "Invalid request. Content-Type must be application/json."
            }),
            400,
        )

    data = request.get_json(silent=True)
    if data is None:
        return (
            jsonify({
                "error": "Malformed JSON payload provided."
            }),
            400,
        )

    # Validate presence of the password field
    if "password" not in data:
        return (
            jsonify({
                "error": "Missing 'password' field in JSON request."
            }),
            400,
        )

    password = data.get("password")
    if not isinstance(password, str):
        return (
            jsonify({
                "error": "The 'password' field must be a string."
            }),
            400,
        )

    # Analyze password (zero logging of the actual password string)
    analysis = check_password_strength(password)

    return jsonify(analysis), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug=True for development; ensure host is 127.0.0.1
    print(f"Password Fault Detector API running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
