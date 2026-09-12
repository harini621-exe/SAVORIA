"""
IBM watsonx.ai Client
Handles authentication and text generation against the IBM watsonx.ai foundation model API.
"""

import logging
import httpx
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class WatsonxClient:
    """
    Modular client for IBM watsonx.ai.
    Swap the model by changing IBM_MODEL_ID in .env — no code changes required.
    """

    IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self):
        self.settings = get_settings()
        self._token: Optional[str] = None

    def is_configured(self) -> bool:
        return bool(self.settings.IBM_API_KEY and self.settings.IBM_PROJECT_ID)

    async def _get_iam_token(self) -> str:
        """Exchange IBM API key for a short-lived IAM bearer token."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.IAM_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.settings.IBM_API_KEY,
                },
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"IBM IAM token request failed ({response.status_code}): {response.text}"
                )
            return response.json()["access_token"]

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Send a chat completion request to IBM watsonx.ai and return the generated text.

        Args:
            system_prompt: Instruction/role context for the model.
            user_prompt: The actual user message / generation task.
            max_tokens: Override default max tokens.
            temperature: Override default temperature.

        Returns:
            Generated text string.
        """
        if not self.is_configured():
            raise RuntimeError(
                "IBM watsonx.ai is not configured. "
                "Set IBM_API_KEY and IBM_PROJECT_ID in your .env file."
            )

        token = await self._get_iam_token()
        url = (
            f"{self.settings.IBM_WATSONX_URL}/ml/v1/text/chat?version=2023-05-29"
        )

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "project_id": self.settings.IBM_PROJECT_ID,
            "model_id": self.settings.IBM_MODEL_ID,
            "frequency_penalty": 0,
            "max_tokens": max_tokens or self.settings.MAX_TOKENS,
            "presence_penalty": 0,
            "temperature": temperature or self.settings.TEMPERATURE,
            "top_p": 1,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                url,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                json=payload,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"watsonx.ai generation failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected watsonx.ai response format: {data}"
            ) from exc


# Singleton instance — imported by agents
watsonx_client = WatsonxClient()
