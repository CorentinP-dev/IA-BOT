import unittest
import sys
import os

# Ajoute le dossier parent au chemin de recherche de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Scraping.scraping import correct_spelling, refine_query  # Ajuste le chemin selon ton projet

class TestQueryProcessing(unittest.TestCase):

    def test_correct_spelling(self):
        """ Vérifie si la correction orthographique fonctionne correctement """
        self.assertEqual(correct_spelling("revoluttion"), "révolution")
        self.assertEqual(correct_spelling("napolèon"), "napoléon")  # Vérifie un nom propre

    def test_refine_query(self):
        """ Vérifie si la reformulation de la requête est correcte """
        self.assertEqual(refine_query("quand napoléon est né"), "Date de napoléon histoire")
        self.assertEqual(refine_query("quel es la date de naisance de napoléon"), "Date de la naissance de napoléon histoire")

if __name__ == '__main__':
    unittest.main()


import unittest
from scraping import search_wikipedia

class TestWikipediaSearch(unittest.TestCase):

    def test_search_wikipedia_valid(self):
        """ Vérifie si la recherche Wikipédia retourne une URL correcte """
        url = search_wikipedia("Révolution française")
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("https://fr.wikipedia.org/wiki/"))

    def test_search_wikipedia_invalid(self):
        """ Vérifie que la recherche retourne None pour un terme inconnu """
        url = search_wikipedia("ajdhqkjshdqkjshdkqjshdkj")
        self.assertIsNone(url)

if __name__ == '__main__':
    unittest.main()

import unittest
from scraping import search_wikipedia

class TestWikipediaSearch(unittest.TestCase):

    def test_search_wikipedia_valid(self):
        """ Vérifie si la recherche Wikipédia retourne une URL correcte """
        url = search_wikipedia("Révolution française")
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("https://fr.wikipedia.org/wiki/"))

    def test_search_wikipedia_invalid(self):
        """ Vérifie que la recherche retourne None pour un terme inconnu """
        url = search_wikipedia("ajdhqkjshdqkjshdkqjshdkj")
        self.assertIsNone(url)

if __name__ == '__main__':
    unittest.main()
