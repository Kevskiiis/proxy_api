import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

# Load variables from a .env file (for security)
load_dotenv()

app = Flask(__name__)

# Supabase Setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Simple blocklist for demonstration
BLOCKED_DOMAINS = ["usf.org", "bad-site.com"]

@app.route('/proxy/check', methods=['POST'])
def check_and_log():
    # Expecting JSON input: {"site": "usf.org"}
    data = request.get_json()
    site_to_check = data.get("site", "").lower()

    if not site_to_check:
        return jsonify({"error": "No site provided"}), 400

    is_blocked = any(site_to_check.endswith(domain) for domain in BLOCKED_DOMAINS)

    if is_blocked:
        # 1. Log the attempt to your Postgres table
        try:
            supabase.table("access_control").insert({"site": site_to_check}).execute()
        except Exception as e:
            print(f"Logging failed: {e}")

        # 2. Return the blocked response
        return jsonify({
            "status": "blocked",
            "message": f"Access to {site_to_check} is denied.",
            "recorded": True
        }), 403

    return jsonify({"status": "allowed", "site": site_to_check}), 200

if __name__ == '__main__':
    # Run on port 5000 in debug mode
    app.run(debug=True, port=5000)