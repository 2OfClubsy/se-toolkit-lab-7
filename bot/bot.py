"""
LMS Telegram Bot — Main Application Module

This module serves as the entry point for the Telegram bot application.
It supports two execution modes: running as a live bot or testing handlers locally.

Examples:
    uv run bot.py                    # Launch the Telegram bot
    uv run bot.py --test "/start"    # Execute handler in test mode
"""

import argparse
import asyncio
import logging
from typing import Callable, Awaitable

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import configuration
from handlers import (
    process_start_command,
    process_help_command,
    process_health_check,
    process_labs_list,
    process_scores_query,
)

# Initialize application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Central command registry: stores command names mapped to their async handler functions
_command_registry: dict[str, Callable[[], Awaitable[str]]] = {}


def register_command(name: str) -> Callable:
    """
    Decorator factory for registering command handlers in the registry.

    Args:
        name: The command identifier (e.g., "start", "help")

    Returns:
        A decorator that registers the decorated function under the given command name

    Example:
        @register_command("start")
        async def process_start_command() -> str:
            return "Welcome!"
    """
    def decorator(func: Callable[[], Awaitable[str]]) -> Callable:
        _command_registry[name] = func
        return func
    return decorator


def get_handler(command: str) -> Callable[[], Awaitable[str]] | None:
    """Retrieve a registered handler function by its command name."""
    return _command_registry.get(command)


async def execute_test_mode(command: str) -> None:
    """
    Execute a command handler in isolation and output the result.

    This mode operates without network connectivity or Telegram API access,
    enabling local testing of command logic.

    Args:
        command: The command string to execute (e.g., "/start", "/scores lab-04")
    """
    # Extract command name from input (e.g., "/start" -> "start")
    cmd = command.lstrip("/").split()[0]

    handler = get_handler(cmd)
    if handler is None:
        print(f"Error: Unknown command '{command}'")
        print("Available commands:", ", ".join(_command_registry.keys()))
        return

    try:
        response = await handler()
        print(response)
    except Exception as e:
        print(f"Error executing command: {e}")
        raise


async def launch_telegram_bot() -> None:
    """Initialize and start the Telegram bot to process incoming messages."""
    bot = Bot(token=configuration.bot_token)
    dp = Dispatcher()

    # Bind all registered commands to aiogram message handlers
    for cmd_name, handler_func in _command_registry.items():
        # Wrapper function to execute handler and send response to user
        async def command_wrapper(message: types.Message, cmd=cmd_name) -> None:
            try:
                handler = _command_registry[cmd]
                response = await handler()
                await message.answer(response)
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                await message.answer("Sorry, something went wrong.")

        # Attach handler to aiogram's command filter
        dp.message.register(command_wrapper, Command(cmd_name))

    logger.info("Starting bot...")
    await dp.start_polling(bot)


# =============================================================================
# Command Registration
# =============================================================================

register_command("start")(process_start_command)
register_command("help")(process_help_command)
register_command("health")(process_health_check)
register_command("labs")(process_labs_list)
register_command("scores")(process_scores_query)


# =============================================================================
# Application Entry Point
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="LMS Telegram Bot Application")
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Execute in test mode with specified command (e.g., --test '/start')"
    )
    args = parser.parse_args()

    if args.test:
        # Execute handler locally without Telegram connection
        asyncio.run(execute_test_mode(args.test))
    else:
        # Launch the live Telegram bot
        asyncio.run(launch_telegram_bot())


if __name__ == "__main__":
    main()
