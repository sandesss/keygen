import os
import json
from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

try:
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

    if project_id and client_email and private_key:
        # Linisin nang husto ang private key laban sa literal na \n o extra backslashes
        cleaned_key = private_key.replace('\\n', '\n').strip()
        if not cleaned_key.startswith("-----BEGIN PRIVATE KEY-----"):
            # Kung sakaling may nakapulot na quotes sa unahan o dulo
            cleaned_key = cleaned_key.strip('"').strip("'")

        cred_dict = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", "5eedd30d67a6aad493036ce257299f0f772f7f96"),
            "private_key": cleaned_key,
            "client_email": client_email,
            "client_id": os.environ.get("FIREBASE_CLIENT_ID", "108608414158489281111"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email.replace('@', '%40')}",
            "universe_domain": "googleapis.com"
        }
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Firebase Init Error: {e}")
