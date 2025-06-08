"""OpenAI API client wrapper."""
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Async OpenAI API client."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL

    async def generate_response(self, prompt: str,
                                system_prompt: Optional[str] = None,
                                temperature: float = TEMPERATURE,
                                max_tokens: int = MAX_TOKENS) -> str:
        """Generate a response from ChatGPT."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I apologize, but I have encountered an error. Please try again later."

    async def generate_conversational_response(self,
                                               messages: List[Dict[str, str]],
                                               temperature: float = TEMPERATURE,
                                               max_tokens: int = MAX_TOKENS) -> str:
        """Generate a response for ongoing conversation."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I apologize, but I have encountered an error. Please try again later."