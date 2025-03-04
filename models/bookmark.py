"""
Bookmark model for managing user bookmarks.
"""
from bson import ObjectId
from .db import db


class Bookmark:
    """
    Provides methods for adding, removing, and retrieving bookmarked user profiles.
    Bookmarks allow users to save potential travel partners for future reference.
    """
    @staticmethod
    def add(user_id, bookmarked_user_id):
        """
        Add a bookmark for a user.
        """
        bookmark = {
            "user_id": ObjectId(user_id),
            "bookmarked_user_id": ObjectId(bookmarked_user_id),
        }
        db.bookmarks.insert_one(bookmark)
        return bookmark

    @staticmethod
    def remove(user_id, bookmarked_user_id):
        """
        Remove bookmark.
        """
        db.bookmarks.delete_one(
            {
                "user_id": ObjectId(user_id),
                "bookmarked_user_id": ObjectId(bookmarked_user_id),
            }
        )

    @staticmethod
    def get_by_user(user_id):
        """
        Find user boomarks by ID.
        """
        bookmarks = db.bookmarks.find({"user_id": ObjectId(user_id)})
        bookmarked_user_ids = [b["bookmarked_user_id"] for b in bookmarks]
        users = db.users.find({"_id": {"$in": bookmarked_user_ids}})
        return list(users)
