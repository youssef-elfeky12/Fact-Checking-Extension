"""
Web Search Engine for Real-Time Fact Checking
Uses DuckDuckGo (no API key needed) to find relevant web content
"""

from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from typing import List, Dict
import time


class WebSearchEngine:
    """Search the web for evidence to fact-check claims"""
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.ddgs = DDGS()
    
    def search(self, query: str) -> List[Dict]:
        """
        Search the web and extract relevant text snippets
        
        Args:
            query: Search query (the claim to fact-check)
            
        Returns:
            List of documents with 'text', 'source', 'url' keys
        """
        print(f"🔍 Searching web for: {query[:100]}...")
        
        try:
            # Search DuckDuckGo (no API key required)
            results = list(self.ddgs.text(
                query, 
                max_results=self.max_results,
                region='wt-wt',  # Worldwide
                safesearch='moderate'
            ))
            
            print(f"✓ Found {len(results)} search results")
            
            # Extract relevant content from each result
            documents = []
            for i, result in enumerate(results):
                try:
                    # Get basic info from search result
                    title = result.get('title', '')
                    snippet = result.get('body', '')
                    url = result.get('href', '')
                    
                    # Combine title and snippet for better context
                    text = f"{title}. {snippet}"
                    
                    # Try to fetch more content from the actual page
                    page_text = self._fetch_page_content(url)
                    if page_text:
                        text = page_text[:1000]  # First 1000 chars
                    
                    documents.append({
                        'text': text,
                        'source': title or url,
                        'url': url,
                        'distance': i * 0.1  # Fake distance based on rank (0.0, 0.1, 0.2...)
                    })
                    
                    # Rate limiting
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"⚠ Error processing result {i+1}: {e}")
                    continue
            
            print(f"✓ Extracted content from {len(documents)} sources")
            return documents
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _fetch_page_content(self, url: str, timeout: int = 5) -> str:
        """
        Fetch and extract main text content from a webpage
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            Extracted text content or empty string on failure
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text from main content areas
            main_content = soup.find(['article', 'main', 'div[role="main"]'])
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return text
            
        except Exception as e:
            # Silently fail - we can still use the snippet
            return ""


def get_web_search_engine(max_results: int = 5) -> WebSearchEngine:
    """Factory function to create web search engine"""
    return WebSearchEngine(max_results=max_results)
