import requests
import json
import os
import re  # Ajouté pour extraire facilement les infos du flux RSS
from telegram_bot import envoyer_alerte
from database import supabase

FICHIER_MEMOIRE = "pianos_vus.json"

def charger_memoire():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def sauvegarder_memoire(liste_pianos):
    with open(FICHIER_MEMOIRE, "w", encoding="utf-8") as f:
        json.dump(liste_pianos, f, ensure_ascii=False, indent=4)

def chasser_les_nouveautes():
    print("🕵️‍♂️ Synchronisation des filtres avec Supabase...")
    
    # 1. Récupération des mots-clés du Dashboard
    try:
        res_mots = supabase.table("config_mots_cles").select("mot").eq("actif", True).execute()
        mots_cles = [row["mot"].lower() for row in res_mots.data] if res_mots.data else []
    except Exception as e:
        print(f"❌ Erreur de liaison Supabase (mots-clés) : {e}")
        return

    # 2. Récupération des sites
    try:
        res_sites = supabase.table("config_sites").select("*").eq("actif", True).execute()
        sites_a_scanner = res_sites.data if res_sites.data else []
    except Exception as e:
        print(f"❌ Erreur de liaison Supabase (sites) : {e}")
        return

    if not sites_a_scanner:
        print("📭 Aucun site configuré. En attente...")
        return

    if not mots_cles:
        print("🔍 Aucun mot-clé configuré. En attente...")
        return

    pianos_deja_vus = charger_memoire()
    nouveaux_pianos = []
    
    # EN-TÊTES ULTRA-COMPLETS POUR ÉVITER LE CODE 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    # 3. Boucle sur les plateformes
    for site in sites_a_scanner:
        url = site['url_cible'].strip()
        if not url.startswith("http"):
            print(f"⚠️ L'URL pour {site['nom_site']} semble incorrecte.")
            continue

        print(f"🌐 Connexion au flux manuel : {site['nom_site']}...")
        
        try:
            reponse = requests.get(url, headers=headers, timeout=15)
            if reponse.status_code != 200:
                print(f"⚠️ {site['nom_site']} indisponible (Code HTTP {reponse.status_code})")
                continue
            
            # --- CAS TRAITEMENT FLUX RSS (ANIBIS) ---
            if "rss" in url or "feeds" in url:
                # Extraction des balises <item> du RSS
                items = re.findall(r'<item>(.*?)</item>', reponse.text, re.DOTALL)
                
                for item in items:
                    titre = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                    titre = titre.group(1) if titre else re.search(r'<title>(.*?)</title>', item).group(1)
                    
                    lien = re.search(r'<link>(.*?)</link>', item).group(1).strip()
                    
                    # Extraction de l'ID unique de l'annonce depuis l'URL
                    id_match = re.search(r'-(\d+)\??', lien)
                    id_annonce = id_match.group(1) if id_match else lien
                    
                    texte_complet = titre.lower()
                    
                    if any(mot in texte_complet for mot in mots_cles):
                        if id_annonce not in pianos_deja_vus:
                            nouveaux_pianos.append({
                                "titre": titre,
                                "url": lien,
                                "id": id_annonce
                            })
            
            # --- CAS TRAITEMENT JSON TRADITIONNEL (AUTRES) ---
            else:
                donnees = reponse.json()
                annonces = donnees.get("entries", donnees.get("items", donnees.get("articles", [])))
                
                for index, item in enumerate(annonces):
                    id_annonce = str(item.get("id", f"{site['nom_site']}_{index}"))
                    titre = item.get("title", item.get("titre", "Sans titre"))
                    description = item.get("description", item.get("body", ""))
                    texte_complet = f"{titre} {description}".lower()
                    
                    if any(mot in texte_complet for mot in mots_cles):
                        if id_annonce not in pianos_deja_vus:
                            url_complete = url
                            if "tutti.ch" in url:
                                url_complete = f"https://www.tutti.ch/fr/vi/{id_annonce}"
                            elif "ricardo.ch" in url:
                                url_complete = f"https://www.ricardo.ch/fr/a/{id_annonce}"

                            nouveaux_pianos.append({
                                "titre": titre,
                                "url": url_complete,
                                "id": id_annonce
                            })
                                
        except Exception as e:
            print(f"⚠️ Impossible de scanner {site['nom_site']} : {e}")

    # 4. Envoi des alertes Telegram
    if nouveaux_pianos:
        print(f"🔥 {len(nouveaux_pianos)} opportunité(s) détectée(s) !")
        rapport = "🎹 *[NOUVEAU] Alertes du Chasseur !*\n\n"
        
        for piano in nouveaux_pianos:
            rapport += f"✨ [{piano['titre']}]({piano['url']})\n\n"
            try:
                supabase.table("annonces").insert({"titre": piano['titre']}).execute()
            except Exception as e:
                print(f"❌ Échec écriture Dashboard : {e}")
                
            pianos_deja_vus.append(piano["id"])
            
        envoyer_alerte(rapport)
        sauvegarder_memoire(pianos_deja_vus)
    else:
        print("📭 RAS : Rien de neuf sur tes plateformes.")
