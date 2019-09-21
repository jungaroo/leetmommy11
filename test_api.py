""" Tests the api """
# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

from unittest import TestCase
from app import app

class TestAPIRoutes(TestCase):
    """ Tests API routes """

    def setUp(self):
        """Create test client """

        self.client = app.test_client()

    def test_ping(self):
        """ Tests if the ping works """
        resp = self.client.get("/api/ping")

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'success', resp.data)

    def test_index_search_validate_params(self):
        """Tests if index route validates parameters """
        
        resp = self.client.get("/api/index-search")
        self.assertIn(b'error', resp.data)

    def test_index_search_links(self):
        """Tests if index route returns links """
        resp = self.client.get("/api/index-search", query_string=dict(search="hi"))
        self.assertIn(b'links', resp.data)
        
    




