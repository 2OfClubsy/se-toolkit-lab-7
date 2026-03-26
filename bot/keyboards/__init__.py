"""Inline keyboard definitions for the Telegram bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Construct inline keyboard with quick action buttons.

    These buttons help users discover common queries without typing.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="📚 Available Labs",
                callback_data="quick_labs",
            ),
            InlineKeyboardButton(
                text="💚 Backend Health",
                callback_data="quick_health",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📊 My Scores",
                callback_data="quick_scores",
            ),
            InlineKeyboardButton(
                text="🏆 Top Students",
                callback_data="quick_top",
            ),
        ],
        [
            InlineKeyboardButton(
                text="❓ Help",
                callback_data="quick_help",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_lab_selection_keyboard(labs: list[dict]) -> InlineKeyboardMarkup:
    """
    Construct inline keyboard for selecting a laboratory.

    Args:
        labs: List of lab dicts with 'title' and optional 'id' keys.
    """
    keyboard = []
    row = []

    for lab in labs[:10]:  # Limit to 10 buttons
        # Extract lab ID from title or use title as ID
        lab_id = lab.get("id", lab.get("title", ""))
        # Clean up lab title for button text
        title = lab.get("title", str(lab_id))
        if len(title) > 20:
            title = title[:17] + "..."

        row.append(
            InlineKeyboardButton(
                text=title,
                callback_data=f"lab_select_{lab_id}",
            )
        )

        # Start new row after 2 buttons
        if len(row) >= 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_back_keyboard() -> InlineKeyboardMarkup:
    """Construct a simple back button keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="↩️ Back",
                    callback_data="back",
                )
            ]
        ]
    )
