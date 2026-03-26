"""Service layer modules for the LMS Telegram Bot.

This package provides backend services including API communication,
LLM integration, and intent routing for natural language processing.
"""

from .api_client import LMSAPIClient
from .llm_client import LLMClient
from .intent_router import dispatch_intent

__all__ = [
    "LMSAPIClient",
    "LLMClient",
    "dispatch_intent",
]
