import requests
from bs4 import BeautifulSoup
import json
import re
import warnings
from spellchecker import SpellChecker

warnings.simplefilter("ignore", ResourceWarning)

EXCLUDED_TERMS = ["film", "série télévisée", "jeux vidéo", "album", "chanson", "bande dessinée", "roman", "fiction"]
HISTORICAL_KEYWORDS = ["histoire", "événement", "bataille", "révolution", "empire", "antiquité", 
                       "moyen âge", "renaissance", "siècle", "guerre", "traité", "dynastie", 
                       "monarchie", "royaume", "empereur"]

def correct_spelling(text):
    """Corrige les fautes d'orthographe en français sans modifier les noms propres"""
    spell = SpellChecker(language="fr")
    words = text.split()
    
    corrected_words = []
    for word in words:
        corrected = spell.correction(word)
        
        # 🔹 Éviter les corrections absurdes
        if corrected is None or corrected.lower() in ["duel", "nuisance", "automobile", "napoleon"]:
            corrected_words.append(word)
        else:
            corrected_words.append(corrected)
    
    return " ".join(corrected_words)

def refine_query(user_query):
    """Corrige la requête et l'améliore pour la rendre plus pertinente historiquement."""
    
    user_query = correct_spelling(user_query)
    
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
        user_query += " histoire"

    return user_query

def search_wikipedia(query):
    query = refine_query(query)
    search_url = f"https://fr.wikipedia.org/w/index.php?search={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête Wikipédia : {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("div", class_="mw-search-result-heading")

    for result in results:
        link = result.find("a")
        if link:
            relative_link = link["href"]
            page_url = f"https://fr.wikipedia.org{relative_link}"

            if not any(term in page_url.lower() for term in EXCLUDED_TERMS):
                return page_url

    return None

def scrape_wikipedia(query):
    wikipedia_url = search_wikipedia(query)

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

    content = ""
    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if text:
            content += text + "\n\n"

    return {"titre": title, "source": wikipedia_url, "contenu": content}

def get_historical_data(user_query):
    refined_query = refine_query(user_query)
    print(f"🔍 Recherche pour : {refined_query}...")

    wikipedia_data = scrape_wikipedia(refined_query)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(wikipedia_data, f, ensure_ascii=False, indent=4)

    print("✅ Scraping terminé ! L'article historique est stocké dans data.json")
    return wikipedia_data

if __name__ == "__main__":
    user_query = input("Posez une question historique : ")
    result = get_historical_data(user_query)

    print(f"\n📜 {result['titre']}\n🔗 {result['source']}\n{result['contenu'][:1000]}...")
