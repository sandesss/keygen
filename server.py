import os
import json
from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string

app = Flask(__name__)

ADMIN_PASSWORD = "boss_rufino_secure_password"

# Solusyon: Gagamitin natin ang base64 o kaya hiwalay na linya na lininis nang diretso
private_key_lines = [
    "-----BEGIN PRIVATE KEY-----",
    "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDV8zNneh9Sc9pS",
    "vuJcb4Hy6rAD+hL9JjHnMdSP2yGVGpgWKhH8PWrDwkqZcDM7fpJaWb+xgLbQ2k1T",
    "xqFlJXNQ3/1GUqNubVUyM/+wnx4t1G/E9ceessJyg0lBxhjYeCwEu2U7KbQBgl1B",
    "KNWE+AOzKJ45lNKmebKYbBn08cN32Cq4PS7FI+jlS29Z55hNr7BbfsSE4Jb9EpIE",
    "7PqRSzPp47lrz1xWR94mtqrP2a4toT4vI+NsSayjTqBQQnL8l/PI6dQCOH7vv+tW",
    "2uILCxxwrYs+Vyl/YhrjD8IZGhSqdY5uSFefqriZ2fltu+CuXqkXH5SUFBIrQBi0",
    "hAMNWk51AgMBAAECggEAHCuCaCx/NUcFxwFVIqCX9pkKBewGVgiSZ4N7HlnW6R/w",
    "SHLPnWukxBOv6NYKGNpIgNbyU3fEGmmz5sTveTbeIRbs7TZySFbi8dJA50t8GMKw",
    "2LkXyIB288bvfVaM7OuduB3IbWrHRa+ZgbvTqUdSjWNaufArcDnz1vfczxCKERxK",
    "mSy0XUK6gyZ7JBoWSSjA8rCv5Xez5VkvJDwKGo4iQavcLv7YfqCu9xgvh+LApu81",
    "CCWyZ4CnMUzf8SJMZbZejnRSKIX8p9kEg7/p/PrlwmjPZqYN/EULUbHsusdwBYH0",
    "xYl/SE4Y6/HBRC5V9ywT6JefobhUDwb5CtJl5/+NAQKBgQDtLfrEiVg5/CawUkl+",
    "36dR9xw8Vee3sZZoh+ZKDmRpE8LogJkI3WV70wVbPJF9pohk/qNF0IhhMcdSfddN",
    "cBfqOdR8FvYYKhfUQrpPg7XD1b/rO3IVGNoEEx6MlyiWmb68J6tgnReDDJnuBhY7",
    "B5aa3tDu1emcAiK1uodYte5nQQKBgQDm7Vbtx6UfUveko11ag0X8F0KucyjkmpNv",
    "nunZCMLc9tuKMa8o0GYcrPbv4+VvunbUyVFlCpGqOZ3gjAvoZHiyLmKtpopHnn12d",
    "PdOuqA9Wuh8WEu5vjw5vb8DWq3Fsl8LE4ZZxgzs1fb5kSlFbjpJTUzq75OmlFXla",
    "nf2r6E2FuNQKBgG4/8VFqhphtnY5YsdFIJX70Xyuswwmgg0oT4fiKuCIgDXoGTRzR",
    "nzVrBvLusa/T8dGp982eAh+SmPwEZffuBH5zBRQRpp/uTlYAVhIVxtAxUT+IIv/8O",
    "njklWmdzAZx2aWg8cYY2HeGZydRsvuSW3YUqcSIK87NqYI4pWKpQR/cABAoGAWLJI",
    "ndUP9dC6V17K3pJBPTShSAFdTGZsVjhB8Y6f6ecXI9k5gd+pmNIGdtV9xpBEHC7HC",
    "JwqnstKjHi+CiCtCyMt26zf5+pEHj+GzcJ40ZgdO8VeMJWU5EixGUS3Afwk7Uguj",
    "nkS3qi/0kJ7kzzorQQRjyskCWTUYWOmA+YpcXERECgYEAmfmSZrvpgwUvfYFMWAOa",
    "RKPsTtNTi6cXFUPJhrXG/Orut+0GKxWDftw/u/pULh4hc9PpYJU3dWl7tb3KaF/D",
    "TQSzRr0+kBaG1XOPJqddIwhz/Ey/pIdWUE+gEItdcdbnA5ft6FJIEgFp7hrTAu9K",
    "HX89A1PLyp6/l5f4xS0Gtpc=",
    "-----END PRIVATE KEY-----"
]

cred_dict = {
    "type": "service_account",
    "project_id": "omegards",
    "private_key_id": "5eedd30d67a6aad493036ce257299f0f772f7f96",
    "private_key": "\n".join(private_key_lines),
    "client_email": "firebase-adminsdk-fbsvc@omegards.iam.gserviceaccount.com",
    "client_id": "108608414158489281111",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40omegards.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Firebase Init Error: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Key Generator Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: #fff; padding: 40px; text-align: center; }
        .box { background: #1e1e1e; padding: 30px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        input, button { padding: 10px; margin: 10px; font-size: 16px; border-radius: 4px; border: none; }
        button { background: #4CAF50; color: white; cursor: pointer; }
        button:hover { background: #45a049; }
        pre { background: #2d2d2d; padding: 15px; text-align: left; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Omegards Keygen System</h2>
        {% if not logged_in %}
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="Enter Admin Password" required>
            <br>
            <button type="submit">Login</button>
        </form>
        {% else %}
        <form method="POST" action="/generate-key">
            <button type="submit">Generate New Key</button>
        </form>
        {% if generated_key %}
        <h3>Generated Key:</h3>
        <pre>{{ generated_key }}</pre>
        {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

logged_in_state = False

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, logged_in=logged_in_state, generated_key=None)

@app.route("/login", methods=["POST"])
def login():
    global logged_in_state
    pwd = request.form.get("password")
    if pwd == ADMIN_PASSWORD:
        logged_in_state = True
    return render_template_string(HTML_TEMPLATE, logged_in=logged_in_state, generated_key=None)

@app.route("/generate-key", methods=["POST"])
def generate_key():
    global logged_in_state
    if not logged_in_state:
        return "Unauthorized", 403
    
    new_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    try:
        db.collection("keys").add({"key": new_key, "created_at": firestore.SERVER_TIMESTAMP})
    except Exception as e:
        print(f"Firestore save error: {e}")

    return render_template_string(HTML_TEMPLATE, logged_in=logged_in_state, generated_key=new_key)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
