import requests

# Remplace par tes vrais jetons
TOKEN_BOT = "TON_TELEGRAM_BOT_TOKEN"
CHAT_ID = "TON_TELEGRAM_CHAT_ID"

def envoyer_alerte(message):
    """Envoie un message sur Telegram au format Markdown pour activer les liens cliquables."""
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    
    donnees = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False  # Permet d'afficher un aperçu du site dans Telegram
    }
    
    try:
        reponse = requests.post(url, data=donnees, timeout=10)
        if reponse.status_code != 200:
            print(f"❌ Erreur Telegram ({reponse.status_code}) : {reponse.text}")
        else:
            print("🚀 Alerte Telegram envoyée avec succès !")
    except Exception as e:
        print(f"❌ Impossible de joindre Telegram : {e}")