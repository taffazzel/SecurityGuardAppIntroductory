import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import requests


load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

REGISTRATION_API_URL = os.getenv(
    "REGISTRATION_API_URL",
    "http://127.0.0.1:8000/public/register-admin",
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register-admin", methods=["POST"])
def register_admin():
    organisation_name = request.form.get(
        "organisation_name",
        "",
    ).strip()
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    profile_photo = request.files.get("profile_photo")

    if not all(
        [
            organisation_name,
            full_name,
            email,
            password,
            profile_photo,
        ]
    ):
        return jsonify(
            {
                "success": False,
                "message": (
                    "Organisation name, full name, email, password "
                    "and profile photo are required."
                ),
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
        "organisation_name": organisation_name,
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
                "message": (
                    "Organisation and admin account created successfully."
                ),
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
    print(f"Registration API: {REGISTRATION_API_URL}")
    app.run(host="0.0.0.0", port=5002, debug=False)
