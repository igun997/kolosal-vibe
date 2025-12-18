"""Kolosal LLM Client - OpenAI-compatible API client for Kolosal AI."""

from openai import OpenAI
from typing import Optional, Generator, List
import json
import httpx


class KolosalClient:
    """Client for Kolosal AI API (OpenAI-compatible)."""

    BASE_URL = "https://api.kolosal.ai/v1"
    DEFAULT_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL
        )

    def set_model(self, model: str):
        """Change the active model."""
        self.model = model

    @classmethod
    def list_models(cls, api_key: str) -> List[dict]:
        """Fetch available models from Kolosal API."""
        try:
            response = httpx.get(
                f"{cls.BASE_URL}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False
    ):
        """Send a chat completion request."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content

    def _stream_response(self, response) -> Generator[str, None, None]:
        """Stream response chunks."""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def generate_code(self, prompt: str, language: str = "python") -> dict:
        """Generate code based on a prompt."""
        system_prompt = f"""You are an expert {language} programmer. Generate clean, working code based on the user's request.

IMPORTANT RULES:
1. Return ONLY the code, no explanations before or after
2. Include necessary imports
3. Make the code complete and executable
4. Use proper error handling where appropriate
5. If you need to show output, use print statements

Wrap your code in triple backticks with the language identifier:
```{language}
# your code here
```"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = self.chat(messages, temperature=0.3)
        return self._extract_code(response, language)

    def _extract_code(self, response: str, language: str) -> dict:
        """Extract code block from LLM response."""
        # Try to find code block with language identifier
        import re

        # Pattern for ```language ... ```
        pattern = rf"```{language}\n?(.*?)```"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)

        if match:
            return {
                "code": match.group(1).strip(),
                "language": language,
                "raw_response": response
            }

        # Try generic code block
        pattern = r"```\n?(.*?)```"
        match = re.search(pattern, response, re.DOTALL)

        if match:
            return {
                "code": match.group(1).strip(),
                "language": language,
                "raw_response": response
            }

        # No code block found, return the whole response
        return {
            "code": response.strip(),
            "language": language,
            "raw_response": response
        }

    def analyze_error(self, code: str, error: str, language: str = "python") -> str:
        """Analyze an error and suggest a fix."""
        messages = [
            {
                "role": "system",
                "content": f"""You are a {language} debugging expert. Analyze the error and provide a corrected version of the code.

Return ONLY the fixed code wrapped in triple backticks:
```{language}
# fixed code here
```"""
            },
            {
                "role": "user",
                "content": f"""The following code produced an error:

```{language}
{code}
```

Error:
{error}

Please fix the code."""
            }
        ]

        response = self.chat(messages, temperature=0.2)
        return self._extract_code(response, language)

    def explain_code(self, code: str, language: str = "python") -> str:
        """Explain what a piece of code does."""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful programming tutor. Explain code clearly and concisely."
            },
            {
                "role": "user",
                "content": f"Explain this {language} code:\n\n```{language}\n{code}\n```"
            }
        ]

        return self.chat(messages, temperature=0.5)
