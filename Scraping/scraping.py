import requests
from bs4 import BeautifulSoup
import json
import re
import warnings
import logging
from urllib.parse import quote
from textblob import TextBlob
from textblob_fr import PatternTagger, PatternAnalyzer
import requests
import logging

HUGGINGFACE_API_KEY = "TON_API_KEY_ICI"  # Ajoute ta clé API ici

def optimize_query_with_ai(user_prompt):
    """
    Envoie le prompt utilisateur à un modèle de langage IA pour reformuler la requête en un mot-clé précis pour Wikipédia.
    """
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    # Construire une requête adaptée à Wikipédia
    formatted_prompt = f"Réécris cette question pour qu'elle corresponde exactement au titre d'une page Wikipédia existante dans le domaine historique : {user_prompt}"

    data = {"inputs": formatted_prompt, "parameters": {"max_length": 50}}

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            optimized_query = result[0]["generated_text"]
            logging.info(f"✅ Requête optimisée : {optimized_query}")
            return optimized_query
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur API Hugging Face : {e}")
    
    return user_prompt  # Retourne le prompt original en cas d'erreur


# Configuration du logging pour le debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.simplefilter("ignore", ResourceWarning)

EXCLUDED_TERMS = ["film", "série télévisée", "jeux vidéo", "album", "chanson", "bande dessinée", "roman", "fiction"]
ROMAN_NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]

HISTORICAL_KEYWORDS = [
    "histoire", "événement", "bataille", "révolution", "empire", "antiquité",
    "moyen âge", "renaissance", "siècle", "guerre", "traité", "dynastie",
    "monarchie", "royaume", "empereur", "roi", "reine", "président", "premier ministre",
    "constitution", "colonie", "conflit", "armée", "napoléon", "charlemagne",
    "république", "civilisation", "explorateur", "invention", "mémorial", "aristocratie","Préhistoire_de_la_France",
    "Gaule",
    "Conquête_de_la_Gaule",
    "Guerre_des_Gaules",
    "Vercingétorix",
    "Province_romaine",
    "Francs",
    "Clovis_Ier",
    "Dynastie_mérovingienne",
    "Charles_Martel",
    "Bataille_de_Poitiers_(732)",
    "Pépin_le_Bref",
    "Dynastie_carolingienne",
    "Charlemagne",
    "Empire_carolingien",
    "Traité_de_Verdun",
    "Hugues_Capet",
    "Dynastie_capétienne",
    "Philippe_Auguste",
    "Guerre_de_Cent_Ans",
    "Jeanne_d'Arc",
    "Charles_VII",
    "Louis_XI",
    "François_Ier",
    "Renaissance_française",
    "Guerres_de_Religion_(France)",
    "Massacre_de_la_Saint-Barthélemy",
    "Henri_IV",
    "Édit_de_Nantes",
    "Louis_XIII",
    "Cardinal_Richelieu",
    "Louis_XIV",
    "Versailles",
    "Guerre_de_Trente_Ans",
    "Colbert",
    "Louis_XV",
    "Guerre_de_Sept_Ans",
    "Louis_XVI",
    "Révolution_française",
    "Prise_de_la_Bastille",
    "Déclaration_des_droits_de_l'homme_et_du_citoyen",
    "Convention_nationale",
    "Exécution_de_Louis_XVI",
    "Terreur_(Révolution_française)",
    "Directoire",
    "Consulat_(France)",
    "Napoléon_Bonaparte",
    "Premier_Empire",
    "Bataille_d'Austerlitz",
    "Campagne_de_Russie",
    "Bataille_de_Waterloo",
    "Congrès_de_Vienne",
    "Restauration_(histoire_de_France)",
    "Charles_X",
    "Révolution_de_Juillet",
    "Louis-Philippe_Ier",
    "Monarchie_de_Juillet",
    "Révolution_française_de_1848",
    "Seconde_République_(France)",
    "Louis-Napoléon_Bonaparte",
    "Coup_d'État_du_2_décembre_1851",
    "Second_Empire",
    "Guerre_de_Crimée",
    "Guerre_franco-allemande_de_1870",
    "Commune_de_Paris_(1871)",
    "Troisième_République_(France)",
    "Affaire_Dreyfus",
    "Colonisation_française",
    "Première_Guerre_mondiale",
    "Bataille_de_Verdun",
    "Traité_de_Versailles_(1919)",
    "Entre-deux-guerres",
    "Front_populaire_(France)",
    "Seconde_Guerre_mondiale",
    "Appel_du_18_Juin",
    "Régime_de_Vichy",
    "Libération_de_la_France",
    "Quatrième_République_(France)",
    "Guerre_d'Indochine",
    "Guerre_d'Algérie",
    "Charles_de_Gaulle",
    "Cinquième_République",
    "Mai_68",
    "François_Mitterrand",
    "Traité_de_Maastricht",
    "Jacques_Chirac",
    "Nicolas_Sarkozy",
    "François_Hollande",
    "Emmanuel_Macron",
    "Union_européenne",
    "Histoire_militaire_de_la_France",
    "Histoire_économique_de_la_France",
    "Histoire_culturelle_de_la_France",
    "Histoire_de_la_France_contemporaine",
    "Politique_de_la_France",
    "Économie_de_la_France",
    "Culture_de_la_France",
    "Démographie_de_la_France"
]

