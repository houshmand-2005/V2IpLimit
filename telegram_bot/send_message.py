import os
import re
from telegram_bot.main import application
from telegram_bot.utils import check_admin
import aiohttp
from utils.read_config import read_config

CHUNK_SIZE = 4000

def split_safely_by_code_tags(text: str, chunk_size: int) -> list[str]:

    tag_pattern = re.compile(r'(<code>|</code>)', flags=re.IGNORECASE)

    chunks = []
    current_chunk = []
    current_length = 0
    in_code_block = False 


    parts = tag_pattern.split(text)

    for part in parts:
        if part == '<code>':

            if not in_code_block and current_length + len(part) > chunk_size:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_length = 0

            in_code_block = True
            current_chunk.append(part)
            current_length += len(part)

        elif part == '</code>':
            current_chunk.append(part)
            current_length += len(part)
            in_code_block = False

            if current_length > chunk_size:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_length = 0

        else:

            seg_len = len(part)

            if not in_code_block and current_length + seg_len > chunk_size:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_length = 0

            current_chunk.append(part)
            current_length += seg_len


    if current_chunk:
        chunks.append(''.join(current_chunk))

    return chunks

async def send_logs(msg):

    log_file_path = "logs.txt"

    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write(msg)


    with open(log_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("github.com/houshmand-2005/V2IpLimit/", "")



    chunks = split_safely_by_code_tags(content, CHUNK_SIZE)


    admins = await check_admin()
    if not admins:
        print("No admins found.")
        os.remove(log_file_path)
        return

    retries = 2
    for admin in admins:
        for chunk in chunks:
            for _ in range(retries):
                try:
                    await application.bot.sendMessage(
                        chat_id=admin,
                        text=chunk,
                        parse_mode="HTML"
                    )
                    break
                except Exception as e:
                    print(f"Failed to send message to admin {admin}: {e}")


    os.remove(log_file_path)






async def send_user_warning_message(user_id: str, message: str) -> None:
    config = await read_config()
    token = config.get("SECOND_BOT_TOKEN")
    if not token:
        print("SECOND_BOT_TOKEN not found in config.")
        return
    try:
        # ??????? ???? ???? ?? user_id ??? '7076044336_eb5f'
        real_chat_id = user_id.split('_')[0]

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": real_chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload) as resp:
                if resp.status != 200:
                    print(f"Failed to send user message. Status: {resp.status}")
    except Exception as e:
        print(f"Error sending user message: {e}")


    


