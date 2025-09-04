import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = ""
ADMIN_ID = 
SEEN_USERS_FILE = "seen_users.json"

# خواندن لیست آیدی‌های ذخیره‌شده
def load_seen_users():
    if os.path.exists(SEEN_USERS_FILE):
        try:
            with open(SEEN_USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# ذخیره‌سازی لیست آیدی‌ها
def save_seen_users(users_list):
    with open(SEEN_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users_list, f)

# هندلر دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    seen_users = load_seen_users()

    if user_id not in seen_users:
        # ارسال پیام به ادمین فقط بار اول
        username = f"@{user.username}" if user.username else "ندارد"
        name = user.full_name if user.full_name else "نام نامشخص"
        admin_message = (
            f"✅ کاربر جدید استارت زد:\n"
            f"<b>ID:</b> <code>{user_id}</code>\n"
            f"<b>Username:</b> {username}\n"
            f"<b>Name:</b> {name}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="HTML")

        # ثبت کاربر
        seen_users.append(user_id)
        save_seen_users(seen_users)

        # خوش‌آمدگویی به کاربر
        await context.bot.send_message(
            chat_id=user.id,
            text="👋 سلام! شما با موفقیت در ربات ثبت شدید.\n⚠️ هشدارهای مصرف سرویس از طریق همین ربات ارسال خواهد شد."
        )

# هندلر دستور /آمار و /امار
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != str(ADMIN_ID):
        return  # فقط ادمین مجاز است

    seen_users = load_seen_users()
    count = len(seen_users)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📊 تا این لحظه <b>{count}</b> کاربر ربات را استارت کرده‌اند.",
        parse_mode="HTML"
    )


# اجرای ربات
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))  # دستور /stats به جای /آمار
    app.run_polling()


if __name__ == "__main__":
    main()
