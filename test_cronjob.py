import unittest
from flasknews import create_app, db
from cronjob import store_news_in_db
from unittest.mock import patch

class CronjobTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # testing hackernews cronjob
    @patch('cronjob.fetch_hackernews_items')
    def test_store_news_in_db(self, mock_fetch):
        mock_fetch.return_value = [{'title': 'Test News', 'time': 1234567890, 'url': 'https://test.com'}]
        store_news_in_db()

