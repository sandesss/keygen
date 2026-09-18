from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string

app = Flask(__name__)

# Palitan mo ito ng sarili mong sikretong password para sa admin login
ADMIN_PASSWORD = "boss_rufino_secure_password"

# Direktang Firebase Configuration mula sa iyong credentials
firebase_config = {
    "type": "service_account",
    "project_id": "omegards",
    "private_key_id": "5eedd30d67a6aad493036ce257299f0f772f7f96",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDV8zNneh9Sc9pS\nvuJcb4Hy6rAD+hL9JjHnMdSP2yGVGpgWKhH8PWrDwkqZcDM7fpJaWb+xgLbQ2k1T\nxqFlJXNQ3/1GUqNubVUyM/+wnx4t1G/E9ceessJyg0lBxhjYeCwEu2U7KbQBgl1B\nKNWE+AOzKJ45lNKmebKYbBn08cN32Cq4PS7FI+jlS29Z55hNr7BbfsSE4Jb9EpIE\n7PqRSzPp47lrz1xWR94mtqrP2a4toT4vI+NsSayjTqBQQnL8l/PI6dQCOH7vv+tW\n2uILCxxwrYs+Vyl/YhrjD8IZGhSqdY5uSFefqriZ2fltu+CuXqkXH5SUFBIrQBi0\nhAMNWk51AgMBAAECggEAHCuCaCx/NUcFxwFVIqCX9pkKBewGVgiSZ4N7HlnW6R/w\nSHLPnWukxBOv6NYKGNpIgNbyU3fEGmmz5sTveTbeIRbs7TZySFbi8dJA50t8GMKw\n2LkXyIB288bvfVaM7OuduB3IbWrHRa+ZgbvTqUdSjWNaufArcDnz1vfczxCKERxK\nmSy0XUK6gyZ7JBoWSSjA8rCv5Xez5VkvJDwKGo4iQavcLv7YfqCu9xgvh+LApu81\nCCWyZ4CnMUzf8SJMZbZejnRSKIX8p9kEg7/p/PrlwmjPZqYN/EULUbHsusdwBYH0\nxYl/SE4Y6/HBRC5V9ywT6JefobhUDwb5CtJl5/+NAQKBgQDtLfrEiVg5/CawUkl+\n36dR9xw8Vee3sZZoh+ZKDmRpE8LogJkI3WV70wVbPJF9pohk/qNF0IhhMcdSfddN\ncBfqOdR8FvYYKhfUQrpPg7XD1b/rO3IVGNoEEx6MlyiWmb68J6tgnReDDJnuBhY7\nB5aa3tDu1emcAiK1uodYte5nQQKBgQDm7Vbtx6UfUveko11ag0X8F0KucyjkmpNv\nunZCMLc9tuKMa8o0GYcrPbv4+VvunbUyVFlCpGqOZ3gjAvoZHiyLmKtpopHnn12d\nPdOuqA9Wuh8WEu5vjw5vb8DWq3Fsl8LE4ZZxgzs1fb5kSlFbjpJTUzq75OmlFXla\nf2r6E2FuNQKBgG4/8VFqhphtnY5YsdFIJX70Xyuswwmgg0oT4fiKuCIgDXoGTRzR\nzVrBvLusa/T8dGp982eAh+SmPwEZffuBH5zBRQRpp/uTlYAVhIVxtAxUT+IIv/8O\njklWmdzAZx2aWg8cYY2HeGZydRsvuSW3YUqcSIK87NqYI4pWKpQR/cABAoGAWLJI\ndUP9dC6V17K3pJBPTShSAFdTGZsVjhB8Y6f6ecXI9k5gd+pmNIGdtV9xpBEHC7HC\nJwqnstKjHi+CiCtCyMt26zf5+pEHj+GzcJ40ZgdO8VeMJWU5EixGUS3Afwk7Uguj\nkS3qi/0kJ7kzzorQQRjyskCWTUYWOmA+YpcXERECgYEAmfmSZrvpgwUvfYFMWAOa\RKPsTtNTi6cXFUPJhrXG/Orut+0GKxWDftw/u/pULh4hc9PpYJU3dWl7tb3KaF/D\nTQSzRr0+kBaG1XOPJqddIwhz/Ey/pIdWUE+gEItdcdbnA5ft6FJIEgFp7hrTAu9K\nHX89A1PLyp6/l5f4xS0Gtpc=\n-----END PRIVATE KEY-----\n".replace('\\n', '\n'),
    "client_email": "firebase-adminsdk-fbsvc@omegards.iam.gserviceaccount.com",
    "client_id": "108608414158489281111",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40omegards.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

try:
    cred = credentials.Certificate(firebase_config)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Firebase Init Error: {e}")

# Modern & Responsive Admin Panel HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepCleaner VIP Manager</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --accent-color: #2ea043;
            --accent-hover: #238636;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            --border-color: #30363d;
            --input-bg: #0d1117;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 90vh;
        }
        .container {
            width: 100%;
            max-width: 420px;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            box-sizing: border-box;
        }
        h2 {
            text-align: center;
            color: #ffffff;
            margin-top: 0;
            font-size: 22px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            margin-bottom: 6px;
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px;
            background-color: var(--input-bg);
            border: 1px solid var(--border-color);
            color: #ffffff;
            border-radius: 6px;
            font-size: 15px;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus {
            border-color: #58a6ff;
        }
        button {
            background-color: var(--accent-color);
            color: white;
            border: none;
            padding: 12px;
            width: 100%;
            font-weight: 600;
            border-radius: 6px;
            font-size: 15px;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-top: 5px;
        }
        button:hover {
            background-color: var(--accent-hover);
        }
        .result-box {
            margin-top: 20px;
            padding: 14px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            word-break: break-all;
            text-align: center;
        }
        .key-text {
            color: #58a6ff;
            font-family: monospace;
            font-size: 16px;
            font-weight: bold;
            margin-top: 8px;
            display: block;
            user-select: all;
        }
        .error-text {
            color: #f85149;
            font-size: 14px;
        }
        .hidden {
            display: none;
        }
        .footer {
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛡️ DeepCleaner VIP</h2>
        
        <!-- Login Section -->
        <div id="login-section">
            <div class="form-group">
                <label>Admin Password</label>
                <input type="password" id="password" placeholder="Ilagay ang password...">
            </div>
            <button onclick="verifyLogin()">Mag-login</button>
        </div>

        <!-- Generator Section -->
        <div id="generator-section" class="hidden">
            <div class="form-group">
                <label>Bisa (Araw / Duration)</label>
                <input type="number" id="days" value="30" min="1">
            </div>
            <button onclick="generateKey()">✨ Gumawa ng VIP Key</button>
            <div id="result" class="result-box hidden"></div>
        </div>
        
        <div class="footer">Secure Admin Control Panel</div>
    </div>

    <script>
        let adminToken = "";

        async function verifyLogin() {
            const pass = document.getElementById('password').value;
            const res = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pass })
            });
            const data = await res.json();
            if(data.success) {
                adminToken = pass;
                document.getElementById('login-section').style.display = 'none';
                document.getElementById('generator-section').style.display = 'block';
            } else {
                alert("Mali ang password mo, boss!");
            }
        }

        async function generateKey() {
            const days = document.getElementById('days').value;
            const res = await fetch('/generate-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: adminToken, days: parseInt(days) })
            });
            const data = await res.json();
            const resultBox = document.getElementById('result');
            resultBox.style.display = 'block';
            
            if(data.success) {
                resultBox.innerHTML = `<span>Bagong Key na Nilikha:</span><span class="key-text">${data.key}</span>`;
            } else {
                resultBox.innerHTML = `<span class="error-text">Error: ${data.message}</span>`;
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
        days = data.get('days', 30)
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
