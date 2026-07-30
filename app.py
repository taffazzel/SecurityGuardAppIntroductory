from flask import Flask, render_template, request, jsonify
import requests


app = Flask(__name__)

REGISTRATION_API_URL = "http://127.0.0.1:7001/public/register-admin"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register-admin", methods=["POST"])
def register_admin():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    profile_photo = request.files.get("profile_photo")

    if not all([full_name, email, password, profile_photo]):
        return jsonify(
            {
                "success": False,
                "message": "All fields are required.",
            }
        ), 400

    files = {
        "profile_photo": (
            profile_photo.filename,
            profile_photo.stream,
            profile_photo.content_type,
        )
    }

    data = {
        "full_name": full_name,
        "email": email,
        "password": password,
    }

    try:
        response = requests.post(
            REGISTRATION_API_URL,
            data=data,
            files=files,
            timeout=30,
        )
    except requests.RequestException:
        return jsonify(
            {
                "success": False,
                "message": "Unable to connect to the registration service.",
            }
        ), 503

    try:
        response_data = response.json()
    except ValueError:
        response_data = {
            "detail": "Unexpected response from the registration service."
        }

    if response.status_code == 201:
        return jsonify(
            {
                "success": True,
                "message": "Admin account created successfully.",
                "user": response_data,
            }
        ), 201

    return jsonify(
        {
            "success": False,
            "message": response_data.get(
                "detail",
                "Registration failed.",
            ),
        }
    ), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
