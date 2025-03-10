"""
Travel Match Web App and API Endpoints
"""

import os
import json
import datetime
from flask import Flask, request, jsonify, render_template, abort, redirect
from flask_cors import CORS
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from models import User, Notification, TravelPreference, Bookmark, Message

# Load environment variables
load_dotenv()


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB ObjectId and datetime objects."""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


# Initialize Flask app
app = Flask(__name__)
app.json_encoder = JSONEncoder
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

# Enable CORS
CORS(app)

# Configure MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client.travel_match_db

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# Routes
@app.route("/api/hello_world", methods=["GET"])
def health_check():
    """Health check endpoint to verify API is running"""
    return jsonify({"status": "success", "message": "API is running"})


# Route to serve HTML templates
@app.route("/", defaults={"page_name": "index"})
@app.route("/<page_name>")
def serve_page(page_name):
    """
    Serve HTML templates based on the page name
    This allows for dynamic routing to any template
    """
    # For root route, redirect logged-in users to profile page
    if page_name == "index" and current_user.is_authenticated:
        return redirect("/profile")

    # List of valid pages (add more as needed) #TODO: Add more pages
    valid_pages = [
        "index",
        "login",
        "register",
        "profile",
        "preferences",
        "matches",
        "messages",
        "notifications",
        "bookmarks",
    ]

    # Check if the requested page exists
    if page_name not in valid_pages:
        abort(404)

    try:
        # Set active page for navigation highlighting
        return render_template(f"{page_name}.html", active_page=page_name)
    except Exception as e:
        # If template doesn't exist, return 404
        app.logger.error("Error: %s", str(e))
        abort(404)


@app.route("/profile/<user_id>")
def user_profile(user_id):
    """
    Serve a specific user's profile page
    """
    try:
        user = User.get_by_id(user_id)

        if not user:
            abort(404)

        return render_template(
            "user_profile.html",
            user=user,
            active_page="profile",
        )
    except Exception as e:
        app.logger.error("Error serving user profile for %s: %s", user_id, str(e))
        abort(404)


@app.route("/messages/<user_id>")
@login_required
def view_messages(user_id):
    """
    Serve the message view page for a specific user
    """
    try:
        # Convert user_id to ObjectId for MongoDB query
        user_id_obj = ObjectId(user_id)
        # Return the message view template with the user_id
        return render_template(
            "message_view.html",
            user_id=user_id,
            current_user=current_user,
            active_page="messages",
        )
    except Exception as e:
        app.logger.error(f"Error serving messages for {user_id}: {str(e)}")
        abort(404)


@app.route("/messages")
@login_required
def messages_dashboard():
    """
    Serve the messages dashboard page showing all conversations
    """
    return render_template("messages.html", active_page="messages")


# Authentication routes
@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Validate required fields
    required_fields = ["name", "email", "password"]
    for field in required_fields:
        if field not in data:
            return (
                jsonify(
                    {"status": "error", "message": f"Missing required field: {field}"}
                ),
                400,
            )

    # Check if user already exists
    if User.get_by_email(data["email"]):
        return jsonify({"status": "error", "message": "Email already registered"}), 409

    # Create user
    user = User.create_user(data["name"], data["email"], data["password"])
    if not user:
        return jsonify({"status": "error", "message": "Failed to create user"}), 500

    # Create welcome notification
    Notification.create(
        user.id,
        "welcome",
        "Welcome to Travel Match! Complete your profile to get started.",
    )

    # Login the user
    login_user(user)

    # Return success response
    return (
        jsonify(
            {
                "status": "success",
                "message": "User registered successfully",
                "user": {"id": user.id, "name": user.name, "email": user.email},
            }
        ),
        201,
    )


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login a user"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Validate required fields
    required_fields = ["email", "password"]
    for field in required_fields:
        if field not in data:
            return (
                jsonify(
                    {"status": "error", "message": f"Missing required field: {field}"}
                ),
                400,
            )

    # Find user by email
    user = User.get_by_email(data["email"])
    if not user:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Check password
    if not user.check_password(data["password"]):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    # Login the user
    login_user(user)

    # Return success response
    return (
        jsonify(
            {
                "status": "success",
                "message": "Logged in successfully",
                "user": {"id": user.id, "name": user.name, "email": user.email},
            }
        ),
        200,
    )


@app.route("/api/auth/logout")
@login_required
def logout():
    """
    Log out the current user by removing their session.
    """
    logout_user()
    return jsonify({"status": "success", "message": "Logged out successfully!"})


@app.route("/logout")
@login_required
def logout_page():
    """
    Logout page that redirects to login page after logging out
    """
    logout_user()
    return redirect("/login")


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template("500.html"), 500


# User Profile Routes
@app.route("/api/users/profile", methods=["GET"])
@login_required
def get_user_profile():
    """Get current user's profile"""
    # Get user profile data
    user_profile = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "profile_picture": current_user.profile_picture,
        "created_at": current_user.created_at,
    }

    # Get travel preferences if they exist
    preferences = TravelPreference.get_by_user_id(current_user.id)
    if preferences:
        user_profile["preferences"] = {
            "budget": preferences.get("budget", ""),
            "travel_style": preferences.get("travel_style", ""),
            "food_preferences": preferences.get("food_preferences", []),
            "accommodation_type": preferences.get("accommodation_type", ""),
            "destination": preferences.get("destination", ""),
            "arrival_time": preferences.get("arrival_time", ""),
        }

    return jsonify({"status": "success", "data": user_profile})


