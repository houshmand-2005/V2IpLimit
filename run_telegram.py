"""Run the telegram bot."""

import asyncio

from telegram_bot.main import application


async def run_telegram_bot():
    """Run the telegram bot."""
    while True:
        try:
            async with application:
                await application.start()
                await application.updater.start_polling()
                while True:
                    await asyncio.sleep(40)
        except Exception:  # pylint: disable=broad-except
            continue
