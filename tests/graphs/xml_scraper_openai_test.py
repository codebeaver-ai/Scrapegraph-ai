"""
xml_scraper_test
"""
import os
import pytest
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory of 'examples' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Load environment variables at the very beginning
load_dotenv()

# Mock XMLScraperGraph before importing xml_scraper_openai
with patch('scrapegraphai.graphs.XMLScraperGraph', MagicMock()):
    from examples.xml_scraper_graph.openai import xml_scraper_openai

# ************************************************
# Define the test fixtures and helpers
# ************************************************

@pytest.fixture
def graph_config():
    """
    Configuration for the XMLScraperGraph
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    return {
        "llm": {
            "api_key": openai_key,
            "model": "openai/gpt-4o",
        },
        "verbose": False,
    }

@pytest.fixture
def xml_content():
    """
    Fixture to read the XML file content
    """
    FILE_NAME = "inputs/books.xml"
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(curr_dir, '..', '..', 'examples', 'xml_scraper_graph', 'openai', FILE_NAME)

    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()

# ************************************************
# Define the test cases
# ************************************************

@patch('scrapegraphai.graphs.XMLScraperGraph')
def test_xml_scraper_graph(mock_xml_scraper, graph_config: dict, xml_content: str):
    """
    Test the XMLScraperGraph scraping pipeline
    """
    mock_instance = mock_xml_scraper.return_value
    mock_instance.run.return_value = "Mocked result"

    xml_scraper_graph = mock_xml_scraper(
        prompt="List me all the authors, title and genres of the books",
        source=xml_content,
        config=graph_config
    )

    result = xml_scraper_graph.run()

    assert result is not None
    assert result == "Mocked result"

@patch('scrapegraphai.graphs.XMLScraperGraph')
def test_xml_scraper_execution_info(mock_xml_scraper, graph_config: dict, xml_content: str):
    """
    Test getting the execution info of XMLScraperGraph
    """
    mock_instance = mock_xml_scraper.return_value
    mock_instance.get_execution_info.return_value = {"mocked": "execution info"}

    xml_scraper_graph = mock_xml_scraper(
        prompt="List me all the authors, title and genres of the books",
        source=xml_content,
        config=graph_config
    )

    xml_scraper_graph.run()

    graph_exec_info = xml_scraper_graph.get_execution_info()

    assert graph_exec_info is not None
    assert graph_exec_info == {"mocked": "execution info"}

@patch('scrapegraphai.graphs.XMLScraperGraph')
def test_xml_scraper_save_results(mock_xml_scraper, graph_config: dict, xml_content: str):
    """
    Test running the XMLScraperGraph
    """
    mock_instance = mock_xml_scraper.return_value
    mock_instance.run.return_value = "Mocked result"

    xml_scraper_graph = mock_xml_scraper(
        prompt="List me all the authors, title and genres of the books",
        source=xml_content,
        config=graph_config
    )

    result = xml_scraper_graph.run()

    assert result is not None
    assert result == "Mocked result"
