import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scraping.scraping import correct_spelling, refine_query, search_wikipedia, scrape_wikipedia

class TestQueryProcessing(unittest.TestCase):

    def test_correct_spelling(self):
        """Vérifie que la correction orthographique fonctionne sur divers cas."""
        self.assertEqual(correct_spelling("revoluttion"), "révolution")
        self.assertEqual(correct_spelling("bataill"), "bataille")
        self.assertEqual(correct_spelling("monarshie"), "monarchie")
        self.assertEqual(correct_spelling("guerre"), "guerre")  # Doit rester inchangé
        self.assertEqual(correct_spelling("Napoléon"), "Napoléon")  # Les noms propres doivent rester inchangés

    def test_refine_query(self):
        """Vérifie que la reformulation de la requête est correcte pour divers cas historiques."""
        self.assertEqual(refine_query("quand la révolution française a commencé"), "Date de la révolution française histoire")
        self.assertEqual(refine_query("ou s'est déroulée la bataille de Waterloo"), "Lieu de la bataille de waterloo histoire")
        self.assertEqual(refine_query("comment a été signé le traité de Versailles"), "Explication sur le traité de versailles histoire")
        self.assertEqual(refine_query("qui est Louis XIV"), "Biographie de louis xiv histoire")

class TestWikipediaSearch(unittest.TestCase):

    def test_search_wikipedia_valid(self):
        """Vérifie que la recherche Wikipédia retourne une URL correcte pour plusieurs événements historiques."""
        queries = ["Révolution française", "Bataille de Stalingrad", "Louis XIV", "Empire romain", "Traité de Versailles"]

        for query in queries:
            with self.subTest(query=query):  # Exécute chaque test indépendamment
                url = search_wikipedia(query)
                self.assertIsNotNone(url, f"Échec pour la requête : {query}")
                self.assertTrue(url.startswith("https://fr.wikipedia.org/wiki/"), f"Mauvaise URL : {url}")

class TestWikipediaScraping(unittest.TestCase):

    def test_scrape_wikipedia_valid(self):
        """Vérifie que le scraping Wikipédia retourne un article valide avec du contenu."""
        queries = ["Révolution française", "Guerre froide", "Napoléon Bonaparte"]

        for query in queries:
            with self.subTest(query=query):
                data = scrape_wikipedia(query)
                self.assertIn(query.split()[0], data["titre"], f"Le titre de l'article ne correspond pas pour {query}")
                self.assertTrue(len(data["contenu"]) > 500, f"Le contenu de l'article est trop court pour {query}")

if __name__ == '__main__':
    unittest.main()