@app.route("/api/users/profile", methods=["PUT"])
@login_required
def update_user_profile():
    """Update current user's profile"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Fields that can be updated
    allowed_fields = ["name", "profile_picture"]
    update_data = {}

    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]

    if not update_data:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    # Update the user in database
    db.users.update_one({"_id": ObjectId(current_user.id)}, {"$set": update_data})

    # Return updated profile
    updated_user = db.users.find_one({"_id": ObjectId(current_user.id)})

    return jsonify(
        {
            "status": "success",
            "message": "Profile updated successfully",
            "data": {
                "id": str(updated_user["_id"]),
                "name": updated_user.get("name", ""),
                "email": updated_user.get("email", ""),
                "profile_picture": updated_user.get("profile_picture", ""),
            },
        }
    )


@app.route("/api/users/profile", methods=["DELETE"])
@login_required
def delete_user_profile():
    """Delete current user's account"""
    user_id = current_user.id

    # Remove user preferences
    TravelPreference.delete_by_user_id(user_id)

    # Delete bookmarks
    db.bookmarks.delete_many({"user_id": ObjectId(user_id)})
    db.bookmarks.delete_many({"bookmarked_user_id": ObjectId(user_id)})

    # Delete notifications
    db.notifications.delete_many({"user_id": ObjectId(user_id)})

    # Delete messages
    db.messages.delete_many({"sender_id": ObjectId(user_id)})
    db.messages.delete_many({"recipient_id": ObjectId(user_id)})

    # Delete user
    result = db.users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Logout user
    logout_user()

    return jsonify({"status": "success", "message": "Account deleted successfully"})


@app.route("/api/users/public/<user_id>", methods=["GET"])
@login_required
def get_public_user_profile(user_id):
    """
    Get a specific user's public profile data.
    """
    try:
        # Convert string ID to ObjectId
        user_id_obj = ObjectId(user_id)

        # Find user by ID
        user = db.users.find_one({"_id": user_id_obj})

        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        # Get preferences using TravelPreference model
        preferences = TravelPreference.get_by_user_id(user_id)

        # Prepare public user data
        user_data = {"id": str(user["_id"]), "name": user["name"], "preferences": None}

        # Add preferences data if available
        if preferences:
            user_data["preferences"] = {
                "destination": preferences.get("destination"),
                "budget": preferences.get("budget"),
                "travel_style": preferences.get("travel_style"),
                "food_preferences": preferences.get("food_preferences"),
                "accommodation_type": preferences.get("accommodation_type"),
                "arrival_time": preferences.get("arrival_time"),
            }

        return jsonify({"status": "success", "data": user_data}), 200

    except Exception as e:
        app.logger.error(f"Error fetching user profile: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Error retrieving user profile: {str(e)}",
                }
            ),
            500,
        )


# Travel Preferences Routes
@app.route("/api/preferences", methods=["GET"])
@login_required
def get_preferences():
    """Get current user's travel preferences"""
    preferences = TravelPreference.get_by_user_id(current_user.id)

    if not preferences:
        return jsonify({"status": "success", "data": None})

    # Format preferences for response
    formatted_preferences = {
        "id": str(preferences["_id"]),
        "budget": preferences.get("budget", ""),
        "travel_style": preferences.get("travel_style", ""),
        "food_preferences": preferences.get("food_preferences", []),
        "accommodation_type": preferences.get("accommodation_type", ""),
        "destination": preferences.get("destination", ""),
        "arrival_time": preferences.get("arrival_time", ""),
        "updated_at": preferences.get("updated_at"),
    }

    return jsonify({"status": "success", "data": formatted_preferences})


