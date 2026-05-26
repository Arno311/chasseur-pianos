import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. CONFIGURATION DU SERVEUR WEB FANTÔME POUR RENDER ---
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Chasseur de Pianos en cours de fonctionnement...")

    def log_message(self, format, *args):
        # Désactive les logs de requêtes HTTP pour ne pas polluer ton terminal
        return

def run_web_server():
    # Render donne le port via la variable PORT, sinon 8000 par défaut en local
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), SimpleServer)
    print(f"🌍 Serveur fantôme démarré sur le port {port}")
    server.serve_forever()

# --- 2. TON CODE DE SCRIPT EXISTANT ---
# (Assure-toi que tes imports comme scraper ou database sont bien là si nécessaire)

def boucle_principale():
    print("🤖 DÉMARRAGE DU CHASSEUR AUTOMATIQUE DE PIANOS")
    
    while True:
        try:
            print("🔄 Passage à la loupe...")
            
            # C'est ici que s'exécute ton code actuel.
            # Exemple :
            # voitures = scraper.obtenir_annonces()
            # database.sauvegarder(voitures)
            
            # Modifie le temps (ici 60 secondes pour le Cloud pour éviter les blocages)
            time.sleep(60)
            
        except Exception as e:
            print(f"❌ Erreur dans la boucle : {e}")
            time.sleep(30)

# --- 3. POINT D'ENTRÉE ---
if __name__ == "__main__":
    # On lance le serveur web dans un fil secondaire (Thread) pour que Render soit content
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # On lance ta vraie fonction de chasse aux pianos dans le fil principal
    boucle_principale()
