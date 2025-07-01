# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Semantic Scholar MCP Server is a Model Context Protocol (MCP) server providing access to the Semantic Scholar Academic Graph API. It offers 12 tools for searching papers/authors, retrieving citations/references, and downloading PDFs through an async HTTP interface.

## Development Commands

**Testing:**
```bash
make test                 # Run all tests
make test-unit           # Unit tests only (fast, no API calls)
make test-integration    # Integration tests (requires SEMANTIC_SCHOLAR_API_KEY)
make test-performance    # Performance/load tests
```

**Code Quality:**
```bash
make lint                # Run flake8, isort, black checks
make format              # Auto-format with black and isort
```

**Setup:**
```bash
make install-dev         # Install with dev dependencies
pip install -e ".[test,dev,metadata]"  # Alternative install
```

**Testing Individual Components:**
```bash
pytest tests/test_server.py::test_search_papers -v
pytest -m "not integration"  # Skip integration tests
pytest -k "test_format_paper"  # Run specific test patterns
```

## Architecture Overview

**Single-Module Design:** All functionality in `src/semantic_scholar_mcp/server.py` (832 lines) using FastMCP framework.

**Core Components:**
- **API Client:** `make_api_request()` handles HTTP requests with error handling
- **Formatters:** `format_paper()`, `format_author()` convert API responses  
- **12 MCP Tools:** Paper search/retrieval, author search, citations, PDF downloads
- **PDF Handler:** Downloads with metadata embedding (requires PyPDF2)

**Tool Categories:**
- Paper tools: `search_papers`, `get_paper`, `get_paper_batch`, `get_paper_citations`, `get_paper_references`
- Author tools: `search_authors`, `get_author` 
- Specialized: `search_snippets`, `get_citation_context`, `get_paper_pdf_info`, `download_paper_pdf`

## Configuration

**API Key (Optional):** Set `SEMANTIC_SCHOLAR_API_KEY` environment variable for higher rate limits. Server works without key but shares public rate limits.

**Dependencies:**
- Core: `mcp>=1.0.0`, `httpx>=0.24.0`, `pydantic>=2.0.0`
- Optional: `PyPDF2>=3.0.0` for PDF metadata embedding
- Dev: `pytest`, `black`, `isort`, `flake8`

## Testing Strategy

**Test Types:**
- Unit tests: Mocked API responses in `test_server.py`
- Integration tests: Real API calls (marked `@pytest.mark.integration`)
- Performance tests: Load testing (marked `@pytest.mark.performance`)

**Fixtures:** Comprehensive mock data in `conftest.py` for papers, authors, citations, references.

**CI/CD:** GitHub Actions runs lint → unit tests → integration tests (if API key available) across Python 3.8-3.11.

## Error Handling Patterns

**API Errors:**
- 403: API key issues or access restrictions
- 429: Rate limiting (suggests getting API key)
- General HTTP errors with descriptive messages

**Async Patterns:** All API calls use `httpx.AsyncClient` with proper error propagation and timeout handling.

## Key Files
- `src/semantic_scholar_mcp/server.py`: Main server implementation
- `tests/conftest.py`: Test fixtures and configuration  
- `pytest.ini`: Test markers and configuration
- `Makefile`: Development workflow automation
- `.github/workflows/test.yml`: CI/CD pipeline