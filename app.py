import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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

# --- 2. TON CODE DE CHASSE ET DE SCRAPING ---
def boucle_principale():
    print("🤖 DÉMARRAGE DU CHASSEUR AUTOMATIQUE DE PIANOS")
    
    while True:
        try:
            print("🔄 Passage à la loupe des sites de petites annonces...")
            
            # Ton scraper va s'exécuter ici en tâche de fond.
            # Laisse tourner une vérification toutes les 60 secondes sur le cloud
            time.sleep(60)
            
        except Exception as e:
            print(f"❌ Erreur dans la boucle : {e}")
            time.sleep(30)

# --- 3. DÉMARRAGE SYNCHRONISÉ ---
if __name__ == "__main__":
    # Lance le serveur web sur un fil d'attente secondaire (Render passe au vert)
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Lance ta vraie boucle principale de recherche
    boucle_principale()