@app.route("/api/preferences", methods=["POST"])
@login_required
def create_preferences():
    """Create travel preferences for current user"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Create or update preferences
    preferences = TravelPreference.create_or_update(current_user.id, data)

    # Create notification
    Notification.create(
        current_user.id, "preferences", "Your travel preferences have been updated."
    )

    # Format preferences for response
    formatted_preferences = {
        "id": str(preferences["_id"]),
        "budget": preferences.get("budget", ""),
        "travel_style": preferences.get("travel_style", ""),
        "food_preferences": preferences.get("food_preferences", []),
        "accommodation_type": preferences.get("accommodation_type", ""),
        "destination": preferences.get("destination", ""),
        "arrival_time": preferences.get("arrival_time", ""),
        "updated_at": preferences.get("updated_at"),
    }

    return (
        jsonify(
            {
                "status": "success",
                "message": "Preferences created successfully",
                "data": formatted_preferences,
            }
        ),
        201,
    )


@app.route("/api/preferences", methods=["PUT"])
@login_required
def update_preferences():
    """Update current user's travel preferences"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Check if preferences exist
    existing = TravelPreference.get_by_user_id(current_user.id)
    if not existing:
        return jsonify({"status": "error", "message": "Preferences not found"}), 404

    # Update preferences
    preferences = TravelPreference.create_or_update(current_user.id, data)

    # Create notification
    Notification.create(
        current_user.id, "preferences", "Your travel preferences have been updated."
    )

    # Format preferences for response
    formatted_preferences = {
        "id": str(preferences["_id"]),
        "budget": preferences.get("budget", ""),
        "travel_style": preferences.get("travel_style", ""),
        "food_preferences": preferences.get("food_preferences", []),
        "accommodation_type": preferences.get("accommodation_type", ""),
        "destination": preferences.get("destination", ""),
        "arrival_time": preferences.get("arrival_time", ""),
        "updated_at": preferences.get("updated_at"),
    }

    return jsonify(
        {
            "status": "success",
            "message": "Preferences updated successfully",
            "data": formatted_preferences,
        }
    )


# Travel Partner Matching Routes
@app.route("/api/matches", methods=["GET"])
@login_required
def get_matches():
    """Get travel partner matches for current user"""
    matches = TravelPreference.find_matches(current_user.id)

    return jsonify({"status": "success", "data": matches})


@app.route("/api/matches/search", methods=["POST"])
@login_required
def search_matches():
    """Search for travel partners based on specific criteria"""
    data = request.get_json()
    if not data:
        return (
            jsonify({"status": "error", "message": "No search criteria provided"}),
            400,
        )

    # Search by criteria
    matches = TravelPreference.search_by_criteria(data)

    return jsonify({"status": "success", "data": matches})


# Bookmarking Routes
@app.route("/api/bookmarks", methods=["GET"])
@login_required
def get_bookmarks():
    """Get current user's bookmarked profiles"""
    bookmarked_users = Bookmark.get_by_user(current_user.id)

    # Format the response
    formatted_bookmarks = []
    for user in bookmarked_users:
        # Get user preferences using TravelPreference model
        user_id = str(user["_id"])
        preferences = TravelPreference.get_by_user_id(user_id)

        bookmark_data = {
            "user": {
                "id": user_id,
                "name": user.get("name", ""),
                "profile_picture": user.get("profile_picture", ""),
                "preferences": None,
            }
        }

        # Add preferences if available
        if preferences:
            bookmark_data["user"]["preferences"] = {
                "destination": preferences.get("destination"),
                "budget": preferences.get("budget"),
                "travel_style": preferences.get("travel_style"),
                "food_preferences": preferences.get("food_preferences"),
                "accommodation_type": preferences.get("accommodation_type"),
                "arrival_time": preferences.get("arrival_time"),
            }

        formatted_bookmarks.append(bookmark_data)

    return jsonify({"status": "success", "data": formatted_bookmarks})


@app.route("/api/bookmarks/<user_id>", methods=["POST"])
@login_required
def add_bookmark(user_id):
    """Bookmark a user profile"""
    # Validate target user exists
    target_user = db.users.find_one({"_id": ObjectId(user_id)})
    if not target_user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Check if already bookmarked
    existing = db.bookmarks.find_one(
        {"user_id": ObjectId(current_user.id), "bookmarked_user_id": ObjectId(user_id)}
    )

    if existing:
        return jsonify({"status": "error", "message": "User already bookmarked"}), 409

    # Add bookmark
    Bookmark.add(current_user.id, user_id)

    return jsonify({"status": "success", "message": "User bookmarked successfully"})


@app.route("/api/bookmarks/<user_id>", methods=["DELETE"])
@login_required
def remove_bookmark(user_id):
    """Remove a bookmarked profile"""
    # Check if bookmark exists
    existing = db.bookmarks.find_one(
        {"user_id": ObjectId(current_user.id), "bookmarked_user_id": ObjectId(user_id)}
    )

    if not existing:
        return jsonify({"status": "error", "message": "Bookmark not found"}), 404

    # Remove bookmark
    Bookmark.remove(current_user.id, user_id)

    return jsonify({"status": "success", "message": "Bookmark removed successfully"})


