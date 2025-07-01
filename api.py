from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

MONGO_URI = "mongodb+srv://curly:modhubadmin@cluster0.o2iyvog.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["modhub"]
keys_col = db["Cluster0"]

@app.route("/verify", methods=["POST"])
def verify_key():
    data = request.json
    key = data.get("key")
    machine_id = data.get("machine_id")

    key_entry = keys_col.find_one({"key": key, "used": False})
    if not key_entry:
        return jsonify({"success": False, "message": "Invalid or already used key"}), 403

    # Invalidate key
    keys_col.update_one({"_id": key_entry["_id"]}, {
        "$set": {
            "used": True,
            "used_at": datetime.utcnow(),
            "machine_id": machine_id
        }
    })

    return jsonify({"success": True})

@app.route("/generate", methods=["POST"])
def generate_key():
    import random, string
    new_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    keys_col.insert_one({
        "key": new_key,
        "used": False,
        "created_at": datetime.utcnow(),
        "created_by": request.json.get("user", "unknown")
    })
    return jsonify({"key": new_key})

if __name__ == "__main__":
    app.run(port=5000)
