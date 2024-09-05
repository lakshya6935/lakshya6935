from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from routes.auth_routes import auth_bp
from routes.hotel_routes import hotel_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp
from routes.owner_routes import owner_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
CORS(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(hotel_bp, url_prefix="/api")
app.register_blueprint(booking_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api")
app.register_blueprint(owner_bp, url_prefix="/api")


@app.route("/")
def index():
    return jsonify({
        "message": "StayLuxe Hotel Management System API is running.",
        "status": "ok"
    })


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"success": False, "message": "Session expired. Please log in again."}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"success": False, "message": "Invalid authentication token."}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"success": False, "message": "Authentication token is required."}), 401


if __name__ == "__main__":
    app.run(debug=True, port=Config.PORT)
