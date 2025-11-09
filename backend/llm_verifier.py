"""
AI Fact Verifier using Tavily Search API
Leverages Tavily's AI-powered search for fact-checking claims.
"""
import os
import re
from typing import Dict, Tuple
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


class LLMVerifier:
    """
    Fact verification using Tavily AI search.
    Automatically searches, analyzes sources, and provides citations.
    """
    
    def __init__(self):
        """Initialize Tavily client with API key from environment."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY not found. "
                "Get a free key from https://tavily.com"
            )
        self.client = TavilyClient(api_key=api_key)
    
    def verify_claim(self, claim: str) -> Dict:
        """
        Fact-check a claim using Tavily AI.
        
        Args:
            claim: The claim text to verify
        
        Returns:
            Dictionary containing:
                - verdict: "SUPPORTS", "REFUTES", or "NOT ENOUGH INFO"
                - confidence: Float between 0.0 and 1.0
                - reasoning: Explanation from AI
                - sources: List of source dictionaries with title, url, content, reliability_score
        """
        
        try:
            # Ask AI to fact-check with explicit certainty level
            analysis_response = self.client.search(
                query=f"Fact-check this claim and respond in this exact format: 'VERDICT: [TRUE/FALSE/UNCERTAIN] | CERTAINTY: [percentage]% | EXPLANATION: [your explanation]'. Claim: {claim}",
                search_depth="advanced",
                max_results=5,
                include_answer=True,
                include_raw_content=False
            )
            
            analysis = analysis_response.get('answer', 'No answer provided')
            
            # Get sources
            sources = []
            for result in analysis_response.get('results', []):
                sources.append({
                    'title': result.get('title', 'Unknown'),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'reliability_score': self._calculate_reliability(result.get('url', ''))
                })
            
            # Parse AI response
            verdict, confidence, explanation = self._parse_answer(analysis)
            
            return {
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": explanation,
                "sources": sources
            }
            
        except Exception as e:
            return {
                "verdict": "NOT ENOUGH INFO",
                "confidence": 0.0,
                "reasoning": f"Error during fact-checking: {str(e)}",
                "sources": []
            }
    
    def _calculate_reliability(self, url: str) -> int:
        """
        Calculate source reliability score based on domain.
        
        Returns:
            Integer score between 60-100
        """
        url_lower = url.lower()
        
        if any(d in url_lower for d in ['wikipedia.org', 'nasa.gov', 'britannica.com', 'who.int', 'cdc.gov']):
            return 100
        elif any(d in url_lower for d in ['.edu', '.gov', 'nih.gov']):
            return 90
        elif any(d in url_lower for d in ['reuters.com', 'apnews.com', 'bbc.com', 'snopes.com']):
            return 85
        elif any(d in url_lower for d in ['nytimes.com', 'theguardian.com', 'scientificamerican.com']):
            return 75
        return 60
    
    def _parse_answer(self, analysis: str) -> Tuple[str, float, str]:
        """
        Extract verdict, certainty, and explanation from Tavily's response.
        
        Expected format: "VERDICT: [TRUE/FALSE/UNCERTAIN] | CERTAINTY: [X]% | EXPLANATION: [text]"
        Falls back to keyword detection if structured format not found.
        
        Returns:
            Tuple of (verdict, confidence, explanation)
        """
        
        # Parse structured format
        verdict_match = re.search(r'VERDICT:\s*(TRUE|FALSE|UNCERTAIN)', analysis, re.IGNORECASE)
        certainty_match = re.search(r'CERTAINTY:\s*(\d+)%', analysis, re.IGNORECASE)
        explanation_match = re.search(r'EXPLANATION:\s*(.+)', analysis, re.IGNORECASE | re.DOTALL)
        
        # Extract verdict
        if verdict_match:
            verdict_text = verdict_match.group(1).upper()
            if verdict_text == "TRUE":
                verdict = "SUPPORTS"
            elif verdict_text == "FALSE":
                verdict = "REFUTES"
            else:
                verdict = "NOT ENOUGH INFO"
        else:
            # Fallback: keyword detection
            text_lower = analysis.lower()
            if any(phrase in text_lower for phrase in ['is true', 'is correct', 'is accurate', 'claim is true', 'this is true']):
                verdict = "SUPPORTS"
            elif any(phrase in text_lower for phrase in ['is false', 'is not true', 'is incorrect', 'claim is false', 'this is false']):
                verdict = "REFUTES"
            else:
                verdict = "NOT ENOUGH INFO"
        
        # Extract certainty
        if certainty_match:
            confidence = float(certainty_match.group(1)) / 100.0
        else:
            any_percentage = re.search(r'(\d+)%', analysis)
            if any_percentage:
                confidence = float(any_percentage.group(1)) / 100.0
            else:
                confidence = 0.85 if verdict != "NOT ENOUGH INFO" else 0.50
        
        # Extract explanation
        if explanation_match:
            explanation = explanation_match.group(1).strip()
        else:
            explanation = analysis
        
        confidence = max(0.0, min(1.0, confidence))
        return verdict, confidence, explanation


def get_llm_verifier() -> LLMVerifier:
    """Create and return an LLMVerifier instance."""
    return LLMVerifier()
