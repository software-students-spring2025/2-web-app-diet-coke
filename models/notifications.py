"""
Notification model for managing user and system notifications.
"""
import datetime
from bson import ObjectId
from .db import db


class Notification:
    """
    Provides methods for creating, retrieving, and updating notification status.
    Notifications include system messages, preference updates, and user interactions.
    """
    @staticmethod
    def create(user_id, notif_type, content, related_id=None):
        """
        Create a new notification for a user.
        """
        notification = {
            "user_id": ObjectId(user_id),
            "type": notif_type,
            "content": content,
            "related_id": related_id,
            "read": False,
            "created_at": datetime.datetime.now(),
        }

        result = db.notifications.insert_one(notification)
        notification["_id"] = result.inserted_id
        return notification

    @staticmethod
    def get_by_user_id(user_id):
        """
        Retrieve all notifications for a specific user.
        """
        notifications = list(
            db.notifications.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
        )

        return notifications

    @staticmethod
    def mark_as_read(notification_id):
        """
        Mark a specific notification as read.
        """
        result = db.notifications.update_one(
            {"_id": ObjectId(notification_id)}, {"$set": {"read": True}}
        )
        return result.modified_count > 0

    @staticmethod
    def mark_all_as_read(user_id):
        """
        Mark all unread notifications for a user as read.
        """
        result = db.notifications.update_many(
            {"user_id": ObjectId(user_id), "read": False}, {"$set": {"read": True}}
        )
        return result.modified_count
