import requests
import json
from typing import List, Dict, Generator
from src.config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama.base_url
        self.model = settings.ollama.model

    def generate(self, prompt: str, system: str = None) -> str:
        """Generates a response from the LLM."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
            
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def generate_json(self, prompt: str, schema: Dict, system: str = None) -> Dict:
        """Generates structured JSON output."""
        # Note: Ollama's JSON mode is model-dependent.
        # We enforce it via prompt and format parameter if supported.
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
        if system:
            payload["system"] = system

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            text = response.json().get("response", "")
            return json.loads(text)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to generate JSON: {e}")
