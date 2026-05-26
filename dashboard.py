import streamlit as st
import os
import json
import requests
from google import genai
from database import supabase  # Import propre depuis le fichier database.py

st.set_page_config(page_title="Piano Hunter - Control Center", page_icon="🎹", layout="wide")

st.title("🎹 Piano Hunter Control Center")
st.markdown("---")

# --- FONCTION AUTOMATIQUE AVEC GEMINI ---
def trouver_url_api_via_ia(nom_plateforme):
    """Utilise Gemini pour trouver automatiquement l'URL du flux JSON de l'API d'un site."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🔑 Clé GEMINI_API_KEY manquante dans les variables d'environnement.")
        return None

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Tu es l'ingénieur système du projet 'Piano Hunter' en Suisse.
        L'utilisateur a entré le nom du site suivant : "{nom_plateforme}".
        
        Trouve l'URL exacte du flux de données API (JSON) utilisé pour l'index ou la recherche d'instruments / musique sur ce site.
        
        Voici les correspondances strictes à renvoyer selon ce que l'utilisateur écrit :
        - Si ça parle de 'Anibis' : "https://wms.anibis.ch/v2/fr/entries?api-version=2.0&category=210&sort=date-desc&page=1&size=20"
        - Si ça parle de 'Tutti' : "https://www.tutti.ch/api/v1/search.json?category=4020&sort=date&page=1"
        - Si ça parle de 'Ricardo' : "https://api.ricardo.ch/v1/articles?categoryIds=12144&sort=StartDateDescending"
        
        Si c'est un autre site de petites annonces connu, essaie de deviner ou générer l'URL de son API publique de recherche.
        
        Renvoie UNIQUEMENT un objet JSON sous cette forme, sans texte autour, sans markdown :
        {{"url_trouvee": "L_URL_ICI"}}
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        texte_nettoye = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(texte_nettoye)
        return data.get("url_trouvee")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la recherche automatique de l'URL : {e}")
        return None


# --- NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🚀 Annonces", "🔍 Configuration Mots-Clés", "🌐 Gestion des Sites"])

# --- TAB 1 : AFFICHAGE DES ANNONCES ---
with tab1:
    st.subheader("Dernières opportunités détectées")
    if st.button("🔄 Actualiser le flux"):
        st.rerun()
    
    try:
        res = supabase.table("annonces").select("*").order("id", desc=True).execute()
        if not res.data:
            st.info("Aucune annonce pour le moment.")
        else:
            for item in res.data:
                with st.container(border=True):
                    st.markdown(f"### {item['titre']}")
                    st.caption(f"Annonce N° : {item['id']}")
    except Exception as e:
        st.error(f"Erreur lors du chargement des annonces : {e}")

# --- TAB 2 : CONFIGURATION MOTS-CLÉS ---
with tab2:
    st.subheader("Gérer les mots-clés recherchés")
    
    with st.form("add_keyword"):
        nouveau_mot = st.text_input("Nouveau mot-clé (ex: clavecin)")
        if st.form_submit_button("Ajouter à la surveillance"):
            if nouveau_mot:
                try:
                    supabase.table("config_mots_cles").insert({"mot": nouveau_mot.lower().strip(), "actif": True}).execute()
                    st.success(f"'{nouveau_mot}' ajouté avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'ajout : {e}")

    st.markdown("#### Mots-clés actifs")
    try:
        keywords = supabase.table("config_mots_cles").select("*").execute()
        if not keywords.data:
            st.info("Aucun mot-clé configuré.")
        else:
            for kw in keywords.data:
                col1, col2 = st.columns([4, 1])
                col1.write(f"✅ {kw['mot']}")
                if col2.button("Supprimer", key=f"del_kw_{kw['id']}"):
                    supabase.table("config_mots_cles").delete().eq("id", kw['id']).execute()
                    st.rerun()
    except Exception as e:
        st.error(f"Impossible de charger les mots-clés : {e}")

# --- TAB 3 : GESTION DES SITES ---
with tab3:
    st.subheader("Ajouter une nouvelle plateforme instantanément")
    
    with st.form("add_site_auto_form"):
        nom_site = st.text_input("Nom de la plateforme à ajouter", placeholder="Ex: Tutti, Ricardo, Anibis...")
        
        if st.form_submit_button("🔍 Trouver et Activer le site"):
            if nom_site:
                with st.spinner(f"Gemini cherche le flux réseau pour '{nom_site}'..."):
                    url_detectee = trouver_url_api_via_ia(nom_site)
                    
                if url_detectee:
                    try:
                        supabase.table("config_sites").insert({
                            "nom_site": nom_site.capitalize().strip(),
                            "url_cible": url_detectee,
                            "actif": True
                        }).execute()
                        st.success(f"🎉 Configuration réussie ! '{nom_site}' a été trouvé et ajouté automatiquement.")
                        st.info(f"🔗 URL configurée en tâche de fond : `{url_detectee}`")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de l'enregistrement dans la base : {e}")
                else:
                    st.error("Impossible de configurer ce site automatiquement. Vérifie le nom.")
            else:
                st.warning("Veuillez écrire un nom de site.")

    st.markdown("---")
    st.subheader("Plateformes actuellement surveillées")
    
    try:
        sites = supabase.table("config_sites").select("*").execute()
        if not sites.data:
            st.info("Aucun site configuré pour le moment.")
        else:
            for s in sites.data:
                with st.expander(f"🌐 {s['nom_site']}"):
                    st.write(f"**URL auto-détectée :** `{s['url_cible']}`")
                    status = "ACTIF" if s['actif'] else "DÉSACTIVÉ"
                    st.write(f"**Statut :** {status}")
                    
                    col_act, col_supp = st.columns([1, 1])
                    
                    label_bouton = "Désactiver" if s['actif'] else "Activer"
                    if col_act.button(label_bouton, key=f"toggle_site_{s['id']}"):
                        supabase.table("config_sites").update({"actif": not s['actif']}).eq("id", s['id']).execute()
                        st.rerun()
                        
                    if col_supp.button("🗑️ Supprimer", key=f"del_site_{s['id']}"):
                        supabase.table("config_sites").delete().eq("id", s['id']).execute()
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Impossible de charger les sites : {e}")