import pytest

from scrapegraphai.utils.research_web import search_on_web  # Replace with actual path to your file
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