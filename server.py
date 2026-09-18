import os
from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string

app = Flask(__name__)

ADMIN_PASSWORD = "omegaaimbot"

# Basahin ang credentials nang direkta sa hiwalay na environment variables para walang bawas-dagdag o escape issues
try:
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

    if project_id and client_email and private_key:
        # Ayusin ang private_key kung sakaling nadoble ang backslashes
        formatted_private_key = private_key.replace('\\n', '\n')
        
        cred_dict = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", "fixed_id"),
            "private_key": formatted_private_key,
            "client_email": client_email,
            "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}",
            "universe_domain": "googleapis.com"
        }
        cred = credentials.Certificate(cred_dict)
    else:
        # Fallback kung local file
        cred = credentials.Certificate("serviceAccountKey.json")

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Firebase Init Error: {e}")

# (I-keep mo rito yung HTML_TEMPLATE at mga routes mo sa ibaba tulad ng dati...)
