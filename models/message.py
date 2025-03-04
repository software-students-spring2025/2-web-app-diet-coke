"""Message model for sending and retrieving user messages."""

import datetime
from bson import ObjectId
from .db import db


class Message:
    """Represents a message in the application."""

    @staticmethod
    def send(sender_id, recipient_id, content):
        """Send a message from user ID to receipient ID."""
        message = {
            "sender_id": ObjectId(sender_id),
            "recipient_id": ObjectId(recipient_id),
            "content": content,
            "created_at": datetime.datetime.now(),
        }
        db.messages.insert_one(message)
        return message

    @staticmethod
    def get_conversation(user1_id, user2_id):
        """Retrieve messages between two user IDs."""
        messages = db.messages.find(
            {
                "$or": [
                    {
                        "sender_id": ObjectId(user1_id),
                        "recipient_id": ObjectId(user2_id),
                    },
                    {
                        "sender_id": ObjectId(user2_id),
                        "recipient_id": ObjectId(user1_id),
                    },
                ]
            }
        ).sort("created_at", 1)
        return list(messages)

    @staticmethod
    def get_conversations(user_id):
        """Retrieve all messages sent and received by a specific user ID."""
        sent_to = db.messages.distinct("recipient_id", {"sender_id": ObjectId(user_id)})
        received_from = db.messages.distinct(
            "sender_id", {"recipient_id": ObjectId(user_id)}
        )
        user_ids = list(set(sent_to + received_from))

        conversations = []
        for other_user_id in user_ids:
            latest_message = db.messages.find_one(
                {
                    "$or": [
                        {"sender_id": ObjectId(user_id), "recipient_id": other_user_id},
                        {"sender_id": other_user_id, "recipient_id": ObjectId(user_id)},
                    ]
                },
                sort=[("created_at", -1)],
            )

            other_user = db.users.find_one({"_id": other_user_id})
            if latest_message and other_user:
                conversations.append(
                    {
                        "user": {
                            "id": str(other_user["_id"]),
                            "name": other_user["name"],
                            "profile_picture": other_user.get("profile_picture", ""),
                        },
                        "latest_message": latest_message["content"],
                    }
                )

        return conversations
