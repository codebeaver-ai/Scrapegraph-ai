import unittest

from scrapegraphai.docloaders.scrape_do import scrape_do_fetch
from unittest.mock import MagicMock, patch

class TestScrapeDo(unittest.TestCase):
    @patch('scrapegraphai.docloaders.scrape_do.requests.get')
    def test_scrape_do_fetch_with_proxy_and_geocode(self, mock_get):
        # Arrange
        token = 'test_token'
        target_url = 'https://example.com'
        use_proxy = True
        geoCode = 'US'
        super_proxy = False

        mock_response = MagicMock()
        mock_response.text = 'Mocked response content'
        mock_get.return_value = mock_response

        # Act
        result = scrape_do_fetch(token, target_url, use_proxy, geoCode, super_proxy)

        # Assert
        self.assertEqual(result, 'Mocked response content')
        mock_get.assert_called_once_with(
            target_url,
            proxies={
                'http': f'http://{token}:@proxy.scrape.do:8080',
                'https': f'http://{token}:@proxy.scrape.do:8080'
            },
            verify=False,
            params={'geoCode': 'US', 'super': 'false'}
        )