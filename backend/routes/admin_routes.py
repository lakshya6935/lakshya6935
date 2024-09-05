from flask import Blueprint, request, jsonify
from bson import ObjectId

from db import users_col, hotels_col, bookings_col
from utils.helpers import serialize_doc, serialize_list, role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/stats", methods=["GET"])
@role_required("admin")
def stats():
    total_customers = users_col.count_documents({"role": "customer"})
    total_owners = users_col.count_documents({"role": "owner", "status": {"$ne": "pending"}})
    pending_owners = users_col.count_documents({"role": "owner", "status": "pending"})
    total_hotels = hotels_col.count_documents({"status": "approved"})
    pending_hotels = hotels_col.count_documents({"status": "pending"})
    total_bookings = bookings_col.count_documents({})
    revenue_cursor = bookings_col.aggregate([
        {"$match": {"status": "confirmed"}},
        {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
    ])
    revenue_result = list(revenue_cursor)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0

    return jsonify({
        "success": True,
        "stats": {
            "total_customers": total_customers,
            "total_owners": total_owners,
            "pending_owners": pending_owners,
            "total_hotels": total_hotels,
            "pending_hotels": pending_hotels,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
        }
    }), 200


@admin_bp.route("/admin/users", methods=["GET"])
@role_required("admin")
def list_users():
    role = request.args.get("role")
    query = {}
    if role:
        query["role"] = role
    users = list(users_col.find(query).sort("created_at", -1))
    safe_users = serialize_list(users)
    for u in safe_users:
        u.pop("password", None)
    return jsonify({"success": True, "users": safe_users}), 200


@admin_bp.route("/admin/users/<user_id>/status", methods=["PUT"])
@role_required("admin")
def update_user_status(user_id):
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("active", "blocked", "pending"):
        return jsonify({"success": False, "message": "Invalid status."}), 400

    try:
        result = users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"status": new_status}})
    except Exception:
        return jsonify({"success": False, "message": "Invalid user id."}), 400

    if result.matched_count == 0:
        return jsonify({"success": False, "message": "User not found."}), 404

    return jsonify({"success": True, "message": f"User status updated to {new_status}."}), 200


@admin_bp.route("/admin/users/<user_id>", methods=["DELETE"])
@role_required("admin")
def delete_user(user_id):
    try:
        result = users_col.delete_one({"_id": ObjectId(user_id), "role": {"$ne": "admin"}})
    except Exception:
        return jsonify({"success": False, "message": "Invalid user id."}), 400

    if result.deleted_count == 0:
        return jsonify({"success": False, "message": "User not found or cannot be deleted."}), 404

    return jsonify({"success": True, "message": "User deleted."}), 200


@admin_bp.route("/admin/hotels", methods=["GET"])
@role_required("admin")
def list_all_hotels():
    status = request.args.get("status")
    query = {}
    if status:
        query["status"] = status
    hotels = list(hotels_col.find(query).sort("created_at", -1))
    return jsonify({"success": True, "hotels": serialize_list(hotels)}), 200


@admin_bp.route("/admin/hotels/<hotel_id>/status", methods=["PUT"])
@role_required("admin")
def update_hotel_status(hotel_id):
    data = request.get_json(force=True) or {}
    new_status = data.get("status")
    if new_status not in ("approved", "pending", "rejected"):
        return jsonify({"success": False, "message": "Invalid status."}), 400

    try:
        result = hotels_col.update_one({"_id": ObjectId(hotel_id)}, {"$set": {"status": new_status}})
    except Exception:
        return jsonify({"success": False, "message": "Invalid hotel id."}), 400

    if result.matched_count == 0:
        return jsonify({"success": False, "message": "Hotel not found."}), 404

    return jsonify({"success": True, "message": f"Hotel status updated to {new_status}."}), 200


@admin_bp.route("/admin/bookings", methods=["GET"])
@role_required("admin")
def all_bookings():
    bookings = list(bookings_col.find({}).sort("created_at", -1))
    return jsonify({"success": True, "bookings": serialize_list(bookings)}), 200
