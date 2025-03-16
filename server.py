from flask import Flask, request, jsonify
import hashlib
import os
import uuid

app = Flask(__name__)

# File to store user data (key, HWID, etc.)
USER_DATA_FILE = "userdata.txt"
BLACKLIST_FILE = "blacklist.txt"

# Predefined valid license keys (replace with your own logic or database)
VALID_KEYS = set()

def get_hwid():
    """Generate a simple HWID based on the machine's hardware information."""
    hardware_info = os.environ.get("COMPUTERNAME", "") + str(os.cpu_count()) + os.name
    return hashlib.sha256(hardware_info.encode()).hexdigest()

def save_user_data(license_key, hwid):
    """Save user data (license key and HWID) to a file."""
    with open(USER_DATA_FILE, "a") as file:
        file.write(f"{license_key}|{hwid}\n")

def check_hwid(license_key, hwid):
    """Check if the provided HWID matches the stored HWID for the given license key."""
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            stored_key, stored_hwid = line.strip().split("|")
            if stored_key == license_key:
                return stored_hwid == hwid
    return False

def is_blacklisted(license_key):
    """Check if a license key is blacklisted."""
    if not os.path.exists(BLACKLIST_FILE):
        return False

    with open(BLACKLIST_FILE, "r") as file:
        for line in file:
            if line.strip() == license_key:
                return True
    return False

def generate_key():
    """Generate a new license key."""
    new_key = str(uuid.uuid4()).replace("-", "").upper()[:16]
    VALID_KEYS.add(new_key)
    return new_key

def blacklist_key(license_key):
    """Blacklist a license key."""
    with open(BLACKLIST_FILE, "a") as file:
        file.write(f"{license_key}\n")

def reset_hwid(license_key):
    """Reset HWID for a license key."""
    if not os.path.exists(USER_DATA_FILE):
        return False

    lines = []
    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            stored_key, _ = line.strip().split("|")
            if stored_key == license_key:
                continue  # Skip this line to reset HWID
            lines.append(line)

    with open(USER_DATA_FILE, "w") as file:
        file.writelines(lines)

    return True

@app.route("/auth", methods=["POST"])
def auth():
    data = request.json
    license_key = data.get("license_key")
    hwid = data.get("hwid")

    if not license_key or not hwid:
        return jsonify({"status": "error", "message": "Missing license key or HWID"}), 400

    if license_key not in VALID_KEYS:
        return jsonify({"status": "error", "message": "Invalid license key"}), 401

    if is_blacklisted(license_key):
        return jsonify({"status": "error", "message": "License key is blacklisted"}), 403

    # Check if this is the first login for the key
    if not os.path.exists(USER_DATA_FILE):
        # First login: save HWID
        save_user_data(license_key, hwid)
        return jsonify({"status": "success", "message": "First login successful! HWID registered."}), 200

    # Check if the key exists in the user data file
    key_exists = False
    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            stored_key, _ = line.strip().split("|")
            if stored_key == license_key:
                key_exists = True
                break

    if not key_exists:
        # First login for this key: save HWID
        save_user_data(license_key, hwid)
        return jsonify({"status": "success", "message": "First login successful! HWID registered."}), 200

    # Check HWID for existing keys
    if check_hwid(license_key, hwid):
        return jsonify({"status": "success", "message": "Authentication successful!"}), 200
    else:
        return jsonify({"status": "error", "message": "Wrong HWID!"}), 401

@app.route("/generate_key", methods=["GET"])
def generate_key_endpoint():
    new_key = generate_key()
    return jsonify({"status": "success", "key": new_key}), 200

@app.route("/blacklist", methods=["POST"])
def blacklist():
    data = request.json
    license_key = data.get("license_key")

    if not license_key:
        return jsonify({"status": "error", "message": "Missing license key"}), 400

    blacklist_key(license_key)
    return jsonify({"status": "success", "message": f"License key {license_key} blacklisted"}), 200

@app.route("/reset_hwid", methods=["POST"])
def reset_hwid_endpoint():
    data = request.json
    license_key = data.get("license_key")

    if not license_key:
        return jsonify({"status": "error", "message": "Missing license key"}), 400

    if reset_hwid(license_key):
        return jsonify({"status": "success", "message": f"HWID reset for {license_key}"}), 200
    else:
        return jsonify({"status": "error", "message": "License key not found"}), 404

if __name__ == "__main__":
    # Create userdata and blacklist files if they don't exist
    if not os.path.exists(USER_DATA_FILE):
        open(USER_DATA_FILE, "w").close()
    if not os.path.exists(BLACKLIST_FILE):
        open(BLACKLIST_FILE, "w").close()

    app.run(host="", port=5000)
