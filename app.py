import time
import sys
from scraper import chasser_les_nouveautes

TEMPS_ATTENTE = 10 

def démarrer_le_chasseur():
    print("🚀 DÉMARRAGE DU CHASSEUR AUTOMATIQUE DE PIANOS")
    print("= = = = = = = = = = = = = = = = = = = = = = = = =")
    print(f"Le robot va analyser tes sites toutes les {TEMPS_ATTENTE} secondes.")
    print("Pour arrêter proprement le robot, fais Ctrl + C dans ce terminal.\n")
    
    compteur_tours = 0
    
    while True:
        compteur_tours += 1
        print(f"\n🔄 Passage n°{compteur_tours} à la loupe...")
        
        try:
            chasser_les_nouveautes()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt manuel détecté (Ctrl+C). Fermeture du Chasseur.")
            sys.exit()
        except Exception as e:
            print(f"⚠️ Une erreur inattendue est survenue : {e}")
            
        print(f"💤 En attente pendant {TEMPS_ATTENTE} secondes...")
        
        # Blindage du sleep contre les pressions de touches aléatoires
        try:
            time.sleep(TEMPS_ATTENTE)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt manuel détecté pendant la pause. Fermeture du Chasseur.")
            sys.exit()

if __name__ == "__main__":
    démarrer_le_chasseur()