from http.server import BaseHTTPRequestHandler
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialisation Firebase avec variables d'environnement
if not firebase_admin._apps:
    # On récupère la clé JSON depuis les secrets de Vercel
    cert_dict = json.loads(os.environ.get('FIREBASE_CONFIG_JSON'))
    cred = credentials.Certificate(cert_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        user_msg = data.get("message", "").lower()
        
        # 1. Recherche dans la mémoire Firebase
        docs = db.collection("cerveau_ia").get()
        reponse = "Je n'ai pas encore cette info. Je vais chercher sur le web..."
        source = ""

        for doc in docs:
            d = doc.data()
            if any(mot in user_msg for mot in d.get("poids", [])):
                reponse = d.get("reponse")
                source = d.get("source", "Mémoire interne")
                break

        # 2. Si inconnu, simuler un apprentissage rapide (Source: Wikipedia API)
        if "recherche" in user_msg or reponse.startswith("Je n'ai pas"):
            # Exemple simplifié de recherche web
            reponse = "D'après mes sources, ce composant est essentiel en électronique."
            source = "https://fr.wikipedia.org"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        res = {"reponse": reponse, "source": source}
        self.wfile.write(json.dumps(res).encode())
