from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGODB_CONNECTION")

client = MongoClient(MONGO_URI)
db = client["bot_logs"]
logs_collection = db["message_logs"]

def log_message_stats(message):
    log_entry = {
        "timestamp": datetime.now(),
        "user_id": message.author.id,
        "username": str(message.author),
        "channel_id": message.channel.id,
        "channel_name": str(message.channel),
        "message_id": message.id,
        "content_length": len(message.content),
        "word_count": len(message.content.split()),
        "has_attachments": len(message.attachments) > 0,
        "mentions": [user.id for user in message.mentions],
        "is_command": message.content.startswith("!"),  # Adjust if you use a different prefix
    }
    logs_collection.insert_one(log_entry)
    print(f"Logged message from {message.author} in {message.channel}")
