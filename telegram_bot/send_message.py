"""
Send logs to telegram bot.
"""

from telegram_bot.main import application
from telegram_bot.utils import check_admin


async def send_logs(msg):
    """Send logs to all admins."""
    admins = await check_admin()
    if admins:
        for admin in admins:
            try:
                await application.bot.sendMessage(
                    chat_id=admin, text=msg, parse_mode="HTML"
                )
            except Exception as e:  # pylint: disable=broad-except
                print(f"Failed to send message to admin {admin}: {e}")
