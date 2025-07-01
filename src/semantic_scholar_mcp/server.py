"""Semantic Scholar MCP Server."""

import os
import json
from typing import Dict, List, Optional, Any, Union
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("semantic-scholar")

# Base URL for Semantic Scholar API
BASE_URL = "https://api.semanticscholar.org/graph/v1"

# Get API key from environment variable
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

async def make_api_request(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    method: str = "GET"
) -> Optional[Dict[str, Any]]:
    """Make a request to the Semantic Scholar API."""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    
    headers = {
        "Accept": "application/json",
        "User-Agent": "semantic-scholar-mcp/1.0"
    }
    
    if API_KEY:
        headers["x-api-key"] = API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    except httpx.HTTPError as e:
        return {"error": f"HTTP error: {str(e)}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def format_paper(paper: Dict[str, Any]) -> str:
    """Format a paper for display."""
    title = paper.get("title", "Unknown Title")
    authors = paper.get("authors", [])
    author_names = [author.get("name", "Unknown") for author in authors[:3]]
    author_str = ", ".join(author_names)
    if len(authors) > 3:
        author_str += f" (and {len(authors) - 3} others)"
    
    year = paper.get("year")
    year_str = f" ({year})" if year else ""
    
    venue = paper.get("venue", "")
    venue_str = f" - {venue}" if venue else ""
    
    citation_count = paper.get("citationCount", 0)
    
    paper_id = paper.get("paperId", "")
    
    return f"Title: {title}\nAuthors: {author_str}{year_str}{venue_str}\nCitations: {citation_count}\nPaper ID: {paper_id}"

def format_author(author: Dict[str, Any]) -> str:
    """Format an author for display."""
    name = author.get("name", "Unknown Name")
    author_id = author.get("authorId", "")
    paper_count = author.get("paperCount", 0)
    citation_count = author.get("citationCount", 0)
    h_index = author.get("hIndex", 0)
    
    return f"Name: {name}\nAuthor ID: {author_id}\nPapers: {paper_count}\nCitations: {citation_count}\nH-Index: {h_index}"


@mcp.tool()
async def search_papers(
    query: str,
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None,
    publication_types: Optional[str] = None,
    open_access_pdf: Optional[bool] = None,
    min_citation_count: Optional[int] = None,
    year: Optional[str] = None,
    venue: Optional[str] = None
) -> str:
    """
    Search for academic papers using Semantic Scholar.
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 10, max: 100)
        offset: Number of results to skip (default: 0)
        fields: Comma-separated list of fields to return
        publication_types: Filter by publication types
        open_access_pdf: Filter for papers with open access PDFs
        min_citation_count: Minimum citation count
        year: Publication year or year range (e.g., "2020-2023")
        venue: Publication venue
    
    Returns:
        Formatted search results
    """
    params = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset
    }
    
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "paperId,title,authors,year,venue,citationCount,abstract"
    
    if publication_types:
        params["publicationTypes"] = publication_types
    if open_access_pdf is not None:
        params["openAccessPdf"] = str(open_access_pdf).lower()
    if min_citation_count is not None:
        params["minCitationCount"] = min_citation_count
    if year:
        params["year"] = year
    if venue:
        params["venue"] = venue
    
    result = await make_api_request("paper/search", params)
    
    if result is None:
        return "Error: Failed to fetch results"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    papers = result.get("data", [])
    total = result.get("total", 0)
    
    if not papers:
        return "No papers found matching your query."
    
    formatted_papers = []
    for i, paper in enumerate(papers, 1):
        formatted_papers.append(f"{i}. {format_paper(paper)}")
    
    result_text = f"Found {total} total papers (showing {len(papers)}):\n\n"
    result_text += "\n\n".join(formatted_papers)
    
    return result_text


@mcp.tool()
async def get_paper(
    paper_id: str,
    fields: Optional[str] = None
) -> str:
    """
    Get detailed information about a specific paper.
    
    Args:
        paper_id: Paper ID (can be Semantic Scholar ID, DOI, ArXiv ID, etc.)
        fields: Comma-separated list of fields to return
    
    Returns:
        Detailed paper information
    """
    params = {}
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "paperId,title,authors,year,venue,citationCount,abstract,references,citations,openAccessPdf"
    
    # URL encode the paper ID to handle DOIs and other special characters
    encoded_id = quote(paper_id, safe='')
    
    result = await make_api_request(f"paper/{encoded_id}", params)
    
    if result is None:
        return "Error: Failed to fetch paper"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    paper = result
    title = paper.get("title", "Unknown Title")
    authors = paper.get("authors", [])
    author_names = [author.get("name", "Unknown") for author in authors]
    
    year = paper.get("year", "Unknown")
    venue = paper.get("venue", "Unknown")
    citation_count = paper.get("citationCount", 0)
    abstract = paper.get("abstract", "No abstract available")
    
    references = paper.get("references", [])
    citations = paper.get("citations", [])
    
    open_access = paper.get("openAccessPdf")
    pdf_url = open_access.get("url") if open_access else "No open access PDF"
    
    result_text = f"""Title: {title}
Authors: {', '.join(author_names)}
Year: {year}
Venue: {venue}
Citations: {citation_count}
Paper ID: {paper.get('paperId', 'Unknown')}

Abstract:
{abstract}

References: {len(references)}
Cited by: {len(citations)}
Open Access PDF: {pdf_url}"""
    
    return result_text


