from bson import ObjectId
from .db import db


class Bookmark:
    @staticmethod
    def add(user_id, bookmarked_user_id):
        bookmark = {
            "user_id": ObjectId(user_id),
            "bookmarked_user_id": ObjectId(bookmarked_user_id),
        }
        db.bookmarks.insert_one(bookmark)
        return bookmark

    @staticmethod
    def remove(user_id, bookmarked_user_id):
        db.bookmarks.delete_one(
            {
                "user_id": ObjectId(user_id),
                "bookmarked_user_id": ObjectId(bookmarked_user_id),
            }
        )

    @staticmethod
    def get_by_user(user_id):
        bookmarks = db.bookmarks.find({"user_id": ObjectId(user_id)})
        bookmarked_user_ids = [b["bookmarked_user_id"] for b in bookmarks]
        users = db.users.find({"_id": {"$in": bookmarked_user_ids}})
        return list(users)
