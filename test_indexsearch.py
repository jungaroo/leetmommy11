""" Tests the search.
It uses the test index. See /helpers/create_test_pickle.py

the test index has :

        fake_index = {
            'hello' : { 1, 2, 3},
            'bye' : { 2, 3 },
            'good' : { 4, 5 },
            'bad' : { 1 }
        }
"""
# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

from unittest import TestCase
from classes import indexsearch

class TestIndexSearchFeature(TestCase):
    """ Tests API routes """

    def setUp(self):
        """Create IndexSearcher  """
        self.index_searcher = indexsearch.IndexSearcher('test')
    
    def test_single_search_word(self):
        """Tests that it works on a single search word """
        
        link_ids = self.index_searcher.search(["bye"])
        self.assertEquals({2, 3}, link_ids)

        empty_ids = self.index_searcher.search(["nothing"])
        self.assertEqual(set(), empty_ids)

    def test_multi_search_word(self):
        """ Tests that it works on multiple search words """

        link_ids = self.index_searcher.search(["bad", "hello"])
        self.assertEquals({1}, link_ids)

        link_ids2 = self.index_searcher.search(["bad", "hello", "good"])
        self.assertEquals(set(), link_ids2)


    

    