@mcp.tool()
async def get_paper_batch(
    paper_ids: str,
    fields: Optional[str] = None
) -> str:
    """
    Get information for multiple papers in a single request.
    
    Args:
        paper_ids: Comma-separated list of paper IDs
        fields: Comma-separated list of fields to return
    
    Returns:
        Batch paper information
    """
    id_list = [id.strip() for id in paper_ids.split(",")]
    
    params = {
        "ids": id_list
    }
    
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "paperId,title,authors,year,venue,citationCount,abstract"
    
    result = await make_api_request("paper/batch", params, method="POST")
    
    if result is None:
        return "Error: Failed to fetch papers"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    papers = result if isinstance(result, list) else result.get("data", [])
    
    if not papers:
        return "No papers found for the provided IDs."
    
    formatted_papers = []
    for i, paper in enumerate(papers, 1):
        if paper is None:
            formatted_papers.append(f"{i}. Paper not found")
        else:
            formatted_papers.append(f"{i}. {format_paper(paper)}")
    
    result_text = f"Retrieved {len(papers)} papers:\n\n"
    result_text += "\n\n".join(formatted_papers)
    
    return result_text


@mcp.tool()
async def search_authors(
    query: str,
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None
) -> str:
    """
    Search for authors by name.
    
    Args:
        query: Author name or search query
        limit: Maximum number of results (default: 10, max: 1000)
        offset: Number of results to skip (default: 0)
        fields: Comma-separated list of fields to return
    
    Returns:
        Formatted author search results
    """
    params = {
        "query": query,
        "limit": min(limit, 1000),
        "offset": offset
    }
    
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "authorId,name,paperCount,citationCount,hIndex"
    
    result = await make_api_request("author/search", params)
    
    if result is None:
        return "Error: Failed to fetch authors"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    authors = result.get("data", [])
    total = result.get("total", 0)
    
    if not authors:
        return "No authors found matching your query."
    
    formatted_authors = []
    for i, author in enumerate(authors, 1):
        formatted_authors.append(f"{i}. {format_author(author)}")
    
    result_text = f"Found {total} total authors (showing {len(authors)}):\n\n"
    result_text += "\n\n".join(formatted_authors)
    
    return result_text


@mcp.tool()
async def get_author(
    author_id: str,
    fields: Optional[str] = None
) -> str:
    """
    Get detailed information about a specific author.
    
    Args:
        author_id: Author ID
        fields: Comma-separated list of fields to return
    
    Returns:
        Detailed author information
    """
    params = {}
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "authorId,name,paperCount,citationCount,hIndex,papers"
    
    result = await make_api_request(f"author/{author_id}", params)
    
    if result is None:
        return "Error: Failed to fetch author"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    author = result
    name = author.get("name", "Unknown Name")
    author_id = author.get("authorId", "")
    paper_count = author.get("paperCount", 0)
    citation_count = author.get("citationCount", 0)
    h_index = author.get("hIndex", 0)
    
    papers = author.get("papers", [])
    
    result_text = f"""Name: {name}
Author ID: {author_id}
Total Papers: {paper_count}
Total Citations: {citation_count}
H-Index: {h_index}

Recent Papers ({len(papers)} shown):"""
    
    if papers:
        for i, paper in enumerate(papers[:10], 1):
            title = paper.get("title", "Unknown Title")
            year = paper.get("year", "Unknown")
            citations = paper.get("citationCount", 0)
            result_text += f"\n{i}. {title} ({year}) - {citations} citations"
    
    return result_text


