from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta, datetime

from db import users_col
from utils.helpers import serialize_doc
from config import Config

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Public registration endpoint.
    Only 'customer' and 'owner' roles may self-register.
    The 'admin' role can NEVER be created through this endpoint -
    it is seeded separately and logs in through a dedicated hidden route.
    """
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "customer").strip().lower()
    phone = (data.get("phone") or "").strip()

    if role not in ("customer", "owner"):
        return jsonify({"success": False, "message": "Invalid role for registration."}), 400

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email and password are required."}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    if users_col.find_one({"email": email}):
        return jsonify({"success": False, "message": "An account with this email already exists."}), 409

    user_doc = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": generate_password_hash(password),
        "role": role,
        "status": "active" if role == "customer" else "pending",  # owners require admin approval
        "created_at": datetime.utcnow(),
    }
    result = users_col.insert_one(user_doc)

    message = "Registration successful. You can now log in."
    if role == "owner":
        message = "Registration successful. Your hotel-owner account is pending admin approval."

    return jsonify({
        "success": True,
        "message": message,
        "user_id": str(result.inserted_id)
    }), 201


def _do_login(expected_role):
    """Shared login logic; expected_role restricts who may use this specific login endpoint."""
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = users_col.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    if user.get("role") != expected_role:
        return jsonify({"success": False, "message": "This login is not available for your account type."}), 403

    if expected_role == "owner" and user.get("status") == "pending":
        return jsonify({"success": False, "message": "Your hotel-owner account is still pending admin approval."}), 403

    if user.get("status") == "blocked":
        return jsonify({"success": False, "message": "Your account has been blocked. Contact support."}), 403

    token = create_access_token(
        identity=str(user["_id"]),
        additional_claims={"role": user["role"], "email": user["email"], "name": user["name"]},
        expires_delta=timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS),
    )

    safe_user = serialize_doc(user)
    safe_user.pop("password", None)

    return jsonify({"success": True, "message": "Login successful.", "token": token, "user": safe_user}), 200


@auth_bp.route("/login/customer", methods=["POST"])
def login_customer():
    return _do_login("customer")


@auth_bp.route("/login/owner", methods=["POST"])
def login_owner():
    return _do_login("owner")


@auth_bp.route("/login/admin", methods=["POST"])
def login_admin():
    """Dedicated, hidden login route for the admin. Not linked anywhere in the public UI."""
    return _do_login("admin")
