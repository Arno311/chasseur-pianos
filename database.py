from supabase import create_client, Client

SUPABASE_URL = "https://knflhttckasbxobxfubz.supabase.co"
SUPABASE_KEY = "sb_publishable_3S-n6kg3SRYCwHImwSQJZQ_w2RsxkbF"

# Connexion initiale unique partagée par tout le projet
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verifier_et_enregistrer_piano(titre_piano):
    """Insère un piano trouvé dans la table annonces."""
    try:
        data = supabase.table("annonces").insert({"titre": titre_piano}).execute()
        if data:
            return True
    except Exception as e:
        print(f"⚠️ Erreur lors de l'enregistrement en base : {e}")
        return False
    return False