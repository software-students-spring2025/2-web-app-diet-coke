"""
Model for travel preferences of a user.
"""
import datetime
from bson import ObjectId
from .db import db


class TravelPreference:
    """
    Model for handling user travel preferences.
    """
    @staticmethod
    def create_or_update(user_id, data):
        """
        Create or update a user's preferences.
        """
        preference = {
            "user_id": ObjectId(user_id),
            "budget": data.get("budget", ""),
            "travel_style": data.get("travel_style", ""),
            "arrival_time": data.get("arrival_time", ""),
            "food_preferences": data.get("food_preferences", []),
            "accommodation_type": data.get("accommodation_type", ""),
            "destination": data.get("destination", ""),
            "updated_at": datetime.datetime.now(),
        }

        existing = db.travel_preferences.find_one({"user_id": ObjectId(user_id)})

        if existing:
            db.travel_preferences.update_one(
                {"user_id": ObjectId(user_id)}, {"$set": preference}
            )
            preference["_id"] = existing["_id"]
        else:
            result = db.travel_preferences.insert_one(preference)
            preference["_id"] = result.inserted_id

        return preference

    @staticmethod
    def get_by_user_id(user_id):
        """
        Get a user's preferences by ID.
        """
        preference = db.travel_preferences.find_one({"user_id": ObjectId(user_id)})
        return preference

    @staticmethod
    def delete_by_user_id(user_id):
        """
        Delete a user's travel preferences.
        """
        result = db.travel_preferences.delete_one({"user_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @staticmethod
    def find_matches(user_id):
        """
        Find users with similar/matching preferences.
        """
        user_pref = db.travel_preferences.find_one({"user_id": ObjectId(user_id)})

        if not user_pref:
            return []

        query = {"user_id": {"$ne": ObjectId(user_id)}}

        if user_pref.get("budget"):
            query["budget"] = user_pref.get("budget")

        if user_pref.get("travel_style"):
            query["travel_style"] = user_pref.get("travel_style")

        if user_pref.get("destination"):
            query["destination"] = user_pref.get("destination")

        matches = list(db.travel_preferences.find(query))

        user_ids = [match["user_id"] for match in matches]
        user_details = list(db.users.find({"_id": {"$in": user_ids}}))

        result = []
        for user in user_details:
            user_pref = next((p for p in matches if p["user_id"] == user["_id"]), None)
            if user_pref:
                result.append(
                    {
                        "user": {
                            "id": str(user["_id"]),
                            "name": user["name"],
                            "profile_picture": user.get("profile_picture", ""),
                        },
                        "preferences": {
                            "budget": user_pref.get("budget", ""),
                            "travel_style": user_pref.get("travel_style", ""),
                            "food_preferences": user_pref.get("food_preferences", []),
                            "destination": user_pref.get("destination", ""),
                        },
                    }
                )

        return result

    @staticmethod
    def search_by_criteria(criteria):
        """Search for users based on specific criteria"""
        query = {}

        if criteria.get("budget"):
            query["budget"] = criteria.get("budget")

        if criteria.get("travel_style"):
            query["travel_style"] = criteria.get("travel_style")

        if criteria.get("destination"):
            query["destination"] = criteria.get("destination")

        if criteria.get("food_preferences"):
            query["food_preferences"] = {"$in": criteria.get("food_preferences")}

        preferences = list(db.travel_preferences.find(query))

        user_ids = [pref["user_id"] for pref in preferences]
        user_details = list(db.users.find({"_id": {"$in": user_ids}}))

        result = []
        for user in user_details:
            user_pref = next(
                (p for p in preferences if p["user_id"] == user["_id"]), None
            )
            if user_pref:
                result.append(
                    {
                        "user": {
                            "id": str(user["_id"]),
                            "name": user["name"],
                            "profile_picture": user.get("profile_picture", ""),
                        },
                        "preferences": {
                            "budget": user_pref.get("budget", ""),
                            "travel_style": user_pref.get("travel_style", ""),
                            "food_preferences": user_pref.get("food_preferences", []),
                            "destination": user_pref.get("destination", ""),
                        },
                    }
                )

        return result
