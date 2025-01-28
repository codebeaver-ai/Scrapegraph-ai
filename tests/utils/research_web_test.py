import json
import pytest
import requests

from scrapegraphai.utils.research_web import filter_pdf_links, format_proxy, search_on_web, search_on_web  # Replace with actual path to your file
from unittest.mock import MagicMock, patch

def test_google_search():
    """Tests search_on_web with Google search engine."""
    results = search_on_web("test query", search_engine="Google", max_results=2)
    assert len(results) == 2
    # You can further assert if the results actually contain 'test query' in the title/snippet using additional libraries

def test_bing_search():
    """Tests search_on_web with Bing search engine."""
    results = search_on_web("test query", search_engine="Bing", max_results=1)
    assert results is not None
    # You can further assert if the results contain '.com' or '.org' in the domain

def test_invalid_search_engine():
    """Tests search_on_web with invalid search engine."""
    with pytest.raises(ValueError):
        search_on_web("test query", search_engine="Yahoo", max_results=5)

def test_max_results():
    """Tests search_on_web with different max_results values."""
    results_5 = search_on_web("test query", max_results=5)
    results_10 = search_on_web("test query", max_results=10)
    assert len(results_5) <= len(results_10)

def test_duckduckgo_search():
    """
    Tests search_on_web with DuckDuckGo search engine.
    This test mocks the DuckDuckGoSearchResults to avoid making actual API calls.
    """
    mock_results = "https://example.com, https://test.org"

    with patch('scrapegraphai.utils.research_web.DuckDuckGoSearchResults') as mock_ddg:
        mock_ddg_instance = MagicMock()
        mock_ddg_instance.run.return_value = mock_results
        mock_ddg.return_value = mock_ddg_instance

        results = search_on_web("test query", search_engine="duckduckgo", max_results=2)

        assert len(results) == 2
        assert "https://example.com" in results
        assert "https://test.org" in results

        mock_ddg.assert_called_once_with(max_results=2)
        mock_ddg_instance.run.assert_called_once_with("test query")

def test_filter_pdf_links():
    """
    Test the filter_pdf_links function to ensure it removes PDF links from the input list.
    """
    test_links = [
        "https://example.com/document.pdf",
        "https://example.com/page",
        "https://another.com/file.PDF",
        "https://test.org/index.html",
        "https://sample.net/report.pdf"
    ]

    filtered_links = filter_pdf_links(test_links)

    assert len(filtered_links) == 2
    assert "https://example.com/page" in filtered_links
    assert "https://test.org/index.html" in filtered_links
    assert not any(link.lower().endswith('.pdf') for link in filtered_links)

def test_serper_search():
    """
    Tests search_on_web with Serper search engine.
    This test mocks the requests.post method to simulate a Serper API response.
    """
    mock_response = {
        "organic": [
            {"link": "https://example.com"},
            {"link": "https://test.org"},
            {"link": "https://sample.net"}
        ]
    }

    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = MagicMock()

        results = search_on_web("test query", search_engine="serper", max_results=2, serper_api_key="fake_key")

        assert len(results) == 2
        assert "https://example.com" in results
        assert "https://test.org" in results

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs['headers']['X-API-KEY'] == "fake_key"
        assert kwargs['json']['q'] == "test query"
        assert kwargs['json']['num'] == 2

def test_searxng_search():
    """
    Tests search_on_web with SearXNG search engine.
    This test mocks the requests.get method to simulate a SearXNG API response.
    """
    mock_response = {
        "results": [
            {"url": "https://example.com"},
            {"url": "https://test.org"},
            {"url": "https://sample.net"}
        ]
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None

        results = search_on_web("test query", search_engine="searxng", max_results=2, port=8080)

        assert len(results) == 2
        assert "https://example.com" in results
        assert "https://test.org" in results

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "http://localhost:8080/search"
        assert kwargs['params']['q'] == "test query"
        assert kwargs['params']['format'] == "json"
        assert "google" in kwargs['params']['engines']

def test_format_proxy():
    """
    Test the format_proxy function with various input types and values.
    This test covers:
    1. Dictionary input with all required fields
    2. String input
    3. Dictionary input with missing fields
    4. Invalid input type
    """
    # Test with valid dictionary input
    proxy_dict = {"server": "192.168.1.1:8080", "username": "user", "password": "pass"}
    assert format_proxy(proxy_dict) == "http://user:pass@192.168.1.1:8080"

    # Test with valid string input
    proxy_str = "https://user:pass@192.168.1.1:8080"
    assert format_proxy(proxy_str) == proxy_str

    # Test with dictionary missing required fields
    invalid_dict = {"server": "192.168.1.1:8080", "username": "user"}
    with pytest.raises(ValueError, match="Proxy dictionary is missing required fields."):
        format_proxy(invalid_dict)

    # Test with invalid input type
    with pytest.raises(TypeError, match="Proxy should be a dictionary or a string."):
        format_proxy(123)

def test_search_timeout():
    """
    Test that search_on_web raises a TimeoutError when the request times out.
    This test mocks the requests.get method to simulate a timeout.
    """
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(TimeoutError) as exc_info:
            search_on_web("test query", search_engine="bing", timeout=5)

        assert str(exc_info.value) == "Search request timed out after 5 seconds"

        mock_get.assert_called_once()