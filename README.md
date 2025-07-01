# Semantic Scholar MCP Server

A Model Context Protocol (MCP) server that provides access to the Semantic Scholar Academic Graph API. This server allows you to search for academic papers, authors, and get detailed information about citations and references.

## Features

- **Paper Search**: Search for academic papers with various filters
- **Paper Details**: Get detailed information about specific papers
- **Batch Paper Retrieval**: Get information for multiple papers at once
- **Author Search**: Find authors by name
- **Author Details**: Get detailed author information and their papers
- **Citation Analysis**: Get papers that cite a specific paper
- **Reference Analysis**: Get papers referenced by a specific paper
- **Citation Context**: Get the context in which one paper cites another
- **Text Snippets**: Search for text snippets across academic papers

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd SemanticScholarMCP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up your Semantic Scholar API key:
```bash
export SEMANTIC_SCHOLAR_API_KEY="your-api-key-here"
```

## Configuration

Add this server to your MCP client configuration:

```json
{
  "mcpServers": {
    "semantic-scholar": {
      "command": "python",
      "args": ["/path/to/SemanticScholarMCP/src/semantic_scholar_mcp/server.py"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Available Tools

### Paper Tools

#### `search_papers`
Search for academic papers with various filters.

**Parameters:**
- `query` (required): Search query string
- `limit`: Maximum number of results (default: 10, max: 100)
- `offset`: Number of results to skip (default: 0)
- `fields`: Comma-separated list of fields to return
- `publication_types`: Filter by publication types
- `open_access_pdf`: Filter for papers with open access PDFs
- `min_citation_count`: Minimum citation count
- `year`: Publication year or year range (e.g., "2020-2023")
- `venue`: Publication venue

#### `get_paper`
Get detailed information about a specific paper.

**Parameters:**
- `paper_id` (required): Paper ID (Semantic Scholar ID, DOI, ArXiv ID, etc.)
- `fields`: Comma-separated list of fields to return

#### `get_paper_batch`
Get information for multiple papers in a single request.

**Parameters:**
- `paper_ids` (required): Comma-separated list of paper IDs
- `fields`: Comma-separated list of fields to return

### Author Tools

#### `search_authors`
Search for authors by name.

**Parameters:**
- `query` (required): Author name or search query
- `limit`: Maximum number of results (default: 10, max: 1000)
- `offset`: Number of results to skip (default: 0)
- `fields`: Comma-separated list of fields to return

#### `get_author`
Get detailed information about a specific author.

**Parameters:**
- `author_id` (required): Author ID
- `fields`: Comma-separated list of fields to return

### Citation and Reference Tools

#### `get_paper_citations`
Get papers that cite a specific paper.

**Parameters:**
- `paper_id` (required): Paper ID to get citations for
- `limit`: Maximum number of results (default: 10, max: 1000)
- `offset`: Number of results to skip (default: 0)
- `fields`: Comma-separated list of fields to return

#### `get_paper_references`
Get papers referenced by a specific paper.

**Parameters:**
- `paper_id` (required): Paper ID to get references for
- `limit`: Maximum number of results (default: 10, max: 1000)
- `offset`: Number of results to skip (default: 0)
- `fields`: Comma-separated list of fields to return

#### `get_citation_context`
Get the context in which one paper cites another.

**Parameters:**
- `paper_id` (required): ID of the paper being cited
- `citing_paper_id` (required): ID of the paper doing the citing

### Text Search Tools

#### `search_snippets`
Search for text snippets across academic papers.

**Parameters:**
- `query` (required): Search query for text snippets
- `limit`: Maximum number of results (default: 10, max: 100)
- `offset`: Number of results to skip (default: 0)

## Usage Examples

### Search for papers on machine learning
```
search_papers("machine learning", limit=5, year="2023")
```

### Get details about a specific paper
```
get_paper("10.1038/nature14539")
```

### Find papers that cite a specific work
```
get_paper_citations("10.1038/nature14539", limit=10)
```

### Search for an author
```
search_authors("Geoffrey Hinton")
```

### Get citation context
```
get_citation_context("paper-id-1", "paper-id-2")
```

## API Rate Limits

The Semantic Scholar API has rate limits. Using an API key provides higher rate limits. Without an API key, you're limited to 100 requests per 5 minutes.

## Error Handling

All tools include comprehensive error handling and will return descriptive error messages if requests fail or if the API returns errors.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
