"""
NLI-based fact verification using pre-trained models.
Uses Natural Language Inference to determine entailment/contradiction.
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from typing import List, Dict, Tuple


class NLIVerifier:
    """
    Natural Language Inference verifier for fact-checking.
    Uses roberta-large-mnli to compute entailment scores.
    """
    
    def __init__(self, model_name: str = "roberta-large-mnli"):
        """
        Initialize NLI model.
        
        Args:
            model_name: HuggingFace model name.
                       Options: roberta-large-mnli, bart-large-mnli, 
                               facebook/bart-large-mnli
        """
        print(f"Loading NLI model: {model_name}...")
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.model.to(self.device)
        
        print(f"✓ NLI model loaded successfully")
    
    def compute_nli_scores(self, premise: str, hypothesis: str) -> Dict[str, float]:
        """
        Compute NLI probabilities for a premise-hypothesis pair.
        
        Args:
            premise: The evidence text (premise)
            hypothesis: The claim to verify (hypothesis)
        
        Returns:
            Dict with keys: contradiction, neutral, entailment (probabilities)
        """
        # Tokenize input
        inputs = self.tokenizer(
            premise, 
            hypothesis, 
            return_tensors="pt", 
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        # Convert to probabilities
        probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
        
        # roberta-large-mnli returns: [contradiction, neutral, entailment]
        return {
            "contradiction": float(probs[0]),
            "neutral": float(probs[1]),
            "entailment": float(probs[2])
        }
    
    def verify_claim(
        self, 
        claim: str, 
        evidence_docs: List[Dict],
        relevance_threshold: float = 0.5
    ) -> Dict:
        """
        Verify a claim against multiple evidence documents.
        
        Args:
            claim: The claim to fact-check
            evidence_docs: List of evidence documents (from retrieval)
                          Each doc should have 'text', 'source', and 'distance' keys
            relevance_threshold: Minimum similarity score to consider evidence (0-1)
                                Higher = stricter filtering of irrelevant docs
        
        Returns:
            Dict containing:
                - truth_score: float (0-100)
                - evidences: List of scored evidence with stance
                - avg_nli_scores: Average NLI probabilities
                - explanation: Brief text explanation
        """
        if not evidence_docs:
            return {
                "truth_score": 50.0,
                "evidences": [],
                "avg_nli_scores": {"contradiction": 0.33, "neutral": 0.34, "entailment": 0.33},
                "explanation": "No evidence found to verify this claim."
            }
        
        # Filter evidence by semantic similarity (distance to similarity conversion)
        # Lower distance = higher similarity. Typical FAISS L2 distances: 0.5-2.0 for relevant docs
        relevant_docs = []
        for doc in evidence_docs:
            distance = doc.get('distance', 1.0)
            # Convert L2 distance to similarity score (0-1)
            # Rough heuristic: similarity = 1 / (1 + distance)
            similarity = 1.0 / (1.0 + distance)
            
            if similarity >= relevance_threshold:
                doc['similarity'] = similarity
                relevant_docs.append(doc)
        
        # If no relevant evidence after filtering, return neutral
        if not relevant_docs:
            return {
                "truth_score": 50.0,
                "evidences": [],
                "avg_nli_scores": {"contradiction": 0.33, "neutral": 0.34, "entailment": 0.33},
                "explanation": "No sufficiently relevant evidence found to verify this claim."
            }
        
        # Compute NLI scores for each relevant evidence document
        scored_evidence = []
        all_nli_scores = []
        weights = []
        
        for doc in relevant_docs:
            evidence_text = doc.get('text', '')
            nli_scores = self.compute_nli_scores(evidence_text, claim)
            all_nli_scores.append(nli_scores)
            
            # Weight by both NLI confidence and semantic similarity
            stance, confidence = self._get_stance(nli_scores)
            weight = confidence * doc['similarity']  # Combined weight
            weights.append(weight)
            
            scored_evidence.append({
                "source": doc.get('source', 'Unknown'),
                "snippet": evidence_text[:200] + "..." if len(evidence_text) > 200 else evidence_text,
                "stance": stance,
                "score": confidence,
                "nli_scores": nli_scores,
                "url": doc.get('url', ''),  # Pass through URL from web search
                "reliability_score": doc.get('reliability_score', 0)  # Pass through reliability score
            })
        
        # Calculate WEIGHTED average NLI scores (not simple average)
        total_weight = sum(weights)
        if total_weight > 0:
            avg_nli = {
                "contradiction": sum(s["contradiction"] * w for s, w in zip(all_nli_scores, weights)) / total_weight,
                "neutral": sum(s["neutral"] * w for s, w in zip(all_nli_scores, weights)) / total_weight,
                "entailment": sum(s["entailment"] * w for s, w in zip(all_nli_scores, weights)) / total_weight
            }
        else:
            avg_nli = {
                "contradiction": sum(s["contradiction"] for s in all_nli_scores) / len(all_nli_scores),
                "neutral": sum(s["neutral"] for s in all_nli_scores) / len(all_nli_scores),
                "entailment": sum(s["entailment"] for s in all_nli_scores) / len(all_nli_scores)
            }
        
        # Calculate truth score (0-100)
        truth_score = self._calculate_truth_score(avg_nli)
        
        # Sort evidence by reliability score (if available) then by confidence
        # This ensures we show the most reliable sources first
        scored_evidence.sort(
            key=lambda x: (x.get('reliability_score', 0), x['score']), 
            reverse=True
        )
        
        # Keep top 3 for display (but used all for NLI calculation)
        display_evidence = scored_evidence[:3]
        
        # Generate explanation
        explanation = self._generate_explanation(truth_score, display_evidence)
        
        return {
            "truth_score": round(truth_score, 2),
            "evidences": display_evidence,  # Only return top 3
            "avg_nli_scores": {k: round(v, 3) for k, v in avg_nli.items()},
            "explanation": explanation
        }
    
    def _get_stance(self, nli_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Determine stance and confidence from NLI scores.
        
        Returns:
            (stance, confidence) where stance is "support", "contradict", or "neutral"
        """
        max_label = max(nli_scores, key=nli_scores.get)
        confidence = nli_scores[max_label]
        
        if max_label == "entailment":
            return "support", confidence
        elif max_label == "contradiction":
            return "contradict", confidence
        else:
            return "neutral", confidence
    
    def _calculate_truth_score(self, avg_nli: Dict[str, float]) -> float:
        """
        Convert average NLI scores to a truth percentage (0-100).
        
        Formula: 100 * (entailment + 0.5*neutral - contradiction)
        Then clamp to [0, 100]
        
        Interpretation:
        - High entailment → high truth score
        - High contradiction → low truth score
        - Neutral → moderate effect (50% weight)
        """
        score = (
            avg_nli["entailment"] + 
            0.5 * avg_nli["neutral"] - 
            avg_nli["contradiction"]
        )
        
        # Convert to 0-100 scale and clamp
        truth_score = score * 100
        return max(0.0, min(100.0, truth_score))
    
    def _generate_explanation(
        self, 
        truth_score: float, 
        evidences: List[Dict]
    ) -> str:
        """
        Generate a simple text explanation of the verdict.
        """
        if truth_score >= 75:
            verdict = "likely true"
        elif truth_score >= 50:
            verdict = "partially true or uncertain"
        elif truth_score >= 25:
            verdict = "partially false or uncertain"
        else:
            verdict = "likely false"
        
        # Count stances
        support_count = sum(1 for e in evidences if e['stance'] == 'support')
        contradict_count = sum(1 for e in evidences if e['stance'] == 'contradict')
        neutral_count = sum(1 for e in evidences if e['stance'] == 'neutral')
        
        explanation = f"This claim appears {verdict} based on {len(evidences)} evidence source(s). "
        
        if support_count > 0:
            explanation += f"{support_count} source(s) support the claim. "
        if contradict_count > 0:
            explanation += f"{contradict_count} source(s) contradict it. "
        if neutral_count > 0:
            explanation += f"{neutral_count} source(s) are neutral or inconclusive."
        
        return explanation.strip()


# Singleton instance (lazy loaded)
_verifier_instance = None


def get_verifier(model_name: str = "roberta-large-mnli") -> NLIVerifier:
    """
    Get or create the global verifier instance.
    
    Args:
        model_name: NLI model name (only used on first call)
    
    Returns:
        NLIVerifier instance
    """
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = NLIVerifier(model_name=model_name)
    return _verifier_instance
