"""Elementary command handlers: user onboarding and assistance."""

from aiogram.types import InlineKeyboardMarkup

from config import configuration
from keyboards import build_quick_actions_keyboard


def _extract_bot_identifier() -> str:
    """Parse bot identifier from the authentication token.

    Telegram bot tokens follow format: <bot_id>:<token>
    The identifier represents the bot_id portion (e.g., 'MyBot' from 'MyBot:abc123...').
    """
    bot_token = configuration.bot_token
    if ":" in bot_token:
        return bot_token.split(":")[0]
    return "LMS Bot"


async def process_start_command() -> tuple[str, InlineKeyboardMarkup]:
    """Generate a personalized welcome message with quick action buttons."""
    bot_identifier = _extract_bot_identifier()
    text = (
        f"Welcome to {bot_identifier}!\n\n"
        "I can help you check your LMS labs and scores.\n"
        "You can type questions in plain English, like:\n"
        "• 'Which lab has the lowest pass rate?'\n"
        "• 'Show me scores for lab 4'\n"
        "• 'Who are the top 5 students?'\n\n"
        "Or use the buttons below!"
    )
    keyboard = build_quick_actions_keyboard()
    return text, keyboard


async def process_help_command() -> str:
    """Display comprehensive documentation of all available bot commands."""
    return (
        "Available commands:\n\n"
        "  /start — Welcome message\n"
        "  /help — Show this help message\n"
        "  /health — Check if the LMS backend is running\n"
        "  /labs — List all available labs\n"
        "  /scores <lab> — Get your scores for a specific lab\n\n"
        "You can also type natural language questions like:\n"
        "• 'what labs are available?'\n"
        "• 'which lab has the best scores?'\n"
        "• 'show me the top 10 students'"
    )
