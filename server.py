from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string
import os

app = Flask(__name__)

# Palitan mo ito ng sarili mong sikretong password para sa pag-generate ng key
ADMIN_PASSWORD = "boss_rufino_secure_password"

# I-initialize ang Firebase gamit ang iyong secret JSON
CRED_PATH = "serviceAccountKey.json"
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(CRED_PATH)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Firebase Init Error: {e}")

# HTML Dashboard na may Password Login
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VIP Key Generator Manager</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f0f13; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; background: #181820; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #00ffcc; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #aaa; }
        input { width: 100%; padding: 10px; background: #22222f; border: 1px solid #333344; color: #fff; border-radius: 5px; box-sizing: border-box; }
        button { background: #ff4d4d; color: white; border: none; padding: 10px 15px; width: 100%; font-weight: bold; border-radius: 5px; cursor: pointer; transition: 0.2s; }
        button:hover { background: #ff1a1a; }
        .result-box { margin-top: 15px; padding: 10px; background: #111116; border-left: 4px solid #00ffcc; font-family: monospace; word-break: break-all; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔑 VIP Key Manager</h2>
        
        <!-- Login Section -->
        <div id="login-section" class="form-group">
            <label>Admin Password:</label>
            <input type="password" id="password" placeholder="Ilagay ang password...">
            <button style="margin-top:10px;" onclick="verifyLogin()">Mag-login</button>
        </div>

        <!-- Generator Section (Naka-hide muna hangga't hindi nagre-login) -->
        <div id="generator-section" class="hidden">
            <div class="form-group">
                <label>Ilang Araw ang Bisa (Duration):</label>
                <input type="number" id="days" value="1" min="1">
            </div>
            <button onclick="generateKey()">Gumawa ng Bagong Key</button>
            <div id="result" class="result-box hidden"></div>
        </div>
    </div>

    <script>
        let token = "";

        async function verifyLogin() {
            const pass = document.getElementById('password').value;
            const res = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pass })
            });
            const data = await res.json();
            if(data.success) {
                token = pass;
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('generator-section').style.display = 'block';
            } else {
                alert("Mali ang password!");
            }
        }

        async function generateKey() {
            const days = document.getElementById('days').value;
            const res = await fetch('/generate-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: token, days: parseInt(days) })
            });
            const data = await res.json();
            const resultBox = document.getElementById('result');
            resultBox.style.display = 'block';
            if(data.success) {
                resultBox.innerHTML = `<b>[SUCCESS] New Key:</b><br><span style="color:#00ffcc; font-size: 16px;">${data.key}</span>`;
            } else {
                resultBox.innerHTML = `<span style="color:#ff4d4d;">Error: ${data.message}</span>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('password') == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/generate-key', methods=['POST'])
def generate_key():
    data = request.json
    if data.get('password') != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    try:
        days = data.get('days', 1)
        chars = string.ascii_uppercase + string.digits
        raw_key = "".join(random.choice(chars) for _ in range(16))
        new_key = f"VIP-{raw_key[:4]}-{raw_key[4:8]}-{raw_key[8:12]}"
        
        key_data = {
            "key": new_key,
            "status": "active",
            "duration_days": days,
            "hwid": None
        }
        
        db.collection("license_keys").document(new_key).set(key_data)
        return jsonify({"success": True, "key": new_key})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/verify-key', methods=['POST'])
def verify_key():
    data = request.json
    entered_key = data.get('key')
    
    if not entered_key:
        return jsonify({"success": False, "message": "No key provided"}), 400

    try:
        docs = db.collection('license_keys').where('key', '==', entered_key).stream()
        key_doc = None
        doc_id = None

        for doc in docs:
            key_doc = doc.to_dict()
            doc_id = doc.id
            break

        if not key_doc:
            return jsonify({"success": False, "message": "Invalid key"})

        status = key_doc.get('status', '').lower()
        if status == "active":
            db.collection('license_keys').document(doc_id).update({
                'status': 'used'
            })
            return jsonify({"success": True, "message": "Key verified and consumed"})

        return jsonify({"success": False, "message": "Key already used or expired"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)