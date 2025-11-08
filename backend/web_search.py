"""
Web Search Engine for Real-Time Fact Checking
Uses DuckDuckGo (no API key needed) to find relevant web content
"""

from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests
from typing import List, Dict
import time
import re


class WebSearchEngine:
    """Search the web for evidence to fact-check claims"""
    
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.ddgs = DDGS()
    
    def _is_english_text(self, text: str) -> bool:
        """Check if text is primarily in English (strict - 70% threshold)"""
        if not text or len(text) < 20:
            return False
        
        # Count English alphabet characters vs total characters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'\S', text))  # Non-whitespace chars
        
        if total_chars == 0:
            return False
        
        # Should be at least 70% English characters
        ratio = english_chars / total_chars
        return ratio > 0.7
    
    def _is_english_text_lenient(self, text: str) -> bool:
        """Check if text has some English (lenient - 40% threshold for LLM filtering)"""
        if not text or len(text) < 10:
            return False
        
        # Count English alphabet characters vs total characters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'\S', text))  # Non-whitespace chars
        
        if total_chars == 0:
            return False
        
        # Just need 40% English - let LLM handle the rest
        ratio = english_chars / total_chars
        return ratio > 0.4
    
    def _is_reliable_domain(self, url: str) -> int:
        """
        Check domain reliability and return priority score
        Higher score = more reliable
        """
        url_lower = url.lower()
        
        # Tier 1: Most reliable (score 100)
        tier1_domains = [
            'wikipedia.org', 'britannica.com', 'nasa.gov', 'cdc.gov', 
            'who.int', 'nih.gov', 'nature.com', 'science.org'
        ]
        
        # Tier 2: Very reliable (score 80)
        tier2_domains = [
            'reuters.com', 'apnews.com', 'bbc.com', 'bbc.co.uk',
            'nationalgeographic.com', 'smithsonianmag.com',
            'scientificamerican.com', 'pbs.org'
        ]
        
        # Tier 3: Reputable news (score 60)
        tier3_domains = [
            'nytimes.com', 'theguardian.com', 'washingtonpost.com',
            'time.com', 'economist.com', 'forbes.com'
        ]
        
        # Tier 4: Educational/Government (score 70)
        tier4_patterns = ['.edu', '.gov']
        
        # Blacklist suspicious patterns (score 0)
        suspicious_patterns = [
            'login', 'signin', 'register', 'signup', 'account',
            'gmail', 'yahoo', 'outlook', 'mail.',
            '.cn', '.ru'  # Often not English content
        ]
        
        # Check for suspicious patterns first
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return 0
        
        # Check reliability tiers
        for domain in tier1_domains:
            if domain in url_lower:
                return 100
        
        for domain in tier2_domains:
            if domain in url_lower:
                return 80
        
        for domain in tier3_domains:
            if domain in url_lower:
                return 60
        
        for pattern in tier4_patterns:
            if pattern in url_lower:
                return 70
        
        # Unknown domain - still return a score for sorting
        return 30
    
    def search(self, query: str) -> List[Dict]:
        """
        Search the web and extract relevant text snippets.
        Minimal filtering - let the LLM decide what's relevant and reliable.
        Minimal filtering - let the LLM decide what's relevant and reliable.
        
        Args:
            query: Search query (the claim to fact-check)
            
        Returns:
            List of documents with 'text', 'source', 'url', 'reliability_score' keys
            Sorted by reliability, returns up to max_results
        """
        print(f"🔍 Searching web for: {query[:100]}...")
        
        try:
            # Search with explicit English region preference
            results = []
            
            try:
                # Use us-en region which prioritizes English sites
                for r in self.ddgs.text(
                    keywords=query,
                    region='us-en',  # US English - prioritizes English results
                    safesearch='moderate',
                    timelimit=None,
                    max_results=self.max_results * 2  # Get 2x to account for some filtering
                ):
                    results.append(r)
                    
            except Exception as e:
                print(f"❌ Search failed: {e}")
                # Try with just keywords as absolute fallback
                try:
                    for r in self.ddgs.text(query, max_results=self.max_results * 2):
                        results.append(r)
                except:
                    return []
            
            if not results:
                print(f"⚠ No results found. This could be due to:")
                print(f"   - DuckDuckGo rate limiting (wait 10-30 seconds)")
                print(f"   - Query too specific")
                print(f"   - Network issues")
                return []
            
            print(f"✓ Found {len(results)} raw search results")
            
            # Minimal filtering - let the LLM decide what's relevant
            scored_results = []
            for result in results:
                url = result.get('href', '')
                title = result.get('title', '')
                snippet = result.get('body', '')
                
                # Skip empty results
                if not url or not title:
                    continue
                
                # Block obviously bad domains (spam, redirects, etc.)
                if any(pattern in url.lower() for pattern in ['login', 'signin', 'redirect', 'accounts.google']):
                    continue
                
                # Get reliability score (but don't filter on it - just for sorting)
                reliability_score = self._is_reliable_domain(url)
                
                # Quick English check (but be very lenient - 50% threshold)
                combined_text = f"{title} {snippet}"
                if combined_text and not self._is_english_text_lenient(combined_text):
                    continue  # Skip obvious non-English
                
                # Use snippet directly
                text = f"{title}. {snippet}"
                
                scored_results.append({
                    'text': text,
                    'source': title or url,
                    'url': url,
                    'reliability_score': reliability_score,
                    'distance': 0.1  # Fake distance for compatibility
                })
                
                # Stop once we have enough
                if len(scored_results) >= self.max_results:
                    break
            
            # Sort by reliability score (highest first)
            scored_results.sort(key=lambda x: x['reliability_score'], reverse=True)
            
            # Take top N results
            final_results = scored_results[:self.max_results]
            
            if len(final_results) == 0:
                print(f"⚠ No sources found after filtering.")
            else:
                print(f"✓ Found {len(final_results)} sources for LLM analysis")
                for i, doc in enumerate(final_results[:3]):
                    print(f"  {i+1}. [{doc['reliability_score']}] {doc['source'][:50]}")
            
            return final_results
            
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
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            
            # Check if we got redirected to a login/account page
            final_url = response.url.lower()
            redirect_indicators = ['login', 'signin', 'signup', 'register', 'account', 'gmail', 'mail']
            if any(indicator in final_url for indicator in redirect_indicators):
                print(f"⚠ Blocked redirect to login page: {final_url[:50]}")
                return ""
            
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
