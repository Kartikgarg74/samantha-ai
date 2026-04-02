"""LLM provider abstraction — supports Gemini API and local Ollama fallback."""

import logging
import os
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OLLAMA_TIMEOUT = 15  # seconds for queries
OLLAMA_HEALTH_TIMEOUT = 2  # seconds for health check


class LLMProvider:
    """Unified interface for LLM inference. Gemini primary, Ollama fallback."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = None
        self._init_provider()

    def _init_provider(self):
        """Initialize the best available LLM provider."""
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.provider_name = "gemini"
                logger.info("LLM provider initialized: Gemini")
                return
            except ImportError:
                logger.warning("google-generativeai not installed. Trying Ollama fallback.")
            except Exception as e:
                logger.warning("Gemini init failed: %s. Trying Ollama fallback.", e)

        # Try Ollama as fallback
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/tags", timeout=OLLAMA_HEALTH_TIMEOUT)
            if resp.status_code == 200:
                self.provider_name = "ollama"
                logger.info("LLM provider initialized: Ollama")
                return
        except Exception:
            pass

        self.provider_name = "none"
        logger.warning("No LLM provider available. Set GOOGLE_API_KEY or run Ollama.")

    def query(self, user_input: str, system_prompt: str = "") -> Dict[str, Any]:
        """Send a query to the LLM and return text + optional structured commands."""
        if self.provider_name == "gemini":
            return self._query_gemini(user_input, system_prompt)
        elif self.provider_name == "ollama":
            return self._query_ollama(user_input, system_prompt)
        else:
            return {"text": f"No LLM available. You said: {user_input}", "commands": None}

    def _query_gemini(self, user_input: str, system_prompt: str) -> Dict[str, Any]:
        """Query Google Gemini API."""
        try:
            prompt = f"{system_prompt}\n\nUser: {user_input}" if system_prompt else user_input
            response = self.model.generate_content(prompt)
            text = response.text
            commands = self._extract_json_commands(text)
            return {"text": text, "commands": commands}
        except AttributeError:
            logger.error("Gemini returned empty response (no .text attribute)")
            return {"text": "I couldn't generate a response. Please try again.", "commands": None}
        except Exception as e:
            logger.error("Gemini query failed: %s", e)
            return {"text": "Sorry, the AI service encountered an error. Please try again.", "commands": None}

    def _query_ollama(self, user_input: str, system_prompt: str) -> Dict[str, Any]:
        """Query local Ollama instance."""
        import requests
        try:
            payload = {
                "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
                "prompt": user_input,
                "system": system_prompt,
                "stream": False,
            }
            resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=OLLAMA_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            text = data.get("response", "")
            commands = self._extract_json_commands(text)
            return {"text": text, "commands": commands}
        except requests.exceptions.Timeout:
            logger.error("Ollama query timed out after %ds", OLLAMA_TIMEOUT)
            return {"text": "The AI took too long to respond. Please try again.", "commands": None}
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama at localhost:11434")
            return {"text": "Cannot reach the local AI. Is Ollama running?", "commands": None}
        except Exception as e:
            logger.error("Ollama query failed: %s", e)
            return {"text": "The local AI encountered an error. Please try again.", "commands": None}

    def _extract_json_commands(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract structured JSON commands from LLM response."""
        try:
            start = text.find('```json')
            if start != -1:
                end = text.find('```', start + 7)
                if end != -1:
                    return json.loads(text[start + 7:end].strip())
        except json.JSONDecodeError:
            pass
        return None
