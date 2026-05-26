import os
import time
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from scraper import chasser_les_nouveautes

# --- 1. SERVEUR WEB FANTÔME POUR CONTOURNER LA LIMITE RENDER ---
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Chasseur de Pianos en cours de fonctionnement...")

    def log_message(self, format, *args):
        return  # Désactive les logs HTTP pour garder le terminal propre

def run_web_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), SimpleServer)
    print(f"🌍 Serveur fantôme connecté sur le port {port}")
    server.serve_forever()

# --- 2. TON VRAI CODE DE CHASSE AUTOMATIQUE ---
TEMPS_ATTENTE = 60  # Augmenté à 60s pour la stabilité sur le Cloud

def boucle_principale():
    print("🚀 DÉMARRAGE DU CHASSEUR AUTOMATIQUE DE PIANOS")
    print("= = = = = = = = = = = = = = = = = = = = = = = = =")
    print(f"Le robot va analyser tes sites toutes les {TEMPS_ATTENTE} secondes.\n")
    
    compteur_tours = 0
    
    while True:
        compteur_tours += 1
        print(f"\n🔄 Passage n°{compteur_tours} à la loupe...")
        
        try:
            # ICI SE LANCE TA VRAIE RECHERCHE
            chasser_les_nouveautes()
        except Exception as e:
            print(f"⚠️ Une erreur inattendue est survenue : {e}")
            
        print(f"💤 En attente pendant {TEMPS_ATTENTE} secondes...")
        time.sleep(TEMPS_ATTENTE)

# --- 3. DÉMARRAGE SYNCHRONISÉ ---
if __name__ == "__main__":
    # 1. On lance le serveur web pour que Render passe au vert ("Live")
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # 2. On lance ta vraie recherche de pianos
    boucle_principale()
