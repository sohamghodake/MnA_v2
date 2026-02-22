import re
from typing import List, Dict, Set

class OutputValidator:
    def __init__(self):
        # Regex to find numbers triggers, float, currency, with optional suffixes M/B/K/mn/bn
        # Examples: $10M, 50%, 100,000, 50bn. Matches start with word boundary or non-word chars (like $)
        # Negative lookbehind to avoid matching "1" in "node_1" or "v1"
        self.number_pattern = re.compile(r'(?<![\w])\$?\d+(?:,\d{3})*(?:\.\d+)?(?:%|[MmBbKk]|(?:[MmBb]n))?')
        # Regex to find references like [node_id]
        self.ref_pattern = re.compile(r'\[([a-zA-Z0-9_\-]+)\]')

    def validate(self, text: str, allowed_numbers: Set[float], available_node_ids: Set[str]) -> bool:
        """
        Validates the generated text.
        1. All numbers must roughly match allowed numbers (with tolerance).
        2. All references must exist in available_node_ids.
        """
        if not self._validate_numbers(text, allowed_numbers):
            print("Validation Failed: Hallucinated Number detected.")
            return False
            
        if not self._validate_references(text, available_node_ids):
            print("Validation Failed: Invalid or Missing Reference.")
            return False
            
        return True

    def _validate_numbers(self, text: str, allowed_numbers: Set[float], tolerance: float = 0.05) -> bool:
        matches = self.number_pattern.findall(text)
        for match in matches:
            # Normalize and parse
            clean = match.replace('$', '').replace(',', '')
            is_percent = '%' in clean
            clean = clean.replace('%', '')
            
            multiplier = 1.0
            lower = clean.lower()
            if lower.endswith('p'): continue # Skip if it matches something weird like specific paragraph refs, though unlikely with this regex
            
            if lower.endswith('m') or lower.endswith('mn'):
                multiplier = 1_000_000.0
                clean = re.sub(r'[mM](?:[nN])?$', '', clean)
            elif lower.endswith('b') or lower.endswith('bn'):
                multiplier = 1_000_000_000.0
                clean = re.sub(r'[bB](?:[nN])?$', '', clean)
            elif lower.endswith('k'):
                multiplier = 1_000.0
                clean = re.sub(r'[kK]$', '', clean)
                
            try:
                val = float(clean) * multiplier
                if is_percent:
                    val = val / 100.0
                
                # Check if this val matches any allowed number
                # We check matches. If a number is in text but NOT in allowed_numbers, it's a hallucination.
                # Exception: Years (e.g., 2023). We can use a heuristic: integers between 1900-2100 allowed?
                # For strictness, let's assume ALL numbers must be sourced.
                
                # Heuristic for years:
                if 1900 <= val <= 2100 and float(val).is_integer():
                     # If it's a year, we might allow it, OR we demand years be in the graph too.
                     # Let's check allowed first.
                     pass

                is_valid = any(
                    abs(val - allowed) / (abs(allowed) + 1e-9) <= tolerance 
                    for allowed in allowed_numbers
                )
                if not is_valid:
                    # Double check if it's a year not in the allowed list but looks valid?
                    # Strict mode: No.
                    print(f"Hallucination detected: {match} (Parsed: {val}) not in allowed numbers.")
                    return False
            except ValueError:
                continue 
        return True

    def _validate_references(self, text: str, available_ids: Set[str]) -> bool:
        refs = self.ref_pattern.findall(text)
        # Rule: At least one ref per paragraph? Or just all refs must be valid?
        # Let's enforce: All refs must be valid.
        for ref in refs:
            if ref not in available_ids:
                return False
        return True
