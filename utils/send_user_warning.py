import httpx
import asyncio
from utils.read_config import read_config

async def send_user_warning(chat_id: str, message: str):
    config = await read_config()
    token = config.get("SECOND_BOT_TOKEN")

    if not token:
        print("?? SECOND_BOT_TOKEN not set in config.json")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, data=payload)
    except Exception as e:
        print(f"?? Failed to send user message: {e}")
