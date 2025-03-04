"""User model for managing user data and authentication."""

import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from .db import db


class User(UserMixin):
    """Represents a user in the application."""

    def __init__(self, user_data):
        """Initialize a User instance with data retrived from database."""
        self.id = str(user_data.get("_id", ""))
        self.email = user_data.get("email", "")
        self.name = user_data.get("name", "")
        self.password_hash = user_data.get("password_hash", "")
        self.profile_picture = user_data.get("profile_picture", "")
        self.created_at = user_data.get("created_at", datetime.datetime.now())

    @staticmethod
    def get_by_id(user_id):
        """Find a user with their ID."""
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_email(email):
        """Find a user with their email."""
        user_data = db.users.find_one({"email": email})
        return User(user_data) if user_data else None

    @staticmethod
    def create_user(name, email, password):
        """Create a new user and save it to the database."""
        if db.users.find_one({"email": email}):
            return None

        user_data = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "profile_picture": "",
            "created_at": datetime.datetime.now(),
        }
        result = db.users.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return User(user_data)

    def check_password(self, password):
        """Check if the provided password matches the user's hashed password."""
        return check_password_hash(self.password_hash, password)
