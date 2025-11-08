"""
AI Fact Verifier using Tavily Search API.
Tavily is designed for AI fact-checking with built-in web search and citations.
"""
import os
from typing import Dict
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMVerifier:
    """
    AI fact verifier using Tavily's search and answer API.
    Tavily handles search, analysis, and citations automatically.
    """
    
    def __init__(self):
        """Initialize Tavily client."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY not found in environment. "
                "Get a free key from https://tavily.com and add to .env file"
            )
        
        self.client = TavilyClient(api_key=api_key)
        print(f"✓ Tavily AI verifier initialized (1000 free searches/month)")
    
    def verify_claim(self, claim: str) -> Dict:
        """
        Verify a claim using Tavily's AI search.
        Tavily searches the web, analyzes sources, and provides citations.
        
        Args:
            claim: The claim to fact-check
        
        Returns:
            Dict with verdict, confidence, reasoning, and sources
        """
        print(f"🔍 Tavily searching: {claim[:80]}...")
        
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
            
            # Parse the AI's response to extract verdict, certainty, and explanation
            verdict, confidence, explanation = self._parse_answer(analysis)
            
            print(f"✓ Verdict: {verdict} ({confidence:.0%})")
            print(f"  Sources: {len(sources)}")
            
            return {
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": explanation,
                "sources": sources
            }
            
        except Exception as e:
            print(f"❌ Tavily error: {e}")
            return {
                "verdict": "NOT ENOUGH INFO",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "sources": []
            }
    
    def _calculate_reliability(self, url: str) -> int:
        """Calculate reliability score based on domain."""
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
    
    def _parse_answer(self, analysis: str) -> tuple:
        """
        Parse Tavily's answer to extract verdict, certainty percentage, and explanation.
        Expected format: "VERDICT: [TRUE/FALSE/UNCERTAIN] | CERTAINTY: [X]% | EXPLANATION: [text]"
        """
        import re
        
        # Try to parse structured format first
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
            # Fallback: analyze the text for verdict keywords
            text_lower = analysis.lower()
            if any(phrase in text_lower for phrase in ['is true', 'is correct', 'is accurate', 'claim is true', 'this is true']):
                verdict = "SUPPORTS"
            elif any(phrase in text_lower for phrase in ['is false', 'is not true', 'is incorrect', 'claim is false', 'this is false']):
                verdict = "REFUTES"
            else:
                verdict = "NOT ENOUGH INFO"
        
        # Extract certainty percentage
        if certainty_match:
            confidence = float(certainty_match.group(1)) / 100.0
        else:
            # Fallback: look for any percentage in the text
            any_percentage = re.search(r'(\d+)%', analysis)
            if any_percentage:
                confidence = float(any_percentage.group(1)) / 100.0
            else:
                # Default based on verdict clarity
                confidence = 0.85 if verdict != "NOT ENOUGH INFO" else 0.50
        
        # Extract explanation
        if explanation_match:
            explanation = explanation_match.group(1).strip()
        else:
            # Use the full analysis as explanation
            explanation = analysis
        
        # Ensure confidence is in valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return verdict, confidence, explanation


def get_llm_verifier() -> LLMVerifier:
    """Get or create LLM verifier singleton."""
    return LLMVerifier()
