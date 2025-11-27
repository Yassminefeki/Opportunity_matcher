import unittest
from scraper import USSOpportunitiesScraper
from unittest.mock import patch, MagicMock
import requests

class TestScraper(unittest.TestCase):

    @patch('scraper.requests.get')
    def test_get_page_success(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        scraper = USSOpportunitiesScraper()
        response = scraper.get_page("http://test.com")

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

    @patch('scraper.requests.get')
    def test_get_page_failure(self, mock_get):
        # Mock a failed response
        mock_get.side_effect = requests.exceptions.RequestException("Failed to connect")

        scraper = USSOpportunitiesScraper()
        response = scraper.get_page("http://test.com")

        self.assertIsNone(response)

if __name__ == '__main__':
    unittest.main()
