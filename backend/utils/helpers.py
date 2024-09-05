from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from bson import ObjectId


def serialize_doc(doc):
    """Convert a MongoDB document into a JSON-serializable dict."""
    if doc is None:
        return None
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc


def serialize_list(cursor):
    return [serialize_doc(doc) for doc in cursor]


def role_required(*allowed_roles):
    """Decorator to restrict an endpoint to specific JWT roles (admin/owner/customer)."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                return jsonify({"success": False, "message": "Access denied. Insufficient permissions."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
