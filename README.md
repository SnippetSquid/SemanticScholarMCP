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
- **PDF Download**: Download open access PDFs with proper filenames and metadata
- **PDF Availability**: Check if PDFs are available before downloading
- **Smart Naming**: PDFs saved with paper title and year as filename
- **Metadata Support**: Embeds title, authors, and year in PDF file properties

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

3. (Optional but recommended) Set up your Semantic Scholar API key:
```bash
export SEMANTIC_SCHOLAR_API_KEY="your-api-key-here"
```
**Note**: The API key is optional. The server works without it, but you'll share the public rate limit (1000 requests per second across all unauthenticated users).

4. (Optional) Install PDF metadata support:
```bash
pip install -e ".[metadata]"
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[test,dev]"
```

### Running Tests

```bash
# Run all tests
make test

# Run only unit tests (fast, no API calls)
make test-unit

# Run integration tests (requires API key)
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
make test-integration

# Run performance tests
make test-performance
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format
```

## Configuration

Add this server to your MCP client configuration:

```json
{
  "mcpServers": {
    "SemanticScholarMCP": {
      "command": "/Users/your-username/Desktop/SemanticScholarMCP/venv/bin/python",
      "args": ["/Users/your-username/Desktop/SemanticScholarMCP/src/semantic_scholar_mcp/server.py"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "your-actual-api-key-here"
      }
    }
  }
}
```

**Configuration without API key** (shares public rate limit):
```json
{
  "mcpServers": {
    "SemanticScholarMCP": {
      "command": "/Users/your-username/Desktop/SemanticScholarMCP/venv/bin/python",
      "args": ["/Users/your-username/Desktop/SemanticScholarMCP/src/semantic_scholar_mcp/server.py"]
    }
  }
}
```

**Important**: 
- Replace `your-username` with your actual username
- The API key is **optional** but recommended for dedicated rate limits
- Without an API key: Shared public rate limit (1000 requests/second across all users)
- With a free API key: Dedicated higher rate limits for your usage

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

### PDF Tools

#### `get_paper_pdf_info`
Check PDF availability for a paper.

**Parameters:**
- `paper_id` (required): Paper ID to check PDF availability

#### `download_paper_pdf`
Download the PDF of a paper if available, using the paper title as filename and setting metadata.

**Parameters:**
- `paper_id` (required): Paper ID to download PDF for
- `download_path`: Directory to save PDF (default: ~/Downloads/semantic_scholar_papers)

**Features:**
- Uses paper title as filename (e.g., "Machine Learning in Healthcare (2023).pdf")
- Sets PDF metadata with title, authors, and publication year
- Handles duplicate filenames automatically
- Creates organized folder structure

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

### Check PDF availability
```
get_paper_pdf_info("10.1038/nature14539")
```

### Download a paper PDF
```
download_paper_pdf("10.1038/nature14539")
```

This will save the PDF as something like:
```
"Deep learning (2015).pdf"
```
With embedded metadata including title, authors (LeCun, Y., Bengio, Y., Hinton, G.), and year (2015).

## API Rate Limits

The Semantic Scholar API has the following rate limits:
- **Without API key**: 1000 requests per second shared among all unauthenticated users (may be throttled during heavy usage)
- **With free API key**: Dedicated higher rate limits for your personal usage

Getting a free API key is recommended for consistent performance.

## Troubleshooting

### Rate Limit Error
If you see this error:
```
Error: Rate limit exceeded. Please wait a moment and try again, or get an API key for higher limits.
```

This means you've hit the shared public rate limit or the API is being throttled due to heavy usage.

**Immediate Solutions:**
1. **Get a free API key** (recommended):
   - Visit https://www.semanticscholar.org/product/api
   - Sign up for a free account
   - Get your API key
   - Add it to your Claude Desktop config:
   ```json
   "env": {
     "SEMANTIC_SCHOLAR_API_KEY": "your-actual-api-key-here"
   }
   ```
   - Restart Claude Desktop

2. **Wait and retry**: The shared public rate limit may be temporarily exceeded
3. **Use smaller result limits**: Reduce the `limit` parameter in your queries
4. **Space out requests**: Avoid making many requests in rapid succession

### Configuration Issues
- Ensure the Python path in your config points to the correct virtual environment
- Verify the server script path is correct
- Check that all dependencies are installed in the virtual environment

### Testing the Connection
You can test if the server is working by asking Claude to search for a single paper with a small limit:
```
search_papers("machine learning", limit=1)
```

## Error Handling

All tools include comprehensive error handling and will return descriptive error messages if requests fail or if the API returns errors.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
