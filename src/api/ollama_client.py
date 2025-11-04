"""
Ollama API client for communicating with local LLM models
"""
import httpx
import json
from typing import Iterator, List, Dict, Any
from ..utils.exceptions import OllamaConnectionError, ModelNotFoundError
from ..utils.logger import setup_logger

logger = setup_logger("ollama_client", "logs/app.log")


class OllamaClient:
    """
    Client for interacting with the Ollama API

    The Ollama API provides endpoints for:
    - Listing available models
    - Generating chat completions
    - Streaming responses
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client

        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.Client(timeout=60.0)
        logger.info(f"Initialized Ollama client with base URL: {self.base_url}")

    def check_connection(self) -> bool:
        """
        Verify that Ollama is running and accessible

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            logger.info("Successfully connected to Ollama")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False

    def list_models(self) -> List[str]:
        """
        Fetch list of available models from Ollama

        Returns:
            List of model names

        Raises:
            OllamaConnectionError: If cannot connect to Ollama
        """
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()

            # Extract model names from response
            models = [model["name"] for model in data.get("models", [])]
            logger.info(f"Found {len(models)} available models")
            return models

        except httpx.HTTPError as e:
            logger.error(f"HTTP error while listing models: {e}")
            raise OllamaConnectionError(f"Failed to list models: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while listing models: {e}")
            raise OllamaConnectionError(f"Failed to list models: {e}")

    def generate_stream(
        self,
        model: str,
        messages: List[Dict[str, str]]
    ) -> Iterator[str]:
        """
        Generate streaming chat completion from Ollama

        This method sends a chat request to Ollama and yields response chunks
        as they arrive, enabling real-time display of the AI's response.

        Args:
            model: Name of the model to use (e.g., "llama2", "mistral")
            messages: List of message dicts with 'role' and 'content' keys

        Yields:
            String chunks of the response as they arrive

        Raises:
            OllamaConnectionError: If request fails
        """
        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": messages,
                "stream": True  # Enable streaming
            }

            logger.info(f"Sending streaming request to model: {model}")
            logger.debug(f"Request payload: {payload}")

            # Make streaming POST request
            with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120.0
            ) as response:
                response.raise_for_status()

                # Process each line of the streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            # Parse JSON response
                            chunk_data = json.loads(line)

                            # Extract message content from chunk
                            if "message" in chunk_data:
                                content = chunk_data["message"].get("content", "")
                                if content:
                                    yield content

                            # Check if streaming is complete
                            if chunk_data.get("done", False):
                                logger.info("Streaming completed")
                                break

                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON chunk: {e}")
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during streaming: {e}")
            raise OllamaConnectionError(f"Streaming failed: {e}")
        except httpx.RequestError as e:
            logger.error(f"Request error during streaming: {e}")
            raise OllamaConnectionError(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}")
            raise OllamaConnectionError(f"Streaming failed: {e}")

    def close(self) -> None:
        """Close the HTTP client connection"""
        self.client.close()
        logger.info("Closed Ollama client connection")
