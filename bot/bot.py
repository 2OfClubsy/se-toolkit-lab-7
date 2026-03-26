"""
LMS Telegram Bot — Main Application Module

This module serves as the entry point for the Telegram bot application.
It supports two execution modes: running as a live bot or testing handlers locally.

Examples:
    uv run bot.py                    # Launch the Telegram bot
    uv run bot.py --test "/start"    # Execute command handler in test mode
    uv run bot.py --test "..."       # Test LLM intent routing for natural language
"""

import argparse
import asyncio
import logging
from typing import Callable, Awaitable

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject

from config import configuration
from handlers import (
    process_start_command,
    process_help_command,
    process_health_check,
    process_labs_list,
    process_scores_query,
)
from handlers.natural_language import process_natural_language_message

# Initialize application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Central command registry: stores command names mapped to their async handler functions
_command_registry: dict[str, Callable] = {}


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
    def decorator(func: Callable) -> Callable:
        _command_registry[name] = func
        return func
    return decorator


def get_handler(command: str) -> Callable | None:
    """Retrieve a registered handler function by its command name."""
    return _command_registry.get(command)


async def execute_test_mode(input_text: str) -> None:
    """
    Execute a command handler or LLM router based on input in test mode.

    - If input starts with '/', treat as a command
    - Otherwise, route through LLM for natural language processing

    Args:
        input_text: The test input string (command or natural language)
    """
    import sys

    # Check if this is a command (starts with /)
    if input_text.startswith("/"):
        # Parse command (e.g., "/start" -> "start", "/scores lab-04" -> "scores")
        parts = input_text.lstrip("/").split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        handler = get_handler(cmd)
        if handler is None:
            print(f"Unknown command: {input_text}")
            print("Use /help to see available commands.")
            return

        try:
            # Call handler with args if it accepts them
            import inspect
            sig = inspect.signature(handler)
            if len(sig.parameters) > 0:
                response = await handler(*args)
            else:
                response = await handler()
            print(response)
        except TypeError as e:
            if "missing" in str(e):
                print(f"Error: Command '{cmd}' requires arguments. Usage: /{cmd} <arg>")
            else:
                print(f"Error executing command: {e}")
                raise
        except Exception as e:
            print(f"Error executing command: {e}")
            raise
    else:
        # Natural language message - route through LLM
        print(f"[llm] Processing: {input_text}", file=sys.stderr)
        try:
            response = await process_natural_language_message(input_text, debug=True)
            print(response)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            raise


async def launch_telegram_bot() -> None:
    """Initialize and start the Telegram bot to process incoming messages."""
    bot = Bot(token=configuration.bot_token)
    dp = Dispatcher()

    # Helper to send response with optional keyboard
    async def send_response(message: types.Message, response) -> None:
        """Send response handling both tuple (text, keyboard) and plain text."""
        if isinstance(response, tuple):
            text, keyboard = response
            await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(response)

    # Bind all registered commands to aiogram message handlers
    for cmd_name, handler_func in _command_registry.items():
        # Wrapper function to execute handler and send response to user
        async def command_wrapper(message: types.Message, cmd=cmd_name) -> None:
            try:
                handler = _command_registry[cmd]
                # Extract arguments from message text (e.g., "/scores lab-01" -> ["lab-01"])
                parts = message.text.split()[1:] if message.text else []
                import inspect
                sig = inspect.signature(handler)
                if len(sig.parameters) > 0:
                    response = await handler(*parts)
                else:
                    response = await handler()
                await send_response(message, response)
            except Exception as e:
                logger.error(f"Error handling command: {e}")
                await message.answer("Sorry, something went wrong.")

        # Attach handler to aiogram's command filter
        dp.message.register(command_wrapper, Command(cmd_name))

    # Handle callback queries from inline buttons
    async def handle_callback_query(callback: types.CallbackQuery) -> None:
        """Process inline button callback queries."""
        data = callback.data
        message = callback.message

        try:
            if data == "quick_labs":
                response = await process_labs_list()
                await message.answer(response)
            elif data == "quick_health":
                response = await process_health_check()
                await message.answer(response)
            elif data == "quick_scores":
                await message.answer("Please specify a lab, e.g., 'lab-01' or use /scores lab-01")
            elif data == "quick_top":
                await message.answer("Please specify a lab for top students, e.g., 'Show top 5 in lab-01'")
            elif data == "quick_help":
                response = await process_help_command()
                await message.answer(response)
            elif data == "back":
                await message.answer("Use /start to see main menu")

            # Acknowledge the callback
            await callback.answer()
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await callback.answer("Sorry, something went wrong.")

    dp.callback_query.register(handle_callback_query)

    # Handle all other text messages with the LLM intent router
    async def process_text_message(message: types.Message) -> None:
        try:
            # Skip if this is a command (starts with /)
            if message.text and message.text.startswith("/"):
                return

            response = await process_natural_language_message(message.text, debug=False)
            await message.answer(response)
        except Exception as e:
            logger.error(f"Error in LLM routing: {e}")
            await message.answer("Sorry, I'm having trouble understanding that right now.")

    dp.message.register(process_text_message)

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
        metavar="INPUT",
        help="Execute in test mode: command (--test '/start') or LLM routing (--test 'what labs...')"
    )
    args = parser.parse_args()

    if args.test:
        # Execute handler or LLM router locally
        asyncio.run(execute_test_mode(args.test))
    else:
        # Launch the live Telegram bot
        asyncio.run(launch_telegram_bot())


if __name__ == "__main__":
    main()
