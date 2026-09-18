os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify, render_template_string
import random
import string

app = Flask(__name__)

ADMIN_PASSWORD = "omegaaimbot"
db = None

try:
    firebase_config = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    
    if firebase_config:
        # Linisin ang string mula sa extra quotes o whitespace
        firebase_config = firebase_config.strip()
        if (firebase_config.startswith("'") and firebase_config.endswith("'")) or \
           (firebase_config.startswith('"') and firebase_config.endswith('"')):
            firebase_config = firebase_config[1:-1]
            
        # Subukang i-parse bilang JSON
        try:
            cred_dict = json.loads(firebase_config)
        except json.JSONDecodeError:
            # Kung sakaling nagloko ang mga quotes, ayusin natin nang manu-mano
            import ast
            cred_dict = ast.literal_eval(firebase_config)
            
        # Ayusin ang private key newlines para hindi magka-PEM error
        if "private_key" in cred_dict:
            pk = cred_dict["private_key"]
            # Palitan ang literal na \n ng tunay na newline kung kinakailangan
            cred_dict["private_key"] = pk.replace("\\n", "\n")

        cred = credentials.Certificate(cred_dict)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully!")
    else:
        print("Firebase Init Error: FIREBASE_SERVICE_ACCOUNT environment variable is missing.")
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
    
    if db is None:
        return "Database not initialized. Check server logs.", 500
    
    new_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    try:
        db.collection("keys").add({"key": new_key, "created_at": firestore.SERVER_TIMESTAMP})
    except Exception as e:
        print(f"Firestore save error: {e}")
        return f"Firestore save error: {e}", 500

    return render_template_string(HTML_TEMPLATE, logged_in=logged_in_state, generated_key=new_key)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
