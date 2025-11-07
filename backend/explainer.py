"""
Optional LLM-based explanation generator using Mistral 7B.
Uses bitsandbytes for 4-bit quantization to fit in 11GB GPU.
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import List, Dict, Optional
import os


class LLMExplainer:
    """
    Generate natural language explanations using a local quantized LLM.
    Uses Mistral 7B Instruct with 4-bit quantization.
    """
    
    def __init__(
        self, 
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
        use_4bit: bool = True,
        device: str = "auto"
    ):
        """
        Initialize the LLM explainer.
        
        Args:
            model_name: HuggingFace model name (default: Mistral 7B Instruct)
            use_4bit: Use 4-bit quantization (required for 11GB GPU)
            device: Device placement ("auto", "cuda", "cpu")
        """
        print(f"\n--- Loading LLM Explainer: {model_name} ---")
        
        self.model_name = model_name
        self.device = device
        
        # Check GPU availability
        if not torch.cuda.is_available() and device != "cpu":
            print("⚠ Warning: CUDA not available. Falling back to CPU (slow!).")
            self.device = "cpu"
            use_4bit = False
        
        # Configure 4-bit quantization
        if use_4bit and self.device != "cpu":
            print("Using 4-bit quantization (saves memory)")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quantization_config = None
        
        # Load tokenizer
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model
        print(f"Loading model (this may take 1-2 minutes on first run)...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto" if self.device == "auto" else None,
            torch_dtype=torch.float16 if quantization_config is None else None,
            low_cpu_mem_usage=True
        )
        
        if self.device == "cpu":
            self.model = self.model.to("cpu")
        
        print(f"✓ LLM loaded successfully")
        print(f"  Device: {next(self.model.parameters()).device}")
        print(f"  Memory: ~3.5-4GB (quantized)\n")
    
    def generate_explanation(
        self,
        claim: str,
        truth_score: float,
        evidences: List[Dict],
        max_length: int = 150
    ) -> str:
        """
        Generate a natural language explanation for the fact-check result.
        
        Args:
            claim: The claim being fact-checked
            truth_score: The computed truth score (0-100)
            evidences: List of evidence with stance and snippets
            max_length: Maximum length of generated explanation (tokens)
        
        Returns:
            Natural language explanation string
        """
        # Build prompt
        prompt = self._build_prompt(claim, truth_score, evidences)
        
        # Generate
        try:
            response = self._generate(prompt, max_length=max_length)
            return response.strip()
        except Exception as e:
            print(f"⚠ LLM generation failed: {e}")
            # Fallback to template-based explanation
            return self._fallback_explanation(claim, truth_score, evidences)
    
    def _build_prompt(
        self,
        claim: str,
        truth_score: float,
        evidences: List[Dict]
    ) -> str:
        """
        Build a prompt for the LLM to generate an explanation.
        """
        # Determine verdict
        if truth_score >= 75:
            verdict = "likely TRUE"
        elif truth_score >= 50:
            verdict = "PARTIALLY TRUE or UNCERTAIN"
        elif truth_score >= 25:
            verdict = "PARTIALLY FALSE or UNCERTAIN"
        else:
            verdict = "likely FALSE"
        
        # Format evidence
        evidence_text = ""
        for i, ev in enumerate(evidences[:3], 1):  # Top 3 only
            stance = ev['stance'].upper()
            snippet = ev['snippet'][:150]
            evidence_text += f"{i}. [{stance}] {snippet}\n"
        
        # Mistral Instruct format
        prompt = f"""[INST] You are a fact-checking assistant. Analyze the claim and evidence, then provide a brief explanation (2-3 sentences).

Claim: "{claim}"
Truth Score: {truth_score:.1f}% (verdict: {verdict})

Evidence:
{evidence_text}

Provide a concise explanation of why this claim is rated {verdict}, citing the evidence. Keep it factual and brief. [/INST]"""
        
        return prompt
    
    def _generate(self, prompt: str, max_length: int = 150) -> str:
        """
        Generate text from prompt using the LLM.
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode and extract response (after [/INST])
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response
        if "[/INST]" in full_text:
            response = full_text.split("[/INST]")[-1].strip()
        else:
            response = full_text.strip()
        
        return response
    
    def _fallback_explanation(
        self,
        claim: str,
        truth_score: float,
        evidences: List[Dict]
    ) -> str:
        """
        Fallback template-based explanation if LLM fails.
        """
        if truth_score >= 75:
            verdict = "likely true"
        elif truth_score >= 50:
            verdict = "partially true or uncertain"
        elif truth_score >= 25:
            verdict = "partially false or uncertain"
        else:
            verdict = "likely false"
        
        support_count = sum(1 for e in evidences if e['stance'] == 'support')
        contradict_count = sum(1 for e in evidences if e['stance'] == 'contradict')
        
        explanation = f"This claim appears {verdict} based on {len(evidences)} evidence source(s). "
        
        if support_count > 0:
            explanation += f"{support_count} source(s) support the claim. "
        if contradict_count > 0:
            explanation += f"{contradict_count} source(s) contradict it."
        
        return explanation.strip()


# Singleton instance (lazy loaded)
_explainer_instance = None
_explainer_enabled = os.getenv("ENABLE_LLM_EXPLAINER", "false").lower() == "true"


def get_explainer(
    model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
    force_enable: bool = False
) -> Optional[LLMExplainer]:
    """
    Get or create the global LLM explainer instance.
    Only loads if ENABLE_LLM_EXPLAINER=true or force_enable=True.
    
    Args:
        model_name: HuggingFace model name
        force_enable: Force loading even if env var not set
    
    Returns:
        LLMExplainer instance or None if disabled
    """
    global _explainer_instance, _explainer_enabled
    
    if not _explainer_enabled and not force_enable:
        return None
    
    if _explainer_instance is None:
        try:
            _explainer_instance = LLMExplainer(model_name=model_name)
        except Exception as e:
            print(f"❌ Failed to load LLM explainer: {e}")
            _explainer_instance = None
    
    return _explainer_instance


def is_explainer_enabled() -> bool:
    """Check if LLM explainer is enabled."""
    return _explainer_enabled or _explainer_instance is not None
