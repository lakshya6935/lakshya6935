from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from db import bookings_col, hotels_col, rooms_col
from utils.helpers import serialize_doc, serialize_list, role_required

booking_bp = Blueprint("bookings", __name__)


@booking_bp.route("/bookings", methods=["POST"])
@role_required("customer")
def create_booking():
    customer_id = get_jwt_identity()
    claims = get_jwt()
    data = request.get_json(force=True) or {}

    required = ["hotel_id", "room_id", "check_in", "check_out", "guests"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        hotel = hotels_col.find_one({"_id": ObjectId(data["hotel_id"])})
        room = rooms_col.find_one({"_id": ObjectId(data["room_id"])})
    except Exception:
        return jsonify({"success": False, "message": "Invalid hotel or room id."}), 400

    if not hotel or not room:
        return jsonify({"success": False, "message": "Hotel or room not found."}), 404

    try:
        check_in = datetime.strptime(data["check_in"], "%Y-%m-%d")
        check_out = datetime.strptime(data["check_out"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "message": "Dates must be in YYYY-MM-DD format."}), 400

    nights = (check_out - check_in).days
    if nights <= 0:
        return jsonify({"success": False, "message": "Check-out date must be after check-in date."}), 400

    total_price = nights * float(room["price_per_night"])

    booking_doc = {
        "customer_id": customer_id,
        "customer_name": claims.get("name"),
        "customer_email": claims.get("email"),
        "hotel_id": data["hotel_id"],
        "hotel_name": hotel["name"],
        "room_id": data["room_id"],
        "room_type": room["room_type"],
        "check_in": data["check_in"],
        "check_out": data["check_out"],
        "nights": nights,
        "guests": int(data["guests"]),
        "price_per_night": room["price_per_night"],
        "total_price": total_price,
        "status": "confirmed",
        "created_at": datetime.utcnow(),
    }
    result = bookings_col.insert_one(booking_doc)
    booking_doc["_id"] = result.inserted_id

    return jsonify({
        "success": True,
        "message": "Booking confirmed!",
        "booking": serialize_doc(booking_doc)
    }), 201


@booking_bp.route("/bookings/my", methods=["GET"])
@role_required("customer")
def my_bookings():
    customer_id = get_jwt_identity()
    bookings = list(bookings_col.find({"customer_id": customer_id}).sort("created_at", -1))
    return jsonify({"success": True, "bookings": serialize_list(bookings)}), 200


@booking_bp.route("/bookings/<booking_id>/cancel", methods=["PUT"])
@role_required("customer")
def cancel_booking(booking_id):
    customer_id = get_jwt_identity()
    try:
        booking = bookings_col.find_one({"_id": ObjectId(booking_id)})
    except Exception:
        return jsonify({"success": False, "message": "Invalid booking id."}), 400

    if not booking or booking.get("customer_id") != customer_id:
        return jsonify({"success": False, "message": "Booking not found."}), 404

    bookings_col.update_one({"_id": ObjectId(booking_id)}, {"$set": {"status": "cancelled"}})
    return jsonify({"success": True, "message": "Booking cancelled."}), 200


@booking_bp.route("/bookings/hotel/<hotel_id>", methods=["GET"])
@role_required("owner", "admin")
def hotel_bookings(hotel_id):
    bookings = list(bookings_col.find({"hotel_id": hotel_id}).sort("created_at", -1))
    return jsonify({"success": True, "bookings": serialize_list(bookings)}), 200
