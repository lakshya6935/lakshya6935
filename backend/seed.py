"""
Run this script ONCE after setting up MongoDB to create:
  1. The default admin account (special hidden login)
  2. A sample hotel owner account
  3. A few sample hotels & rooms so the site isn't empty on first run

Usage:
    python seed.py
"""
from datetime import datetime
from werkzeug.security import generate_password_hash

from db import users_col, hotels_col, rooms_col
from config import Config


def seed_admin():
    existing = users_col.find_one({"role": "admin"})
    if existing:
        print(f"[skip] Admin already exists: {existing['email']}")
        return

    users_col.insert_one({
        "name": "System Administrator",
        "email": Config.DEFAULT_ADMIN_EMAIL,
        "phone": "",
        "password": generate_password_hash(Config.DEFAULT_ADMIN_PASSWORD),
        "role": "admin",
        "status": "active",
        "created_at": datetime.utcnow(),
    })
    print(f"[created] Admin account -> email: {Config.DEFAULT_ADMIN_EMAIL} | password: {Config.DEFAULT_ADMIN_PASSWORD}")
    print("          IMPORTANT: change this password after first login in a real deployment.")


def seed_sample_owner_and_hotels():
    owner = users_col.find_one({"email": "owner@stayluxe.com"})
    if not owner:
        result = users_col.insert_one({
            "name": "Rajesh Sharma",
            "email": "owner@stayluxe.com",
            "phone": "9876543210",
            "password": generate_password_hash("Owner@123"),
            "role": "owner",
            "status": "active",
            "created_at": datetime.utcnow(),
        })
        owner_id = str(result.inserted_id)
        print("[created] Sample owner -> email: owner@stayluxe.com | password: Owner@123")
    else:
        owner_id = str(owner["_id"])
        print("[skip] Sample owner already exists.")

    if hotels_col.count_documents({}) > 0:
        print("[skip] Hotels already seeded.")
        return

    sample_hotels = [
        {
            "name": "The Pink Pearl Palace",
            "city": "Jaipur",
            "address": "MI Road, Jaipur, Rajasthan",
            "description": "A royal heritage hotel in the heart of the Pink City, blending Rajasthani architecture with modern luxury.",
            "starting_price": 3499,
            "amenities": ["Free WiFi", "Swimming Pool", "Spa", "Rooftop Restaurant", "Parking"],
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80",
            "rating": 4.7,
            "owner_id": owner_id,
            "status": "approved",
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Ocean Breeze Resort",
            "city": "Goa",
            "address": "Calangute Beach Road, Goa",
            "description": "Beachfront resort with stunning sea views, perfect for a relaxing tropical getaway.",
            "starting_price": 4999,
            "amenities": ["Private Beach", "Free WiFi", "Bar", "Swimming Pool", "Gym"],
            "image": "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=1000&q=80",
            "rating": 4.5,
            "owner_id": owner_id,
            "status": "approved",
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Himalayan Mist Retreat",
            "city": "Manali",
            "address": "Old Manali, Himachal Pradesh",
            "description": "Cozy mountain retreat surrounded by pine forests with breathtaking Himalayan views.",
            "starting_price": 2799,
            "amenities": ["Bonfire", "Free WiFi", "Mountain View", "Restaurant", "Parking"],
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=1000&q=80",
            "rating": 4.6,
            "owner_id": owner_id,
            "status": "approved",
            "created_at": datetime.utcnow(),
        },
        {
            "name": "Urban Sky Business Hotel",
            "city": "Mumbai",
            "address": "Bandra Kurla Complex, Mumbai",
            "description": "Modern business hotel with skyline views, ideal for corporate travelers.",
            "starting_price": 5999,
            "amenities": ["Free WiFi", "Conference Rooms", "Gym", "Rooftop Bar", "Airport Shuttle"],
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=1000&q=80",
            "rating": 4.4,
            "owner_id": owner_id,
            "status": "approved",
            "created_at": datetime.utcnow(),
        },
    ]

    inserted = hotels_col.insert_many(sample_hotels)
    print(f"[created] {len(inserted.inserted_ids)} sample hotels.")

    room_templates = [
        {"room_type": "Deluxe Room", "price_multiplier": 1.0, "capacity": 2, "total_rooms": 10,
         "image": "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80"},
        {"room_type": "Executive Suite", "price_multiplier": 1.6, "capacity": 3, "total_rooms": 5,
         "image": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80"},
        {"room_type": "Family Room", "price_multiplier": 1.3, "capacity": 4, "total_rooms": 6,
         "image": "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=800&q=80"},
    ]

    for hotel_id, hotel in zip(inserted.inserted_ids, sample_hotels):
        for template in room_templates:
            rooms_col.insert_one({
                "hotel_id": str(hotel_id),
                "room_type": template["room_type"],
                "price_per_night": round(hotel["starting_price"] * template["price_multiplier"], 2),
                "capacity": template["capacity"],
                "total_rooms": template["total_rooms"],
                "image": template["image"],
                "amenities": ["AC", "TV", "Free WiFi", "Room Service"],
                "created_at": datetime.utcnow(),
            })

    print("[created] Sample rooms for each hotel.")


if __name__ == "__main__":
    seed_admin()
    seed_sample_owner_and_hotels()
    print("\nSeeding complete.")
