"""Elementary command handlers: user onboarding and assistance."""


async def process_start_command() -> str:
    """Generate a welcome message for new users initiating the bot."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


async def process_help_command() -> str:
    """Provide a comprehensive list of all available bot commands."""
    return (
        "Available commands:\n"
        "  /start — Welcome message\n"
        "  /help — Show this help\n"
        "  /health — Check backend status\n"
        "  /labs — List available labs\n"
        "  /scores <lab> — Get scores for a lab"
    )
