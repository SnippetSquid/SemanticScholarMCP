"""Tests for the Semantic Scholar MCP server."""

from unittest.mock import patch

import pytest

from semantic_scholar_mcp.server import (
    create_safe_filename,
    download_paper_pdf,
    format_author,
    format_paper,
    get_author,
    get_citation_context,
    get_paper,
    get_paper_batch,
    get_paper_citations,
    get_paper_pdf_info,
    get_paper_references,
    make_api_request,
    search_authors,
    search_papers,
    search_snippets,
    set_pdf_metadata,
)


class TestApiRequest:
    """Test the make_api_request function."""

    @pytest.mark.asyncio
    async def test_successful_get_request(self, httpx_mock):
        """Test successful GET request."""
        mock_response = {"data": [{"title": "Test Paper"}]}

        httpx_mock.add_response(
            method="GET",
            url="https://api.semanticscholar.org/graph/v1/paper/search?query=test",
            json=mock_response,
        )

        result = await make_api_request("paper/search", {"query": "test"})
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test HTTP error handling."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = (
                Exception("HTTP error")
            )

            result = await make_api_request("paper/search", {"query": "test"})
            assert "error" in result
            assert "Request failed" in result["error"]

    @pytest.mark.asyncio
    async def test_rate_limit_error_no_api_key(self, httpx_mock):
        """Test rate limit error handling without API key."""
        # Mock no API key
        with patch("semantic_scholar_mcp.server.API_KEY", None):
            httpx_mock.add_response(
                method="GET",
                url="https://api.semanticscholar.org/graph/v1/paper/search?query=test",
                status_code=403,
            )

            result = await make_api_request("paper/search", {"query": "test"})
            assert "error" in result
            assert "shared public rate limit (1000 req/sec)" in result["error"]
            assert "semanticscholar.org/product/api" in result["error"]

    @pytest.mark.asyncio
    async def test_rate_limit_error_with_api_key(self, httpx_mock):
        """Test rate limit error handling with API key."""
        # Mock the API_KEY global variable
        with patch("semantic_scholar_mcp.server.API_KEY", "test-key"):
            httpx_mock.add_response(
                method="GET",
                url="https://api.semanticscholar.org/graph/v1/paper/search?query=test",
                status_code=403,
            )

            result = await make_api_request("paper/search", {"query": "test"})
            assert "error" in result
            assert "API key may be invalid or rate limit exceeded" in result["error"]

    @pytest.mark.asyncio
    async def test_429_error_handling(self, httpx_mock):
        """Test 429 rate limit error handling."""
        httpx_mock.add_response(
            method="GET",
            url="https://api.semanticscholar.org/graph/v1/paper/search?query=test",
            status_code=429,
        )

        result = await make_api_request("paper/search", {"query": "test"})
        assert "error" in result
        assert "Rate limit exceeded" in result["error"]
        assert "dedicated higher limits" in result["error"]


class TestFormatting:
    """Test formatting functions."""

    def test_format_paper(self):
        """Test paper formatting."""
        paper = {
            "title": "Test Paper",
            "authors": [{"name": "John Doe"}, {"name": "Jane Smith"}],
            "year": 2023,
            "venue": "Test Conference",
            "citationCount": 42,
            "paperId": "test123",
        }

        result = format_paper(paper)
        assert "Test Paper" in result
        assert "John Doe, Jane Smith" in result
        assert "(2023)" in result
        assert "Test Conference" in result
        assert "Citations: 42" in result
        assert "Paper ID: test123" in result

    def test_format_paper_many_authors(self):
        """Test paper formatting with many authors."""
        paper = {
            "title": "Test Paper",
            "authors": [
                {"name": "Author 1"},
                {"name": "Author 2"},
                {"name": "Author 3"},
                {"name": "Author 4"},
                {"name": "Author 5"},
            ],
            "year": 2023,
            "citationCount": 10,
            "paperId": "test123",
        }

        result = format_paper(paper)
        assert "Author 1, Author 2, Author 3 (and 2 others)" in result

    def test_format_author(self):
        """Test author formatting."""
        author = {
            "name": "John Doe",
            "authorId": "author123",
            "paperCount": 50,
            "citationCount": 1000,
            "hIndex": 25,
        }

        result = format_author(author)
        assert "John Doe" in result
        assert "author123" in result
        assert "Papers: 50" in result
        assert "Citations: 1000" in result
        assert "H-Index: 25" in result


