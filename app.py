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
PLAN_ENQUIRY_API_URL = os.getenv(
    "PLAN_ENQUIRY_API_URL",
    "http://127.0.0.1:8000/public/plan-enquiry",
)


@app.route("/")
def home():
    return render_template("index.html")


def _proxy_registration(api_url, data, profile_photo):
    files = {
        "profile_photo": (
            profile_photo.filename,
            profile_photo.stream,
            profile_photo.content_type,
        )
    }
    try:
        response = requests.post(api_url, data=data, files=files, timeout=30)
    except requests.RequestException:
        return jsonify({"success": False, "message": "Unable to connect to the registration service."}), 503

    try:
        response_data = response.json()
    except ValueError:
        response_data = {"detail": "Unexpected response from the registration service."}

    if response.status_code == 201:
        return jsonify({"success": True, "message": response_data.get("message", "Request completed successfully."), "result": response_data}), 201
    return jsonify({"success": False, "message": response_data.get("detail", "Registration failed.")}), response.status_code


@app.route("/register", methods=["POST"])
def register():
    selected_plan = request.form.get("plan_type", "TEST").strip().upper()
    organisation_name = request.form.get(
        "organisation_name",
        "",
    ).strip()
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    phone_number = request.form.get("phone_number", "").strip()
    preferred_contact = request.form.get("preferred_contact", "EMAIL").strip().upper()
    profile_photo = request.files.get("profile_photo")

    if selected_plan not in {"TEST", "BEGINNER", "PROFESSIONAL", "PREMIUM"}:
        return jsonify({"success": False, "message": "Please select a valid account plan."}), 400

    required = [organisation_name, full_name, email, profile_photo]
    if selected_plan == "TEST":
        required.append(password)
    else:
        required.append(phone_number)

    if not all(required):
        return jsonify(
            {
                "success": False,
                "message": (
                    "Please complete every required field for the selected plan."
                ),
            }
        ), 400

    if selected_plan == "TEST":
        data = {
            "organisation_name": organisation_name,
            "full_name": full_name,
            "email": email,
            "password": password,
        }
        return _proxy_registration(REGISTRATION_API_URL, data, profile_photo)

    data = {
        "plan_type": selected_plan,
        "organisation_name": organisation_name,
        "full_name": full_name,
        "email": email,
        "phone_number": phone_number,
        "preferred_contact": preferred_contact,
    }
    return _proxy_registration(PLAN_ENQUIRY_API_URL, data, profile_photo)


@app.route("/register-admin", methods=["POST"])
def register_admin_compatibility():
    """Keep old bookmarks/integrations working as a test registration."""
    return register()


if __name__ == "__main__":
    print(f"Test registration API: {REGISTRATION_API_URL}")
    print(f"Paid plan enquiry API: {PLAN_ENQUIRY_API_URL}")
    app.run(host="0.0.0.0", port=5002, debug=False)
