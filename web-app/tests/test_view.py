import unittest
from app import app

class TestViews(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        # Test the home page

if __name__ == '__main__':
    unittest.main()
