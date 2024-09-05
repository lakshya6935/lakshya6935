from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from db import hotels_col, bookings_col
from utils.helpers import serialize_list, role_required

owner_bp = Blueprint("owner", __name__)


@owner_bp.route("/owner/hotels", methods=["GET"])
@role_required("owner")
def my_hotels():
    owner_id = get_jwt_identity()
    hotels = list(hotels_col.find({"owner_id": owner_id}).sort("created_at", -1))
    return jsonify({"success": True, "hotels": serialize_list(hotels)}), 200


@owner_bp.route("/owner/bookings", methods=["GET"])
@role_required("owner")
def my_hotel_bookings():
    owner_id = get_jwt_identity()
    hotel_ids = [str(h["_id"]) for h in hotels_col.find({"owner_id": owner_id}, {"_id": 1})]
    bookings = list(bookings_col.find({"hotel_id": {"$in": hotel_ids}}).sort("created_at", -1))
    return jsonify({"success": True, "bookings": serialize_list(bookings)}), 200


@owner_bp.route("/owner/stats", methods=["GET"])
@role_required("owner")
def owner_stats():
    owner_id = get_jwt_identity()
    hotel_ids = [str(h["_id"]) for h in hotels_col.find({"owner_id": owner_id}, {"_id": 1})]
    total_hotels = len(hotel_ids)
    total_bookings = bookings_col.count_documents({"hotel_id": {"$in": hotel_ids}})
    revenue_cursor = bookings_col.aggregate([
        {"$match": {"hotel_id": {"$in": hotel_ids}, "status": "confirmed"}},
        {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
    ])
    revenue_result = list(revenue_cursor)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0

    return jsonify({
        "success": True,
        "stats": {
            "total_hotels": total_hotels,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
        }
    }), 200
