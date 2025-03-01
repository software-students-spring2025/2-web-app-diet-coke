from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["travelmatch_db"]
users_collection = db["users"]

# Test connection
if db.list_collection_names():
    print("MongoDB Connection Successful Collections:", db.list_collection_names())
else:
    print("Connected to MongoDB, no collections found.")
