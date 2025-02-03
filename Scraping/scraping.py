import requests
from bs4 import BeautifulSoup
import json
import re
from spellchecker import SpellChecker

spell = SpellChecker(language="fr")  # Détecte et corrige les fautes en français

def correct_spelling(user_query):
    """Corrige les fautes d'orthographe dans la requête utilisateur."""
    words = user_query.split()
    corrected_words = [spell.correction(word) if spell.correction(word) else word for word in words]
    return " ".join(corrected_words)


# === 🔍 Exclure les résultats non pertinents (films, jeux vidéo, etc.) ===
EXCLUDED_TERMS = ["film", "série télévisée", "jeux vidéo", "album", "chanson", "bande dessinée", "roman", "fiction"]

# === 🔍 Mots-clés pour forcer la recherche historique ===
HISTORICAL_KEYWORDS = ["histoire", "événement", "bataille", "révolution", "empire", "antiquité", "moyen âge", 
                        "renaissance", "siècle", "guerre", "traité", "dynastie", "monarchie", "royaume", "empereur"]

# === 📌 Fonction pour reformuler le prompt utilisateur ===
def refine_query(user_query):
    """Améliore la requête pour la rendre plus pertinente historiquement."""

    # Détection des questions et reformulation
    question_patterns = {
        r"quand (.+)": r"Date de \1",
        r"où (.+)": r"Lieu de \1",
        r"comment (.+)": r"Explication sur \1",
        r"qui est (.+)": r"Biographie de \1",
        r"quel est (.+)": r"Définition de \1",
        r"quelle est (.+)": r"Définition de \1",
        r"pourquoi (.+)": r"Raisons de \1",
    }

    user_query = user_query.lower().strip()

    for pattern, replacement in question_patterns.items():
        user_query = re.sub(pattern, replacement, user_query)

    if not any(word in user_query for word in HISTORICAL_KEYWORDS):
        user_query += f" {HISTORICAL_KEYWORDS[0]}"  # Ajoute "histoire" par défaut
    
    # Ajout d’un mot-clé historique si ce n’est pas déjà le cas
    if not any(word in user_query for word in HISTORICAL_KEYWORDS):
        user_query += f" {HISTORICAL_KEYWORDS[0]}"  # Ajoute "histoire" par défaut

    return user_query

# === 🔍 Trouver l'article Wikipédia le plus pertinent ===
def search_wikipedia(query):
    query = refine_query(query)  # Reformuler la requête
    search_url = f"https://fr.wikipedia.org/w/index.php?search={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête Wikipédia : {e}")
        return None  # En cas d'erreur

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("div", class_="mw-search-result-heading")

    for result in results:
        link = result.find("a")
        if link:
            relative_link = link["href"]
            page_url = f"https://fr.wikipedia.org{relative_link}"

            # Vérifier que l'article ne contient pas un mot-clé exclu
            if not any(term in page_url.lower() for term in EXCLUDED_TERMS):
                return page_url

    return None  # Aucun résultat pertinent

# === 📝 Scraper Wikipédia avec l'article complet ===
def scrape_wikipedia(query):
    wikipedia_url = search_wikipedia(query)  # Trouver la meilleure page

    if not wikipedia_url:
        return {"titre": query, "source": "Wikipédia", "contenu": "Aucune donnée historique trouvée sur Wikipédia."}

    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(wikipedia_url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du scraping Wikipédia : {e}")
        return {"titre": query, "source": wikipedia_url, "contenu": "Erreur de récupération."}

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1").text

    # Récupérer tout le contenu de l'article
    content = ""
    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if text:  # Ignorer les paragraphes vides
            content += text + "\n\n"

    return {"titre": title, "source": wikipedia_url, "contenu": content}


# === 📌 Fonction principale : Recherche et Scraping ===
def get_historical_data(user_query):
    refined_query = refine_query(user_query)  # Reformuler la requête
    print(f"🔍 Recherche pour : {refined_query}...")

    wikipedia_data = scrape_wikipedia(refined_query)

    # Sauvegarde dans un fichier JSON avec article complet
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(wikipedia_data, f, ensure_ascii=False, indent=4)

    print("✅ Scraping terminé ! L'article historique est stocké dans data.json")
    return wikipedia_data


# === ✨ Tester avec une requête utilisateur ===
if __name__ == "__main__":
    user_query = input("Posez une question historique : ")
    result = get_historical_data(user_query)

    print(f"\n📜 {result['titre']}\n🔗 {result['source']}\n{result['contenu'][:1000]}...")
