"""Pytest configuration and fixtures."""

import asyncio
import os
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    with patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test-api-key"}):
        yield "test-api-key"


@pytest.fixture
def sample_paper():
    """Sample paper data for testing."""
    return {
        "paperId": "test123",
        "title": "Sample Paper Title",
        "authors": [
            {"name": "John Doe", "authorId": "author1"},
            {"name": "Jane Smith", "authorId": "author2"},
        ],
        "year": 2023,
        "venue": "Test Conference",
        "citationCount": 42,
        "abstract": "This is a sample abstract for testing purposes.",
        "references": [{"paperId": "ref1"}, {"paperId": "ref2"}],
        "citations": [{"paperId": "cite1"}],
        "openAccessPdf": {"url": "http://example.com/paper.pdf"},
    }


@pytest.fixture
def sample_author():
    """Sample author data for testing."""
    return {
        "authorId": "author123",
        "name": "Dr. Sample Author",
        "paperCount": 50,
        "citationCount": 1000,
        "hIndex": 25,
        "papers": [
            {"title": "Recent Paper 1", "year": 2023, "citationCount": 15},
            {"title": "Recent Paper 2", "year": 2022, "citationCount": 25},
        ],
    }


@pytest.fixture
def sample_search_response():
    """Sample search response for testing."""
    return {
        "data": [
            {
                "paperId": "paper1",
                "title": "First Paper",
                "authors": [{"name": "Author One"}],
                "year": 2023,
                "venue": "Conference A",
                "citationCount": 10,
            },
            {
                "paperId": "paper2",
                "title": "Second Paper",
                "authors": [{"name": "Author Two"}],
                "year": 2022,
                "venue": "Conference B",
                "citationCount": 5,
            },
        ],
        "total": 2,
    }


@pytest.fixture
def sample_citation_response():
    """Sample citation response for testing."""
    return {
        "data": [
            {
                "citingPaper": {
                    "paperId": "citing1",
                    "title": "Paper That Cites",
                    "authors": [{"name": "Citing Author"}],
                    "year": 2024,
                    "citationCount": 3,
                }
            }
        ],
        "total": 1,
    }


@pytest.fixture
def sample_reference_response():
    """Sample reference response for testing."""
    return {
        "data": [
            {
                "citedPaper": {
                    "paperId": "cited1",
                    "title": "Referenced Paper",
                    "authors": [{"name": "Referenced Author"}],
                    "year": 2020,
                    "citationCount": 100,
                }
            }
        ],
        "total": 1,
    }
