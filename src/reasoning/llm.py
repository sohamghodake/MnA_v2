import ollama
from typing import Dict
from src.config import settings


class OllamaClient:
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama.base_url)
        self.model = settings.ollama.model

    def generate(self, prompt: str, system: str = None) -> str:
        """Generates a response from the LLM using the ollama SDK."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
            )
            return response.message.content
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def generate_json(self, prompt: str, schema: Dict, system: str = None) -> Dict:
        """Generates structured JSON output using the ollama SDK."""
        import json
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                format="json",
            )
            text = response.message.content
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Failed to generate JSON: {e}")
