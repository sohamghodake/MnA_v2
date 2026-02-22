from typing import List, Dict, Any
import re
try:
    import spacy
    NLP = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    NLP = None

class EntityExtractor:
    def __init__(self):
        self.use_spacy = NLP is not None

    def extract_companies(self, text: str) -> List[str]:
        if self.use_spacy:
            doc = NLP(text)
            return [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        else:
            # Fallback regex for Capitalized Words (very naive)
            return re.findall(r'\b[A-Z][a-zA-Z]+\s(?:Inc\.|Corp\.|Ltd\.|LLC|Group)\b', text)

    def extract_amounts(self, text: str) -> List[str]:
        # Regex is often better for money anyway
        return re.findall(r'\$\d+(?:,\d{3})*(?:\.\d+)?(?:[MmBb]n)?', text)

    def extract_risks(self, text: str) -> List[Dict[str, Any]]:
        # Keyword based extraction for MVP
        risks = []
        keywords = ["lawsuit", "compliance violation", "churn", "debt cliff"]
        for kw in keywords:
            if kw in text.lower():
                risks.append({
                    "description": f"Potential {kw} detected",
                    "severity": "medium",  # Default, requires LLM refinement in real system
                    "probability": 0.5
                })
        return risks