def correct_spelling_api(text):
    """Corrige les fautes d'orthographe via LanguageTool."""
    url = "https://api.languagetool.org/v2/check"
    params = {"text": text, "language": "fr"}

    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur API LanguageTool : {e}")
        return text

    result = response.json()
    corrected_text = text
    for match in result.get("matches", []):
        replacement = match["replacements"][0]["value"] if match["replacements"] else None
        if replacement:
            corrected_text = corrected_text[:match["offset"]] + replacement + corrected_text[match["offset"] + match["length"]:]

    return corrected_text

def extract_main_keyword(text):
    """Extrait le mot-clé principal en tenant compte des noms propres, chiffres romains et expressions historiques."""
    words = text.split()

    # Mots interrogatifs et inutiles à ignorer
    question_words = {"qui", "quand", "où", "comment", "quel", "quelle", "quelles", "quels", "pourquoi", "est", "sont"}

    # Expressions historiques courantes à préserver
    important_phrases = {"histoire de", "bataille de", "révolution de", "guerre de"}

    # Vérifier si la phrase contient une expression historique connue
    for phrase in important_phrases:
        if phrase in text.lower():
            return text  # Retourne la phrase complète si elle est reconnue

    # Vérifier les noms propres et chiffres romains
    proper_nouns = []
    historical_terms = []

    i = 0
    while i < len(words):
        word = words[i].strip("?").strip(",")  # Nettoie la ponctuation

        # Vérifier que le mot n'est pas vide avant d'accéder à word[0]
        if not word:
            i += 1
            continue

        # Ignorer les mots interrogatifs
        if word.lower() in question_words:
            i += 1
            continue

        # Détecter les noms propres (majuscule)
        if word[0].isupper():
            temp = word

            # Vérifie si c'est un nom propre avec chiffre romain (ex: "Henri IV")
            if i + 1 < len(words) and words[i + 1] in ROMAN_NUMERALS:
                temp += " " + words[i + 1]
                i += 1

            proper_nouns.append(temp)

        # Vérifie si c'est un mot-clé historique
        elif word.lower() in HISTORICAL_KEYWORDS:
            historical_terms.append(word)

        i += 1

    # Prend un nom propre s'il y en a un
    if proper_nouns:
        return " ".join(proper_nouns)

    # Sinon, prend un mot-clé historique
    if historical_terms:
        return " ".join(historical_terms)

    # Si rien n'est pertinent, retourne la phrase complète
    return text

def search_wikipedia(query):
    """Recherche Wikipédia en suivant automatiquement la redirection."""
    logging.debug(f"🔍 Recherche Wikipédia pour : {query}")
    search_url = f"https://fr.wikipedia.org/w/index.php?search={quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=5, allow_redirects=True)
        response.raise_for_status()
        
        # Vérifie si Wikipédia a redirigé directement vers une page
        if response.url.startswith("https://fr.wikipedia.org/wiki/"):
            logging.debug(f"✅ Redirection suivie : {response.url}")
            return response.url

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur Wikipédia : {e}")
        return None

    # Si pas de redirection directe, alors on scrute les résultats
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("div", class_="mw-search-result-heading")

    for result in results:
        link = result.find("a")
        if link:
            page_url = f"https://fr.wikipedia.org{link['href']}"
            if not any(term in page_url.lower() for term in EXCLUDED_TERMS):
                return page_url

    logging.warning("⚠ Aucune page pertinente trouvée.")
    return None

def get_historical_data(user_query):
    """Exécute la recherche, optimise le prompt avec IA et récupère les données Wikipédia."""
    original_prompt = user_query  # 🔹 Sauvegarde le prompt original

    corrected_query = correct_spelling_api(user_query)  # 🔹 Correction orthographique
    logging.debug(f"Correction orthographique : {user_query} → {corrected_query}")

    optimized_query = optimize_query_with_ai(corrected_query)  # 🔹 Optimisation avec IA
    logging.debug(f"Requête IA optimisée : {optimized_query}")

    wikipedia_url = search_wikipedia(optimized_query)

    if wikipedia_url:
        # 🔹 Scraping du contenu de la page Wikipédia
        try:
            response = requests.get(wikipedia_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 🔹 Récupère le titre de la page
            title = soup.find("h1").text.strip()

            # 🔹 Récupère tout le contenu des paragraphes
            paragraphs = soup.find_all("p")
            content = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            wikipedia_data = {
                "prompt_utilisateur": original_prompt,
                "recherche_wikipedia": optimized_query,
                "titre": title,
                "source": wikipedia_url,
                "contenu": content
            }

            logging.info(f"✅ Scraping réussi pour : {title}")

        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Erreur lors du scraping Wikipédia : {e}")
            wikipedia_data = {
                "prompt_utilisateur": original_prompt,
                "recherche_wikipedia": optimized_query,
                "titre": "Erreur",
                "source": wikipedia_url,
                "contenu": "Erreur de récupération du contenu."
            }

    else:
        wikipedia_data = {
            "prompt_utilisateur": original_prompt,
            "recherche_wikipedia": optimized_query,
            "titre": "Aucune donnée trouvée",
            "source": "Aucune source disponible",
            "contenu": "Aucune donnée historique disponible."
        }
        logging.warning("⚠ Scraping échoué : aucune donnée trouvée.")

    # 🔹 Sauvegarde des données dans un fichier JSON
    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(wikipedia_data, f, ensure_ascii=False, indent=4)
        logging.debug("📁 Données sauvegardées dans data.json")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'écriture du fichier JSON : {e}")

    return wikipedia_data

if __name__ == "__main__":
    user_query = input("Posez une question historique : ")
    result = get_historical_data(user_query)

    print(f"\n🔍 Recherche pour : {result['mot_cle']}\n🔗 {result['source']}\n{result['contenu'][:500]}...")