# Messaging Routes
@app.route("/api/messages", methods=["GET"])
@login_required
def get_conversations():
    """Get all conversations for current user"""
    # Find all users that current user has exchanged messages with
    sent_to = db.messages.distinct(
        "recipient_id", {"sender_id": ObjectId(current_user.id)}
    )
    received_from = db.messages.distinct(
        "sender_id", {"recipient_id": ObjectId(current_user.id)}
    )

    # Combine the lists and remove duplicates
    conversation_user_ids = list(
        set([str(user_id) for user_id in sent_to + received_from])
    )

    # Get details of users
    conversations = []
    for user_id in conversation_user_ids:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            # Get the latest message
            latest_message = (
                db.messages.find(
                    {
                        "$or": [
                            {
                                "sender_id": ObjectId(current_user.id),
                                "recipient_id": ObjectId(user_id),
                            },
                            {
                                "sender_id": ObjectId(user_id),
                                "recipient_id": ObjectId(current_user.id),
                            },
                        ]
                    }
                )
                .sort("created_at", -1)
                .limit(1)
            )

            latest_message = list(latest_message)

            # Format the conversation data
            conversation_data = {
                "user": {
                    "id": str(user["_id"]),
                    "name": user.get("name", ""),
                    "profile_picture": user.get("profile_picture", ""),
                },
                "unread_count": 0,  # Placeholder for unread count
            }

            # Add last message data if available
            if latest_message:
                conversation_data["last_message"] = {
                    "content": latest_message[0]["content"],
                    "timestamp": latest_message[0]["created_at"],
                }

            conversations.append(conversation_data)

    return jsonify({"status": "success", "data": conversations})


@app.route("/api/messages/<user_id>", methods=["GET"])
@login_required
def get_messages(user_id):
    """Get messages between current user and another user"""
    # Validate target user exists
    target_user = db.users.find_one({"_id": ObjectId(user_id)})
    if not target_user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Get messages
    messages = Message.get_conversation(current_user.id, user_id)

    # Format messages for response
    formatted_messages = []
    for message in messages:
        formatted_messages.append(
            {
                "id": str(message["_id"]),
                "sender_id": str(message["sender_id"]),
                "recipient_id": str(message["recipient_id"]),
                "content": message["content"],
                "timestamp": message[
                    "created_at"
                ],  # Use timestamp instead of created_at for consistency
            }
        )

    return jsonify({"status": "success", "data": formatted_messages})


@app.route("/api/messages/<user_id>", methods=["POST"])
@login_required
def send_message(user_id):
    """Send a message to another user"""
    # Validate target user exists
    target_user = db.users.find_one({"_id": ObjectId(user_id)})
    if not target_user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    data = request.get_json()
    if not data or "content" not in data:
        return (
            jsonify({"status": "error", "message": "No message content provided"}),
            400,
        )

    # Send message
    message = Message.send(current_user.id, user_id, data["content"])

    # Create notification for recipient
    sender_name = current_user.name
    Notification.create(
        user_id,
        "message",
        f"You received a new message from {sender_name}",
        str(
            current_user.id
        ),  # Store the sender's ID as related_id for message notifications
    )

    # Format message for response
    formatted_message = {
        "id": str(message["_id"]) if "_id" in message else None,
        "sender_id": str(message["sender_id"]),
        "recipient_id": str(message["recipient_id"]),
        "content": message["content"],
        "timestamp": message[
            "created_at"
        ],  # Use timestamp instead of created_at for consistency
    }

    return jsonify({"status": "success", "data": formatted_message}), 201


# Notification Routes
@app.route("/api/notifications", methods=["GET"])
@login_required
def get_notifications():
    """Get notifications for current user"""
    notifications = Notification.get_by_user_id(current_user.id)

    # Format notifications for response
    formatted_notifications = []
    for notification in notifications:
        formatted_notifications.append(
            {
                "id": str(notification["_id"]),
                "content": notification["content"],
                "read": notification["read"],
                "created_at": notification["created_at"],
                "type": notification.get("type", "general"),
                "related_user_id": notification.get("related_id"),
            }
        )

    return jsonify({"status": "success", "data": formatted_notifications})


@app.route("/api/notifications/<notification_id>", methods=["PUT"])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read"""

    if not ObjectId.is_valid(notification_id):
        return jsonify({"status": "error", "message": "Invalid notification ID"}), 400

    result = db.notifications.update_one(
        {"_id": ObjectId(notification_id), "user_id": ObjectId(current_user.id)},
        {"$set": {"read": True}},
    )
    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "Notification not found"}), 404
    return jsonify({"status": "success", "message": "Notification marked as read"}), 200


if __name__ == "__main__":
    app.run(debug=True)
