from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from bson import ObjectId
from datetime import datetime

from db import hotels_col, rooms_col
from utils.helpers import serialize_doc, serialize_list, role_required

hotel_bp = Blueprint("hotels", __name__)


@hotel_bp.route("/hotels", methods=["GET"])
def list_hotels():
    """Public endpoint - anyone (customer or guest) can browse approved hotels."""
    query = {"status": "approved"}

    city = request.args.get("city")
    if city:
        query["city"] = {"$regex": city, "$options": "i"}

    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    if min_price or max_price:
        price_filter = {}
        if min_price:
            price_filter["$gte"] = float(min_price)
        if max_price:
            price_filter["$lte"] = float(max_price)
        query["starting_price"] = price_filter

    search = request.args.get("search")
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"city": {"$regex": search, "$options": "i"}},
        ]

    hotels = list(hotels_col.find(query).sort("created_at", -1))
    return jsonify({"success": True, "hotels": serialize_list(hotels)}), 200


@hotel_bp.route("/hotels/<hotel_id>", methods=["GET"])
def get_hotel(hotel_id):
    try:
        hotel = hotels_col.find_one({"_id": ObjectId(hotel_id)})
    except Exception:
        return jsonify({"success": False, "message": "Invalid hotel id."}), 400

    if not hotel:
        return jsonify({"success": False, "message": "Hotel not found."}), 404

    rooms = list(rooms_col.find({"hotel_id": hotel_id}))
    hotel_data = serialize_doc(hotel)
    hotel_data["rooms"] = serialize_list(rooms)
    return jsonify({"success": True, "hotel": hotel_data}), 200


@hotel_bp.route("/hotels", methods=["POST"])
@role_required("owner", "admin")
def create_hotel():
    """Hotel owners add their hotel; admins can add directly as approved."""
    claims = get_jwt()
    owner_id = get_jwt_identity()
    data = request.get_json(force=True) or {}

    required = ["name", "city", "address", "description", "starting_price"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    hotel_doc = {
        "name": data["name"],
        "city": data["city"],
        "address": data["address"],
        "description": data["description"],
        "starting_price": float(data["starting_price"]),
        "amenities": data.get("amenities", []),
        "image": data.get("image", ""),
        "rating": data.get("rating", 4.5),
        "owner_id": owner_id,
        "status": "approved" if claims.get("role") == "admin" else "pending",
        "created_at": datetime.utcnow(),
    }
    result = hotels_col.insert_one(hotel_doc)
    return jsonify({
        "success": True,
        "message": "Hotel submitted." if hotel_doc["status"] == "pending" else "Hotel created.",
        "hotel_id": str(result.inserted_id)
    }), 201


@hotel_bp.route("/hotels/<hotel_id>", methods=["PUT"])
@role_required("owner", "admin")
def update_hotel(hotel_id):
    claims = get_jwt()
    owner_id = get_jwt_identity()
    data = request.get_json(force=True) or {}

    try:
        hotel = hotels_col.find_one({"_id": ObjectId(hotel_id)})
    except Exception:
        return jsonify({"success": False, "message": "Invalid hotel id."}), 400

    if not hotel:
        return jsonify({"success": False, "message": "Hotel not found."}), 404

    if claims.get("role") == "owner" and hotel.get("owner_id") != owner_id:
        return jsonify({"success": False, "message": "You do not own this hotel."}), 403

    allowed_fields = ["name", "city", "address", "description", "starting_price", "amenities", "image", "rating"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    if "starting_price" in update_data:
        update_data["starting_price"] = float(update_data["starting_price"])

    if claims.get("role") == "admin" and "status" in data:
        update_data["status"] = data["status"]

    hotels_col.update_one({"_id": ObjectId(hotel_id)}, {"$set": update_data})
    return jsonify({"success": True, "message": "Hotel updated."}), 200


@hotel_bp.route("/hotels/<hotel_id>", methods=["DELETE"])
@role_required("owner", "admin")
def delete_hotel(hotel_id):
    claims = get_jwt()
    owner_id = get_jwt_identity()

    try:
        hotel = hotels_col.find_one({"_id": ObjectId(hotel_id)})
    except Exception:
        return jsonify({"success": False, "message": "Invalid hotel id."}), 400

    if not hotel:
        return jsonify({"success": False, "message": "Hotel not found."}), 404

    if claims.get("role") == "owner" and hotel.get("owner_id") != owner_id:
        return jsonify({"success": False, "message": "You do not own this hotel."}), 403

    hotels_col.delete_one({"_id": ObjectId(hotel_id)})
    rooms_col.delete_many({"hotel_id": hotel_id})
    return jsonify({"success": True, "message": "Hotel deleted."}), 200


# ---------------- Rooms ----------------

@hotel_bp.route("/hotels/<hotel_id>/rooms", methods=["POST"])
@role_required("owner", "admin")
def add_room(hotel_id):
    claims = get_jwt()
    owner_id = get_jwt_identity()
    data = request.get_json(force=True) or {}

    try:
        hotel = hotels_col.find_one({"_id": ObjectId(hotel_id)})
    except Exception:
        return jsonify({"success": False, "message": "Invalid hotel id."}), 400

    if not hotel:
        return jsonify({"success": False, "message": "Hotel not found."}), 404

    if claims.get("role") == "owner" and hotel.get("owner_id") != owner_id:
        return jsonify({"success": False, "message": "You do not own this hotel."}), 403

    required = ["room_type", "price_per_night", "capacity", "total_rooms"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    room_doc = {
        "hotel_id": hotel_id,
        "room_type": data["room_type"],
        "price_per_night": float(data["price_per_night"]),
        "capacity": int(data["capacity"]),
        "total_rooms": int(data["total_rooms"]),
        "image": data.get("image", ""),
        "amenities": data.get("amenities", []),
        "created_at": datetime.utcnow(),
    }
    result = rooms_col.insert_one(room_doc)
    return jsonify({"success": True, "message": "Room added.", "room_id": str(result.inserted_id)}), 201


@hotel_bp.route("/rooms/<room_id>", methods=["DELETE"])
@role_required("owner", "admin")
def delete_room(room_id):
    try:
        rooms_col.delete_one({"_id": ObjectId(room_id)})
    except Exception:
        return jsonify({"success": False, "message": "Invalid room id."}), 400
    return jsonify({"success": True, "message": "Room deleted."}), 200
