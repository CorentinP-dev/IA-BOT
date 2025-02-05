import requests
from bs4 import BeautifulSoup
import json
import logging
from urllib.parse import quote

# Configuration du logging pour le debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 Clé API Hugging Face (à renseigner)
HUGGINGFACE_API_KEY = "TON_API_KEY_ICI"

def optimize_query_with_ai(user_prompt):
    """
    Utilise une IA pour trouver directement l'URL de la page Wikipédia la plus pertinente.
    """
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    # 🔹 Demande à l'IA de rechercher l'URL exacte sur Wikipédia
    formatted_prompt = f"""
    Donne-moi uniquement l'URL Wikipédia la plus pertinente pour cette question sans ajouter de texte supplémentaire :
    {user_prompt}

    Réponds uniquement avec l'URL complète de la page Wikipédia en français.
    """

    data = {"inputs": formatted_prompt, "parameters": {"max_length": 150}}

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            wikipedia_url = result[0]["generated_text"].strip()

            # Vérifie si l'URL est valide et bien formée
            if wikipedia_url.startswith("https://fr.wikipedia.org/wiki/"):
                logging.info(f"✅ URL trouvée par l'IA : {wikipedia_url}")
                return wikipedia_url
            else:
                logging.warning("⚠ L'IA n'a pas retourné une URL Wikipédia valide.")
                return None
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur API Hugging Face : {e}")

    return None  # Retourne None si l'IA ne trouve pas d'URL

def search_wikipedia(query):
    """Recherche Wikipédia et suit les redirections pour obtenir l'URL de l'article le plus pertinent."""
    logging.debug(f"🔍 Recherche Wikipédia pour : {query}")
    search_url = f"https://fr.wikipedia.org/w/index.php?search={quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers, timeout=5, allow_redirects=True)
        response.raise_for_status()
        
        # 🔹 Si Wikipédia redirige directement vers un article
        if response.url.startswith("https://fr.wikipedia.org/wiki/"):
            logging.debug(f"✅ Redirection suivie : {response.url}")
            return response.url

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur Wikipédia : {e}")
        return None

    # 🔹 Si pas de redirection, recherche dans les résultats
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("div", class_="mw-search-result-heading")

    for result in results:
        link = result.find("a")
        if link:
            return f"https://fr.wikipedia.org{link['href']}"

    logging.warning("⚠ Aucune page pertinente trouvée.")
    return None

def scrape_wikipedia(url):
    """Scrape le contenu complet d'une page Wikipédia."""
    if not url:
        return None, None

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 🔹 Récupère le titre de la page
        title = soup.find("h1").text.strip()

        # 🔹 Récupère tous les paragraphes du corps de l'article
        paragraphs = soup.find_all("p")
        content = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        return title, content

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur lors du scraping de Wikipédia : {e}")
        return None, None

def get_historical_data(user_query):
    """Gère le pipeline : recherche IA sur Wikipédia et scraping du contenu."""
    original_prompt = user_query  # 🔹 Sauvegarde le prompt original

    wikipedia_url = optimize_query_with_ai(user_query)  # 🔹 Recherche directe via l'IA

    if wikipedia_url:
        title, content = scrape_wikipedia(wikipedia_url)
    else:
        title, content = None, None

    wikipedia_data = {
        "prompt_utilisateur": original_prompt,
        "source": wikipedia_url if wikipedia_url else "Aucune source disponible",
        "titre": title if title else "Aucune donnée trouvée",
        "contenu": content if content else "Aucune donnée historique disponible."
    }

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

    print(f"\n🔍 Recherche optimisée : {result['recherche_wikipedia']}\n🔗 {result['source']}\n📜 {result['titre']}\n\n{result['contenu'][:500]}...")
