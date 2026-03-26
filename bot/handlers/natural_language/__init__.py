"""Natural language message handler using LLM intent routing."""

from services.intent_router import dispatch_intent


async def process_natural_language_message(text: str, debug: bool = False) -> str:
    """
    Process a natural language message using the LLM intent router.

    Args:
        text: The user's message text
        debug: If True, enable debug logging to stderr

    Returns:
        The LLM's response text
    """
    return await dispatch_intent(text, debug=debug)
