import asyncio
import unittest

from langchain_core.documents import Document
from scrapegraphai.docloaders.chromium import ChromiumLoader
from unittest.mock import AsyncMock, patch

class TestChromiumLoader(unittest.TestCase):
    @patch('scrapegraphai.docloaders.chromium.ChromiumLoader.ascrape_playwright')
    def test_lazy_load_yields_documents(self, mock_ascrape):
        # Setup
        urls = ['http://example.com', 'http://example.org']
        loader = ChromiumLoader(urls)
        mock_ascrape.side_effect = ['<html>Example 1</html>', '<html>Example 2</html>']

        # Execute
        documents = list(loader.lazy_load())

        # Assert
        self.assertEqual(len(documents), 2)
        self.assertIsInstance(documents[0], Document)
        self.assertIsInstance(documents[1], Document)
        self.assertEqual(documents[0].page_content, '<html>Example 1</html>')
        self.assertEqual(documents[0].metadata, {'source': 'http://example.com'})
        self.assertEqual(documents[1].page_content, '<html>Example 2</html>')
        self.assertEqual(documents[1].metadata, {'source': 'http://example.org'})

        # Verify that ascrape_playwright was called twice
        self.assertEqual(mock_ascrape.call_count, 2)