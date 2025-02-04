import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scraping.scraping import correct_spelling, refine_query, search_wikipedia, scrape_wikipedia

class TestQueryProcessing(unittest.TestCase):

    def test_correct_spelling(self):
        self.assertEqual(correct_spelling("revoluttion"), "révolution")
        self.assertEqual(correct_spelling("napolèon"), "napoléon")

    def test_refine_query(self):
        self.assertEqual(refine_query("quand napoléon est né"), "Date de napoléon histoire")

class TestWikipediaSearch(unittest.TestCase):

    def test_search_wikipedia_valid(self):
        url = search_wikipedia("Révolution française")
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("https://fr.wikipedia.org/wiki/"))

if __name__ == '__main__':
    unittest.main()
