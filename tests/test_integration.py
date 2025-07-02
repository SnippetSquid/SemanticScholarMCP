"""Integration tests for the Semantic Scholar MCP server."""

import asyncio
import os

import pytest

from semantic_scholar_mcp.server import (
    get_paper,
    search_authors,
    search_papers,
    search_snippets,
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestIntegration:
    """Integration tests that make real API calls."""

    @pytest.fixture(autouse=True)
    def check_api_key(self):
        """Skip integration tests if no API key is available."""
        if not os.getenv("SEMANTIC_SCHOLAR_API_KEY"):
            pytest.skip(
                "Integration tests require SEMANTIC_SCHOLAR_API_KEY environment variable"
            )

    async def test_search_papers_real_api(self):
        """Test real paper search with rate limiting."""
        result = await search_papers("machine learning", limit=2)

        assert "Found" in result
        assert "papers" in result
        assert len(result) > 100  # Should have substantial content

        # Add delay to respect rate limits
        await asyncio.sleep(1)

    async def test_get_paper_real_api(self):
        """Test real paper retrieval with a well-known paper."""
        # Using a well-known paper DOI
        result = await get_paper(
            "10.1038/nature14539", fields="title,authors,year,abstract"
        )

        assert "Title:" in result
        assert "Authors:" in result
        assert "Year:" in result

        # Add delay to respect rate limits
        await asyncio.sleep(1)

    async def test_search_authors_real_api(self):
        """Test real author search."""
        result = await search_authors("Geoffrey Hinton", limit=1)

        assert "Found" in result
        assert "authors" in result

        # Add delay to respect rate limits
        await asyncio.sleep(1)

    async def test_search_snippets_real_api(self):
        """Test real snippet search."""
        result = await search_snippets("neural networks", limit=2)

        # Note: Snippets might not always return results
        assert isinstance(result, str)
        assert len(result) > 0

        # Add delay to respect rate limits
        await asyncio.sleep(1)

    async def test_error_handling_invalid_paper_id(self):
        """Test error handling with invalid paper ID."""
        result = await get_paper("invalid-paper-id-that-does-not-exist")

        assert "Error:" in result or "not found" in result.lower()

        # Add delay to respect rate limits
        await asyncio.sleep(1)


@pytest.mark.performance
@pytest.mark.asyncio
class TestPerformance:
    """Performance tests for the MCP server."""

    async def test_search_response_time(self):
        """Test that search responses are reasonably fast."""
        import time

        start_time = time.time()
        result = await search_papers("test query", limit=5)
        end_time = time.time()

        response_time = end_time - start_time

        # Should respond within 10 seconds (allowing for network latency)
        assert response_time < 10.0
        assert isinstance(result, str)

    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        tasks = []

        # Create multiple concurrent search tasks
        for i in range(3):
            task = search_papers(f"query {i}", limit=2)
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All tasks should complete successfully
        for result in results:
            assert not isinstance(result, Exception)
            assert isinstance(result, str)

        # Add delay to respect rate limits
        await asyncio.sleep(2)


if __name__ == "__main__":
    # Run only unit tests by default
    pytest.main([__file__, "-m", "not integration and not performance"])