@mcp.tool()
async def search_snippets(
    query: str,
    limit: int = 10,
    offset: int = 0
) -> str:
    """
    Search for text snippets across academic papers.
    
    Args:
        query: Search query for text snippets
        limit: Maximum number of results (default: 10, max: 100)
        offset: Number of results to skip (default: 0)
    
    Returns:
        Text snippets from papers
    """
    params = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset
    }
    
    result = await make_api_request("snippet/search", params)
    
    if result is None:
        return "Error: Failed to fetch snippets"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    snippets = result.get("data", [])
    total = result.get("total", 0)
    
    if not snippets:
        return "No snippets found matching your query."
    
    formatted_snippets = []
    for i, snippet in enumerate(snippets, 1):
        paper = snippet.get("paper", {})
        title = paper.get("title", "Unknown Title")
        year = paper.get("year", "Unknown")
        text = snippet.get("text", "No text available")
        
        formatted_snippets.append(f"{i}. From: {title} ({year})\nSnippet: {text}")
    
    result_text = f"Found {total} total snippets (showing {len(snippets)}):\n\n"
    result_text += "\n\n".join(formatted_snippets)
    
    return result_text


@mcp.tool()
async def get_paper_citations(
    paper_id: str,
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None
) -> str:
    """
    Get papers that cite a specific paper.
    
    Args:
        paper_id: Paper ID to get citations for
        limit: Maximum number of results (default: 10, max: 1000)
        offset: Number of results to skip (default: 0)
        fields: Comma-separated list of fields to return
    
    Returns:
        List of citing papers
    """
    params = {
        "limit": min(limit, 1000),
        "offset": offset
    }
    
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "paperId,title,authors,year,venue,citationCount"
    
    encoded_id = quote(paper_id, safe='')
    result = await make_api_request(f"paper/{encoded_id}/citations", params)
    
    if result is None:
        return "Error: Failed to fetch citations"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    citations = result.get("data", [])
    total = result.get("total", 0)
    
    if not citations:
        return "No citations found for this paper."
    
    formatted_citations = []
    for i, citation in enumerate(citations, 1):
        citing_paper = citation.get("citingPaper", {})
        if citing_paper:
            formatted_citations.append(f"{i}. {format_paper(citing_paper)}")
    
    result_text = f"Found {total} total citations (showing {len(formatted_citations)}):\n\n"
    result_text += "\n\n".join(formatted_citations)
    
    return result_text


@mcp.tool()
async def get_paper_references(
    paper_id: str,
    limit: int = 10,
    offset: int = 0,
    fields: Optional[str] = None
) -> str:
    """
    Get papers referenced by a specific paper.
    
    Args:
        paper_id: Paper ID to get references for
        limit: Maximum number of results (default: 10, max: 1000)
        offset: Number of results to skip (default: 0)
        fields: Comma-separated list of fields to return
    
    Returns:
        List of referenced papers
    """
    params = {
        "limit": min(limit, 1000),
        "offset": offset
    }
    
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "paperId,title,authors,year,venue,citationCount"
    
    encoded_id = quote(paper_id, safe='')
    result = await make_api_request(f"paper/{encoded_id}/references", params)
    
    if result is None:
        return "Error: Failed to fetch references"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    references = result.get("data", [])
    total = result.get("total", 0)
    
    if not references:
        return "No references found for this paper."
    
    formatted_references = []
    for i, reference in enumerate(references, 1):
        cited_paper = reference.get("citedPaper", {})
        if cited_paper:
            formatted_references.append(f"{i}. {format_paper(cited_paper)}")
    
    result_text = f"Found {total} total references (showing {len(formatted_references)}):\n\n"
    result_text += "\n\n".join(formatted_references)
    
    return result_text


@mcp.tool()
async def get_citation_context(
    paper_id: str,
    citing_paper_id: str
) -> str:
    """
    Get the context in which one paper cites another.
    
    Args:
        paper_id: ID of the paper being cited
        citing_paper_id: ID of the paper doing the citing
    
    Returns:
        Citation context information
    """
    encoded_paper_id = quote(paper_id, safe='')
    encoded_citing_id = quote(citing_paper_id, safe='')
    
    result = await make_api_request(f"paper/{encoded_paper_id}/citations/{encoded_citing_id}")
    
    if result is None:
        return "Error: Failed to fetch citation context"
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    contexts = result.get("contexts", [])
    citing_paper = result.get("citingPaper", {})
    cited_paper = result.get("citedPaper", {})
    
    if not contexts:
        return "No citation context found."
    
    result_text = f"Citation context:\n\n"
    result_text += f"Cited paper: {cited_paper.get('title', 'Unknown')}\n"
    result_text += f"Citing paper: {citing_paper.get('title', 'Unknown')}\n\n"
    
    for i, context in enumerate(contexts, 1):
        result_text += f"{i}. {context}\n"
    
    return result_text


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()