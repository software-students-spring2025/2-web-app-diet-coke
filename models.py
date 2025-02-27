from flask_login import UserMixin
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# load environment variables
load_dotenv()

# configure MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["travel_match_db"]

# collections
users_collection = db["users"]
preferences_collection = db["preferences"]
matches_collection = db["matches"]

class User(UserMixin):
    """User model for Flask-Login authentication."""
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.password_hash = user_data["password"]

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get(user_id):
        """Fetch user from database by ID."""
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_username(username):
        """Fetch user from database by username."""
        user_data = users_collection.find_one({"username": username})
        return User(user_data) if user_data else None

    @staticmethod
    def create(username, email, password):
        """Create a new user with hashed password."""
        if users_collection.find_one({"username": username}):
            return None  # Username already exists
        password_hash = generate_password_hash(password)
        user_id = users_collection.insert_one({
            "username": username,
            "email": email,
            "password": password_hash
        }).inserted_id
        return User.get(user_id)

class Preferences:
    """User preferences for travel match filtering."""
    @staticmethod
    def set_preferences(user_id, destination, budget, travel_style):
        """Set or update user preferences."""
        preferences_collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {
                "destination": destination,
                "budget": budget,
                "travel_style": travel_style
            }},
            upsert=True
        )

    @staticmethod
    def get_preferences(user_id):
        """Get user preferences."""
        return preferences_collection.find_one({"user_id": ObjectId(user_id)})

class Matches:
    """Find potential travel matches based on preferences."""
    @staticmethod
    def find_matches(user_id):
        """Find users with similar travel preferences."""
        user_prefs = Preferences.get_preferences(user_id)
        if not user_prefs:
            return []

        # find users with matching preferences
        matches = users_collection.find({
            "_id": {"$ne": ObjectId(user_id)},  # exclude current user
            "destination": user_prefs["destination"]
        })

        return [{"username": match["username"], "id": str(match["_id"])} for match in matches]
