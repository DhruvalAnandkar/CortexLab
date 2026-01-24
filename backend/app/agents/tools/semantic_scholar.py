"""
Semantic Scholar API Tool

Search and retrieve academic papers from Semantic Scholar.
"""

import httpx
from typing import List, Optional
from app.config import get_settings

settings = get_settings()

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1"


async def search_semantic_scholar(
    query: str,
    limit: int = 20,
    year_range: Optional[tuple] = None,
    fields_of_study: Optional[List[str]] = None,
) -> List[dict]:
    """
    Search for papers on Semantic Scholar.
    
    Args:
        query: Search query string
        limit: Maximum number of results (default 20, max 100)
        year_range: Optional tuple of (start_year, end_year)
        fields_of_study: Optional list of fields to filter by
        
    Returns:
        List of paper dictionaries with metadata
    """
    headers = {}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key
    
    params = {
        "query": query,
        "limit": min(limit, 100),
        "fields": "paperId,title,abstract,year,authors,venue,citationCount,url,externalIds",
    }
    
    if year_range:
        params["year"] = f"{year_range[0]}-{year_range[1]}"
    
    if fields_of_study:
        params["fieldsOfStudy"] = ",".join(fields_of_study)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{SEMANTIC_SCHOLAR_API_URL}/paper/search",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for paper in data.get("data", []):
                papers.append({
                    "id": paper.get("paperId"),
                    "title": paper.get("title"),
                    "abstract": paper.get("abstract"),
                    "year": paper.get("year"),
                    "authors": ", ".join([
                        a.get("name", "") for a in paper.get("authors", [])
                    ]),
                    "venue": paper.get("venue"),
                    "citation_count": paper.get("citationCount"),
                    "url": paper.get("url"),
                    "provider": "semantic_scholar",
                    "external_ids": paper.get("externalIds", {}),
                })
            
            return papers
            
        except httpx.HTTPError as e:
            print(f"Semantic Scholar API error: {e}")
            return []


async def get_paper_details(paper_id: str) -> Optional[dict]:
    """
    Get detailed information about a specific paper.
    
    Args:
        paper_id: Semantic Scholar paper ID
        
    Returns:
        Paper dictionary with full details, or None if not found
    """
    headers = {}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key
    
    fields = "paperId,title,abstract,year,authors,venue,citationCount,url,references,citations,tldr"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{SEMANTIC_SCHOLAR_API_URL}/paper/{paper_id}",
                params={"fields": fields},
                headers=headers,
            )
            response.raise_for_status()
            paper = response.json()
            
            return {
                "id": paper.get("paperId"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "year": paper.get("year"),
                "authors": ", ".join([
                    a.get("name", "") for a in paper.get("authors", [])
                ]),
                "venue": paper.get("venue"),
                "citation_count": paper.get("citationCount"),
                "url": paper.get("url"),
                "tldr": paper.get("tldr", {}).get("text"),
                "reference_count": len(paper.get("references", [])),
                "citation_details": len(paper.get("citations", [])),
                "provider": "semantic_scholar",
            }
            
        except httpx.HTTPError as e:
            print(f"Semantic Scholar API error: {e}")
            return None


async def get_paper_citations(paper_id: str, limit: int = 50) -> List[dict]:
    """
    Get papers that cite a specific paper.
    
    Args:
        paper_id: Semantic Scholar paper ID
        limit: Maximum number of citations to retrieve
        
    Returns:
        List of citing paper dictionaries
    """
    headers = {}
    if settings.semantic_scholar_api_key:
        headers["x-api-key"] = settings.semantic_scholar_api_key
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{SEMANTIC_SCHOLAR_API_URL}/paper/{paper_id}/citations",
                params={
                    "fields": "paperId,title,abstract,year,authors,venue,citationCount",
                    "limit": limit,
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for item in data.get("data", []):
                paper = item.get("citingPaper", {})
                if paper:
                    papers.append({
                        "id": paper.get("paperId"),
                        "title": paper.get("title"),
                        "abstract": paper.get("abstract"),
                        "year": paper.get("year"),
                        "authors": ", ".join([
                            a.get("name", "") for a in paper.get("authors", [])
                        ]),
                        "venue": paper.get("venue"),
                        "citation_count": paper.get("citationCount"),
                        "provider": "semantic_scholar",
                    })
            
            return papers
            
        except httpx.HTTPError as e:
            print(f"Semantic Scholar API error: {e}")
            return []
