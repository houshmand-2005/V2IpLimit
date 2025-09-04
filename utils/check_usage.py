# -*- coding: utf-8 -*-
import asyncio
from collections import Counter
from telegram_bot.send_message import send_user_warning_message, send_logs
from utils.logs import logger
from utils.panel_api import disable_user
from utils.read_config import read_config
from utils.types import PanelType, UserType

ACTIVE_USERS: dict[str, UserType] | dict = {}
USER_WARNINGS: dict[str, int] = {}

# Exempt usernames: if a username contains any of these, skip warnings/disable
EXEMPT_NAME_CONTAINS = ("hajmi",)

def _is_exempt_username(username: str) -> bool:
    u = (username or "").lower()
    return any(s in u for s in EXEMPT_NAME_CONTAINS)

async def check_ip_used() -> dict[str, list[str]]:
    """
    فقط لیستی از کاربران و IPهای فعال بیش از حد مجاز می‌سازد و لاگ را آماده می‌کند.
    """
    all_users_log: dict[str, list[str]] = {}
    for email in list(ACTIVE_USERS.keys()):
        data = ACTIVE_USERS[email]
        ip_counts = Counter(data.ip)
        filtered_ip = [ip for ip in data.ip if ip_counts[ip] > 2]
        data.ip = list(set(filtered_ip))
        all_users_log[email] = data.ip
        logger.info(data)

    total_ips = sum(len(ips) for ips in all_users_log.values())
    all_users_log = dict(sorted(all_users_log.items(), key=lambda x: len(x[1]), reverse=True))

    messages = [
        f"<code>{email}</code> with <code>{len(ips)}</code> active ip\n- " + "\n- ".join(ips)
        for email, ips in all_users_log.items() if ips
    ]
    logger.info("Number of all active ips: %s", str(total_ips))
    messages.append(f"---------\nCount Of All Active IPs: <b>{total_ips}</b>")
    messages.append("<code>github.com/houshmand-2005/V2IpLimit/</code>")

    shorter_messages = ["\n".join(messages[i:i + 100]) for i in range(0, len(messages), 100)]
    for message in shorter_messages:
        await send_logs(message)

    return all_users_log

async def check_users_usage(panel_data: PanelType):
    try:
        config_data = await read_config()
        all_users_log = await check_ip_used()
        except_users = config_data.get("EXCEPT_USERS", [])
        special_limit = config_data.get("SPECIAL_LIMIT", {})
        limit_number = config_data["GENERAL_LIMIT"]

        for user_name, user_ip in all_users_log.items():
            if user_name in except_users:
                continue

            user_limit_number = int(special_limit.get(user_name, limit_number))
            unique_ips = list(set(user_ip))

            if unique_ips and len(unique_ips) > user_limit_number:
                # شمارش اخطار - معاف‌ها را نمی‌شماریم
                if _is_exempt_username(user_name):
                    USER_WARNINGS[user_name] = 0
                else:
                    USER_WARNINGS[user_name] = USER_WARNINGS.get(user_name, 0) + 1

                if USER_WARNINGS[user_name] < 3:
                    message = (
                        f"⚠️ Warning {USER_WARNINGS[user_name]}/3 for <b>{user_name}</b>: "
                        f"{len(unique_ips)} active IPs (limit: {user_limit_number})\n"
                        f"IPs: <code>{', '.join(sorted(unique_ips))}</code>"
                    )
                    # اگر نمی‌خواهی برای معاف‌ها لاگ ادمین هم برود، این if را نگه دار
                    if not _is_exempt_username(user_name):
                        await send_logs(message)

                    if USER_WARNINGS[user_name] >= 2 and not _is_exempt_username(user_name):
                        await send_user_warning_message(
                            user_id=user_name,
                            message=(
                                f"⚠️ اکانت <code>{user_name}</code> توسط تعداد بیشتری از کاربر یا دستگاه نسبت به تعداد مجاز، در حال استفاده است.\n"
                                f"به همین دلیل، اخطار {USER_WARNINGS[user_name]}/3 برای این اکانت ثبت شده. اگه این روند ادامه پیدا کنه، اکانت به‌صورت خودکار غیرفعال می‌شود.\n\n"
                                "🔸 توجه: اگر فکر می‌کنی این پیام اشتباهی برات ارسال شده، ممکنه به خاطر تعویض اینترنت یا اتصال موقت از چند جا باشه. در این صورت اخطار را نادیده بگیر؛ "
                                "سیستم به صورت خودکار اگر شرایط نرمال بشه، اخطارها را پاک می‌کند.\n\n"
                                "🔹 خواهشاً به پشتیبانی پیام نده — چون این پیام‌ها خودکار ارسال می‌شوند و پشتیبانی به اکانت‌های غیرفعال‌شده رسیدگی نمی‌کند 🙏\n\n"
                                "مرسی از همراهی و رعایت قانون‌ها ❤️"
                            ),
                        )
                else:
                    # سومین بار: دیسیبل
                    message = f"⛔ <b>{user_name}</b> exceeded IP limit 3 times. Disabling..."
                    if not _is_exempt_username(user_name):
                        await send_logs(message)
                        await send_user_warning_message(
                            user_id=user_name,
                            message=(
                                f"⛔️ هشدار: اکانت <code>{user_name}</code> بیش از ۳ بار از حد مجاز اتصال IP عبور کرده است.\n"
                                "اکانت شما غیرفعال شد."
                            ),
                        )
                        try:
                            await disable_user(panel_data, UserType(name=user_name, ip=[]))
                        finally:
                            USER_WARNINGS[user_name] = 0
                    else:
                        # معاف‌ها را هرگز دیسیبل نکن
                        USER_WARNINGS[user_name] = 0

            else:
                if user_name in USER_WARNINGS:
                    USER_WARNINGS.pop(user_name, None)
                    print(f"[INFO] {user_name} رعایت کرد، اخطارش پاک شد.")

    except Exception as err:
        print(f"[FATAL ERROR] در اجرای check_users_usage خطایی پیش آمد: {err}")

    ACTIVE_USERS.clear()

async def run_check_users_usage(panel_data: PanelType) -> None:
    while True:
        await check_users_usage(panel_data)
        data = await read_config()
        await asyncio.sleep(int(data["CHECK_INTERVAL"]))
