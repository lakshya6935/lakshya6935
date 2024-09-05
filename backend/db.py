from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

# Collections
users_col = db["users"]           # customers, owners, admin
hotels_col = db["hotels"]         # hotel listings (owned by an owner)
rooms_col = db["rooms"]           # rooms belonging to a hotel
bookings_col = db["bookings"]     # bookings made by customers