class TestSearchPapers:
    """Test the search_papers tool."""

    @pytest.mark.asyncio
    async def test_search_papers_success(self):
        """Test successful paper search."""
        mock_response = {
            "data": [
                {
                    "title": "Test Paper",
                    "authors": [{"name": "John Doe"}],
                    "year": 2023,
                    "venue": "Test Conference",
                    "citationCount": 10,
                    "paperId": "test123",
                }
            ],
            "total": 1,
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await search_papers("machine learning", limit=10)

            assert "Found 1 total papers" in result
            assert "Test Paper" in result
            assert "John Doe" in result

    @pytest.mark.asyncio
    async def test_search_papers_no_results(self):
        """Test paper search with no results."""
        mock_response = {"data": [], "total": 0}

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await search_papers("nonexistent query")

            assert "No papers found" in result

    @pytest.mark.asyncio
    async def test_search_papers_error(self):
        """Test paper search with API error."""
        mock_response = {"error": "API error"}

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await search_papers("test query")

            assert "Error: API error" in result


class TestGetPaper:
    """Test the get_paper tool."""

    @pytest.mark.asyncio
    async def test_get_paper_success(self):
        """Test successful paper retrieval."""
        mock_response = {
            "title": "Test Paper",
            "authors": [{"name": "John Doe"}],
            "year": 2023,
            "venue": "Test Conference",
            "citationCount": 10,
            "paperId": "test123",
            "abstract": "This is a test abstract.",
            "references": [{"paperId": "ref1"}],
            "citations": [{"paperId": "cite1"}],
            "openAccessPdf": {"url": "http://example.com/paper.pdf"},
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_paper("test123")

            assert "Test Paper" in result
            assert "John Doe" in result
            assert "This is a test abstract" in result
            assert "References: 1" in result
            assert "Cited by: 1" in result
            assert "http://example.com/paper.pdf" in result


class TestGetPaperBatch:
    """Test the get_paper_batch tool."""

    @pytest.mark.asyncio
    async def test_get_paper_batch_success(self):
        """Test successful batch paper retrieval."""
        mock_response = [
            {
                "title": "Paper 1",
                "authors": [{"name": "Author 1"}],
                "year": 2023,
                "citationCount": 5,
                "paperId": "paper1",
            },
            {
                "title": "Paper 2",
                "authors": [{"name": "Author 2"}],
                "year": 2022,
                "citationCount": 10,
                "paperId": "paper2",
            },
        ]

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_paper_batch("paper1,paper2")

            assert "Retrieved 2 papers" in result
            assert "Paper 1" in result
            assert "Paper 2" in result


class TestSearchAuthors:
    """Test the search_authors tool."""

    @pytest.mark.asyncio
    async def test_search_authors_success(self):
        """Test successful author search."""
        mock_response = {
            "data": [
                {
                    "name": "John Doe",
                    "authorId": "author123",
                    "paperCount": 50,
                    "citationCount": 1000,
                    "hIndex": 25,
                }
            ],
            "total": 1,
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await search_authors("John Doe")

            assert "Found 1 total authors" in result
            assert "John Doe" in result
            assert "Papers: 50" in result


class TestGetAuthor:
    """Test the get_author tool."""

    @pytest.mark.asyncio
    async def test_get_author_success(self):
        """Test successful author retrieval."""
        mock_response = {
            "name": "John Doe",
            "authorId": "author123",
            "paperCount": 50,
            "citationCount": 1000,
            "hIndex": 25,
            "papers": [{"title": "Recent Paper", "year": 2023, "citationCount": 15}],
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_author("author123")

            assert "John Doe" in result
            assert "Total Papers: 50" in result
            assert "H-Index: 25" in result
            assert "Recent Paper" in result


class TestSearchSnippets:
    """Test the search_snippets tool."""

    @pytest.mark.asyncio
    async def test_search_snippets_success(self):
        """Test successful snippet search."""
        mock_response = {
            "data": [
                {
                    "text": "This is a test snippet about machine learning.",
                    "paper": {"title": "ML Paper", "year": 2023},
                }
            ],
            "total": 1,
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await search_snippets("machine learning")

            assert "Found 1 total snippets" in result
            assert "This is a test snippet" in result
            assert "ML Paper (2023)" in result


class TestCitationTools:
    """Test citation and reference tools."""

    @pytest.mark.asyncio
    async def test_get_paper_citations_success(self):
        """Test successful citation retrieval."""
        mock_response = {
            "data": [
                {
                    "citingPaper": {
                        "title": "Citing Paper",
                        "authors": [{"name": "Author"}],
                        "year": 2024,
                        "citationCount": 5,
                        "paperId": "citing123",
                    }
                }
            ],
            "total": 1,
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_paper_citations("paper123")

            assert "Found 1 total citations" in result
            assert "Citing Paper" in result

    @pytest.mark.asyncio
    async def test_get_paper_references_success(self):
        """Test successful reference retrieval."""
        mock_response = {
            "data": [
                {
                    "citedPaper": {
                        "title": "Referenced Paper",
                        "authors": [{"name": "Author"}],
                        "year": 2020,
                        "citationCount": 100,
                        "paperId": "ref123",
                    }
                }
            ],
            "total": 1,
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_paper_references("paper123")

            assert "Found 1 total references" in result
            assert "Referenced Paper" in result

    @pytest.mark.asyncio
    async def test_get_citation_context_success(self):
        """Test successful citation context retrieval."""
        mock_response = {
            "contexts": [
                "This paper builds on the work of Smith et al. (2020).",
                "The methodology follows the approach described in the original paper.",
            ],
            "citingPaper": {"title": "Citing Paper"},
            "citedPaper": {"title": "Cited Paper"},
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_citation_context("cited123", "citing123")

            assert "Citation context:" in result
            assert "Citing Paper" in result
            assert "Cited Paper" in result
            assert "This paper builds on the work" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_api_request_failure(self):
        """Test API request failure handling."""
        with patch("semantic_scholar_mcp.server.make_api_request", return_value=None):
            result = await search_papers("test")
            assert "Error: Failed to fetch results" in result

    def test_format_paper_missing_fields(self):
        """Test paper formatting with missing fields."""
        paper = {"title": "Minimal Paper"}
        result = format_paper(paper)
        assert "Minimal Paper" in result
        assert "Unknown" in result or "0" in result

    def test_format_author_missing_fields(self):
        """Test author formatting with missing fields."""
        author = {"name": "Minimal Author"}
        result = format_author(author)
        assert "Minimal Author" in result
        assert "0" in result or "" in result


class TestPDFTools:
    """Test PDF-related functionality."""

    def test_create_safe_filename(self):
        """Test filename sanitization."""
        # Test normal title
        title = "Machine Learning: A Comprehensive Review"
        safe_name = create_safe_filename(title)
        assert safe_name == "Machine Learning A Comprehensive Review"

        # Test with problematic characters
        title_with_bad_chars = 'Deep Learning: "Computer Vision" & NLP <2023>'
        safe_name = create_safe_filename(title_with_bad_chars)
        assert safe_name == "Deep Learning Computer Vision & NLP 2023"

        # Test with forbidden characters
        title_forbidden = "Paper/Title\\With:Bad*Characters?"
        safe_name = create_safe_filename(title_forbidden)
        assert "/" not in safe_name
        assert "\\" not in safe_name
        assert ":" not in safe_name
        assert "*" not in safe_name
        assert "?" not in safe_name

        # Test length limiting
        long_title = "A" * 200  # Very long title
        safe_name = create_safe_filename(long_title, max_length=50)
        assert len(safe_name) <= 50

        # Test empty title
        empty_title = ""
        safe_name = create_safe_filename(empty_title)
        assert safe_name == "Unknown_Paper"

    def test_set_pdf_metadata_no_pypdf2(self):
        """Test metadata setting when PyPDF2 is not available."""
        import tempfile
        from pathlib import Path

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"fake pdf content")
            tmp_path = Path(tmp.name)

        try:
            # Mock PyPDF2 import failure
            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'PyPDF2'"),
            ):
                result = set_pdf_metadata(
                    tmp_path, "Test Title", [{"name": "Author"}], 2023
                )
                assert result is False
        finally:
            # Clean up
            tmp_path.unlink()

    @pytest.mark.asyncio
    async def test_get_paper_pdf_info_success(self):
        """Test PDF info retrieval."""
        mock_response = {
            "title": "Test Paper",
            "openAccessPdf": {"url": "http://example.com/paper.pdf"},
            "externalIds": {
                "ArXiv": "2301.12345",
                "DOI": "10.1000/test",
                "PubMed": "12345678",
            },
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_paper_pdf_info("test-paper-id")

            assert "✅ Open Access PDF Available" in result
            assert "http://example.com/paper.pdf" in result
            assert "ArXiv: https://arxiv.org/abs/2301.12345" in result
            assert "Publisher (DOI): https://doi.org/10.1000/test" in result

    @pytest.mark.asyncio
    async def test_get_paper_pdf_info_no_pdf(self):
        """Test PDF info when no PDF is available."""
        mock_response = {
            "title": "Test Paper",
            "openAccessPdf": None,
            "externalIds": {"DOI": "10.1000/test"},
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await get_paper_pdf_info("test-paper-id")

            assert "❌ No Open Access PDF Available" in result
            assert "Publisher (DOI): https://doi.org/10.1000/test" in result

    @pytest.mark.asyncio
    async def test_download_paper_pdf_no_pdf(self):
        """Test PDF download when no PDF is available."""
        mock_response = {
            "title": "Test Paper",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "openAccessPdf": None,
            "paperId": "test123",
        }

        with patch(
            "semantic_scholar_mcp.server.make_api_request", return_value=mock_response
        ):
            result = await download_paper_pdf("test-paper-id")

            assert "Error: No open access PDF available" in result

    @pytest.mark.asyncio
    async def test_download_paper_pdf_success(self, httpx_mock, tmp_path):
        """Test successful PDF download."""
        # Mock the paper info request
        mock_paper_response = {
            "title": "Test Paper",
            "authors": [{"name": "Test Author"}, {"name": "Second Author"}],
            "year": 2023,
            "openAccessPdf": {"url": "http://example.com/paper.pdf"},
            "paperId": "test123",
        }

        # Mock PDF content
        fake_pdf_content = b"%PDF-1.4 fake pdf content"

        # Setup mocks
        httpx_mock.add_response(
            method="GET",
            url="https://api.semanticscholar.org/graph/v1/paper/test-paper-id?fields=paperId%2Ctitle%2Cauthors%2Cyear%2CopenAccessPdf",
            json=mock_paper_response,
        )

        httpx_mock.add_response(
            method="GET",
            url="http://example.com/paper.pdf",
            content=fake_pdf_content,
            headers={"content-type": "application/pdf"},
        )

        # Test with custom download path
        with patch("semantic_scholar_mcp.server.set_pdf_metadata", return_value=True):
            result = await download_paper_pdf("test-paper-id", str(tmp_path))

            assert "✅ PDF downloaded successfully!" in result
            assert "Test Paper" in result
            assert "Test Author, Second Author" in result
            assert "2023" in result
            assert "✅ PDF metadata set" in result

            # Check that file was created
            expected_file = tmp_path / "Test Paper (2023).pdf"
            assert expected_file.exists()

            # Check file content
            with open(expected_file, "rb") as f:
                content = f.read()
                assert content == fake_pdf_content

    @pytest.mark.asyncio
    async def test_download_paper_pdf_duplicate_filename(self, httpx_mock, tmp_path):
        """Test PDF download with duplicate filename handling."""
        # Create an existing file
        existing_file = tmp_path / "Test Paper (2023).pdf"
        existing_file.write_bytes(b"existing content")

        mock_paper_response = {
            "title": "Test Paper",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "openAccessPdf": {"url": "http://example.com/paper.pdf"},
            "paperId": "test123",
        }

        fake_pdf_content = b"%PDF-1.4 fake pdf content"

        httpx_mock.add_response(
            method="GET",
            url="https://api.semanticscholar.org/graph/v1/paper/test-paper-id?fields=paperId%2Ctitle%2Cauthors%2Cyear%2CopenAccessPdf",
            json=mock_paper_response,
        )

        httpx_mock.add_response(
            method="GET",
            url="http://example.com/paper.pdf",
            content=fake_pdf_content,
            headers={"content-type": "application/pdf"},
        )

        with patch("semantic_scholar_mcp.server.set_pdf_metadata", return_value=True):
            result = await download_paper_pdf("test-paper-id", str(tmp_path))

            assert "✅ PDF downloaded successfully!" in result

            # Check that new file was created with (1) suffix
            expected_file = tmp_path / "Test Paper (2023) (1).pdf"
            assert expected_file.exists()

            # Original file should still exist
            assert existing_file.exists()

    @pytest.mark.asyncio
    async def test_download_paper_pdf_http_error(self, httpx_mock):
        """Test PDF download with HTTP error."""
        mock_paper_response = {
            "title": "Test Paper",
            "authors": [{"name": "Test Author"}],
            "year": 2023,
            "openAccessPdf": {"url": "http://example.com/paper.pdf"},
            "paperId": "test123",
        }

        httpx_mock.add_response(
            method="GET",
            url="https://api.semanticscholar.org/graph/v1/paper/test-paper-id?fields=paperId%2Ctitle%2Cauthors%2Cyear%2CopenAccessPdf",
            json=mock_paper_response,
        )

        httpx_mock.add_response(
            method="GET", url="http://example.com/paper.pdf", status_code=404
        )

        result = await download_paper_pdf("test-paper-id")

        assert "Error downloading PDF:" in result


if __name__ == "__main__":
    pytest.main([__file__])
