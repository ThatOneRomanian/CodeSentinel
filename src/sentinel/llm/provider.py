"""
LLM Provider abstraction layer for CodeSentinel Phase 2.

Provides a unified interface for different LLM providers with placeholder
implementations during the bootstrap phase.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

import os
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM provider.
        
        Args:
            prompt: The input prompt to send to the LLM
            
        Returns:
            The generated response as a string
        """
        pass


class DeepSeekProvider(LLMProvider):
    """Real DeepSeek API provider with environment variable configuration."""
    
    def __init__(self):
        """Initialize the DeepSeek provider with environment configuration."""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.timeout = 30  # seconds
        self.max_retries = 2
        
    def _is_configured(self) -> bool:
        """Check if the provider is properly configured with API key."""
        return bool(self.api_key)
    
    def _make_api_request(self, prompt: str) -> str:
        """
        Make actual API request to DeepSeek.
        
        Args:
            prompt: The input prompt
            
        Returns:
            The generated response
            
        Raises:
            ValueError: If API key is not configured
            ConnectionError: If network connection fails
            TimeoutError: If request times out
            Exception: For other API errors
        """
        if not self._is_configured():
            raise ValueError("DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable.")
        
        # Prepare the request data
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "max_tokens": 2048,
            "temperature": 0.7
        }
        
        # Convert to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Prepare the request
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "CodeSentinel/1.0"
        }
        
        request = Request(url, data=json_data, headers=headers, method="POST")
        
        # Make the request with retries
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    if response.status != 200:
                        raise HTTPError(url, response.status, "API request failed", response.headers, None)
                    
                    response_data = json.loads(response.read().decode('utf-8'))
                    
                    # Extract the response content
                    if 'choices' in response_data and len(response_data['choices']) > 0:
                        return response_data['choices'][0]['message']['content']
                    else:
                        raise ValueError("Invalid response format from DeepSeek API")
                        
            except HTTPError as e:
                last_error = f"HTTP Error {e.code}: {e.reason}"
                if e.code in [429, 500, 502, 503]:  # Retry on rate limits and server errors
                    if attempt < self.max_retries:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                raise ConnectionError(f"DeepSeek API error: {last_error}")
                
            except URLError as e:
                last_error = f"URL Error: {e.reason}"
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise ConnectionError(f"Network error: {last_error}")
                
            except TimeoutError:
                last_error = "Request timeout"
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise TimeoutError("DeepSeek API request timed out")
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON response from DeepSeek API: {e}")
                
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"Unexpected error calling DeepSeek API: {last_error}")
        
        # If we get here, all retries failed
        raise Exception(f"All retries failed. Last error: {last_error}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response from DeepSeek API.
        
        Args:
            prompt: The input prompt to send to the LLM
            
        Returns:
            The generated response as a string, or placeholder if not configured
        """
        # If not configured, return placeholder to maintain backward compatibility
        if not self._is_configured():
            return f"DeepSeek: This is a placeholder response. To enable real AI explanations, set DEEPSEEK_API_KEY environment variable. Prompt was: {prompt[:100]}..."
        
        try:
            return self._make_api_request(prompt)
        except Exception as e:
            # Return informative error message instead of crashing
            error_msg = f"DeepSeek API Error: {str(e)}. Prompt was: {prompt[:100]}..."
            return error_msg


class OpenAIProvider(LLMProvider):
    """Placeholder provider for OpenAI API."""
    
    def generate(self, prompt: str) -> str:
        """
        Generate a placeholder response for OpenAI.
        
        Args:
            prompt: The input prompt (ignored in placeholder)
            
        Returns:
            Static placeholder response
        """
        return "OpenAI: This is a placeholder response for Phase 2 bootstrap. Actual LLM integration will be implemented in Phase 2 development."


class LocalOllamaProvider(LLMProvider):
    """Placeholder provider for local Ollama models."""
    
    def generate(self, prompt: str) -> str:
        """
        Generate a placeholder response for local Ollama.
        
        Args:
            prompt: The input prompt (ignored in placeholder)
            
        Returns:
            Static placeholder response
        """
        return "LocalOllama: This is a placeholder response for Phase 2 bootstrap. Actual LLM integration will be implemented in Phase 2 development."


def get_provider(provider_name: str) -> LLMProvider:
    """
    Get an LLM provider instance by name.
    
    Args:
        provider_name: Name of the provider ("deepseek", "openai", "local_ollama")
        
    Returns:
        An instance of the requested LLM provider
        
    Raises:
        ValueError: If the provider name is not recognized
    """
    providers: Dict[str, LLMProvider] = {
        "deepseek": DeepSeekProvider(),
        "openai": OpenAIProvider(),
        "local_ollama": LocalOllamaProvider(),
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")
    
    return providers[provider_name]


def get_available_providers() -> List[str]:
    """
    Get list of available AI providers.
    
    Returns:
        List of provider names that are available
    """
    return ["deepseek", "openai", "local_ollama"]