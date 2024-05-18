"""
This module contains the main functionality of a Telegram bot.
It includes functions for adding admins,
listing admins, setting special limits, and creating a config and more...
"""

import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram_bot.utils import (
    add_admin_to_config,
    add_base_information,
    check_admin,
    get_special_limit_list,
    handel_special_limit,
    read_json_file,
    remove_admin_from_config,
)

(
    GET_DOMAIN,
    GET_PORT,
    GET_USERNAME,
    GET_PASSWORD,
    GET_CONFIRMATION,
    GET_CHAT_ID,
    GET_SPECIAL_LIMIT,
    GET_LIMIT_NUMBER,
    GET_CHAT_ID_TO_REMOVE,
) = range(9)

application = (
    ApplicationBuilder().token("").build()
)


async def send_logs(msg):
    """Send logs to all admins."""
    print("Here!")
    admins = await check_admin()
    print(admins)
    for admin in admins:
        print(admin, msg)
        try:
            await application.bot.sendMessage(
                chat_id=admin, text=msg, parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to send message to admin {admin}: {e}")


async def add_admin(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Adds an admin to the bot.
    At first checks if the user has admin privileges.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    if len(await check_admin()) > 5:
        await update.message.reply_html(
            text="You set more than '5' admins you need to delete one of them to add a new admin\n"
            + "check your active admins with /admins_list\n"
            + "you can delete with /remove_admin command"
        )
        return ConversationHandler.END
    await update.message.reply_html(text="Send chat id: ")
    return GET_CHAT_ID


async def get_chat_id(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Adds a new admin if the provided chat ID is valid and not already an admin.
    """
    new_admin_id = update.message.text.strip()
    try:
        if await add_admin_to_config(new_admin_id):
            await update.message.reply_html(
                text=f"Admin <code>{new_admin_id}</code> added successfully!"
            )
        else:
            await update.message.reply_html(
                text=f"Admin <code>{new_admin_id}</code> already exists!"
            )
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/add_admin</b>"
        )
    return ConversationHandler.END


async def admins_list(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a list of current admins.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    admins = await check_admin()
    if admins:
        admins_str = "\n- ".join(map(str, admins))
        await update.message.reply_html(text=f"Admins: \n-{admins_str}")
    else:
        await update.message.reply_html(text="No admins found!")
    return ConversationHandler.END


async def check_admin_privilege(update: Update):
    """
    Checks if the user has admin privileges.
    """
    admins = await check_admin()
    if not admins:
        await add_admin_to_config(update.effective_chat.id)
    admins = await check_admin()
    if update.effective_chat.id not in admins:
        await update.message.reply_html(
            text="Sorry, you do not have permission to execute this command."
        )
        return ConversationHandler.END


async def set_special_limit(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    set a special limit for a user.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_html(
        text="Please send the username. For example: <code>Test_User</code>"
    )
    return GET_SPECIAL_LIMIT


async def get_special_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    get the number of limit for a user.
    """
    context.user_data["selected_user"] = update.message.text.strip()
    await update.message.reply_html(
        text="Please send the Number of limit. For example: <code>4</code> or <code>2</code>"
    )
    return GET_LIMIT_NUMBER


async def get_limit_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sets the special limit for a user if the provided input is a valid number.
    """
    try:
        context.user_data["limit_number"] = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/set_special_limit</b>"
        )
        return ConversationHandler.END
    out_put = await handel_special_limit(
        context.user_data["selected_user"], context.user_data["limit_number"]
    )
    if out_put[0]:
        await update.message.reply_html(
            text=f"<code>{context.user_data['selected_user']}</code> already has a"
            + " special limit. Change it with new value"
        )
    await update.message.reply_html(
        text=f"Special limit for <code>{context.user_data['selected_user']}</code>"
        + f" set to <code>{out_put[1]}</code> successfully!"
    )
    return ConversationHandler.END


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Start function for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_html(
        text="Command List:\n<b>/start</b> \n<code>start the bot</code>\n"
        + "<b>/create_config</b> \n"
        + "<code>Config panel information (username, password, ...)</code>\n"
        + "<b>/set_special_limit</b> \n<code>set each"
        + " user ip limit like: test_user limit: 5 ips</code>"
        + "\n<b>/show_special_limit</b> \n<code>show special limit list</code>"
        + "\n<b>/add_admin</b>\n<code>"
        + "Giving access to another chat ID and creating a new admin for the bot</code>"
        + "\n<b>/admins_list</b>\n<code>Show the list of active bot admins</code>"
        + "\n<b>/remove_admin</b>\n<code>An admin's access will be removed from this bot</code>"
    )


async def create_config(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Add panel domain, username, and password to add into the config file.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    if os.path.exists("config.json"):
        await update.message.reply_html(text="You set configuration before!")
        data = await read_json_file()
        domain = data.get("PANEL_DOMAIN", "Not set")
        username = data.get("PANEL_USERNAME", "Not set")
        password = data.get("PANEL_PASSWORD", "Not set")
        await update.message.reply_html(
            text="<b>Current configuration:</b>\n"
            + f"Domain: <code>{domain}</code>\n"
            + f"Username: <code>{username}</code>\n"
            + f"Password: <code>{password}</code>\n"
            + "Do you want to change these settings? <code>(yes/no)</code>"
        )
        return GET_CONFIRMATION
    await update.message.reply_html(
        text="So now give me your <b>panel address!</b>\n"
        + "Send The Domain or Ip with Port\n"
        + "like: <code>sub.domain.com:8333</code> Or <code>95.12.153.87:443</code> \n"
        + "<b>without</b> <code>https://</code> or <code>http://</code> or anything else",
    )
    return GET_DOMAIN


async def get_confirmation(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Get confirmation for change panel information.
    """
    if update.message.text.lower() == "yes" or update.message.text.lower() == "y":
        await update.message.reply_html(
            text="So now give me your <b>panel address!</b>\n"
            + "Send The Domain or Ip with Port\n"
            + "like: <code>sub.domain.com:8333</code> Or <code>95.12.153.87:443</code> \n"
            + "<b>without</b> <code>https://</code> or <code>http://</code> or anything else",
        )
        return GET_DOMAIN
    return ConversationHandler.END


async def get_domain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get panel domain form user"""
    context.user_data["domain"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your Username: ",
    )
    return GET_USERNAME


async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get panel username form user"""
    context.user_data["username"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your Password: ",
    )
    return GET_PASSWORD


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get panel password form user"""
    context.user_data["password"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please wait to check panel address, username and password...",
    )
    try:
        await add_base_information(
            context.user_data["domain"],
            context.user_data["password"],
            context.user_data["username"],
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Config saved successfully 🎊"
        )
    except ValueError:
        await update.message.reply_html(
            text="<b>There is a problem with your information check them again!</b>"
            + " (also make sure the panel is running)"
            + "\n"
            + f"Panel Address: <code>{context.user_data['domain']}</code>\n"
            + f"Username: <code>{context.user_data['username']}</code>\n"
            + f"Password: <code>{context.user_data['password']}</code>\n"
            + "--------\n"
            + "Try again /create_config",
        )

    return ConversationHandler.END


async def remove_admin(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Removes a admin form admin list"""
    check = await check_admin_privilege(update)
    if check:
        return check
    admins_count = len(await check_admin())
    if admins_count == 1:
        await update.message.reply_html(
            text="there is just <b>1</b> active admin remain."
            + " <b>if you delete this chat id, then first person start bot "
            + "is new admin</b> or <b>add admin chat id</b> in <code>config.json</code> file"
        )
    await update.message.reply_html(text="Send chat id of the admin to remove: ")
    return GET_CHAT_ID_TO_REMOVE


async def get_chat_id_to_remove(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Get admin chat id to delete it form admin list"""
    try:
        admin_id_to_remove = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/remove_admin</b>"
        )
        return ConversationHandler.END
    if await remove_admin_from_config(admin_id_to_remove):
        await update.message.reply_html(
            text=f"Admin <code>{admin_id_to_remove}</code> removed successfully!"
        )
    else:
        await update.message.reply_html(
            text=f"Admin <code>{admin_id_to_remove}</code> does not exist!"
        )
    return ConversationHandler.END


start_handler = CommandHandler("start", start)
application.add_handler(start_handler)
upload_handler = ConversationHandler(
    entry_points=[CommandHandler("create_config", create_config)],
    states={
        GET_CONFIRMATION: [MessageHandler(filters.TEXT, get_confirmation)],
        GET_DOMAIN: [MessageHandler(filters.TEXT, get_domain)],
        GET_USERNAME: [MessageHandler(filters.TEXT, get_username)],
        GET_PASSWORD: [MessageHandler(filters.TEXT, get_password)],
    },
    fallbacks=[],
)
application.add_handler(upload_handler)
special_limit_handler = ConversationHandler(
    entry_points=[
        CommandHandler("set_special_limit", set_special_limit),
    ],
    states={
        GET_SPECIAL_LIMIT: [MessageHandler(filters.TEXT, get_special_limit)],
        GET_LIMIT_NUMBER: [MessageHandler(filters.TEXT, get_limit_number)],
    },
    fallbacks=[],
)
application.add_handler(upload_handler)

application.add_handler(special_limit_handler)


async def show_special_limit_function(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
):
    """Show special limit list for all users."""
    out_put = await get_special_limit_list()
    for user in out_put:
        await update.message.reply_html(text=f"{user}")


show_special_limit_handler = ConversationHandler(
    entry_points=[
        CommandHandler("show_special_limit", show_special_limit_function),
    ],
    states={},
    fallbacks=[],
)
application.add_handler(show_special_limit_handler)
add_admin_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add_admin", add_admin),
    ],
    states={
        GET_CHAT_ID: [MessageHandler(filters.TEXT, get_chat_id)],
    },
    fallbacks=[],
)
list_admins_handler = CommandHandler("admins_list", admins_list)

application.add_handler(add_admin_handler)
application.add_handler(list_admins_handler)

remove_admin_handler = ConversationHandler(
    entry_points=[
        CommandHandler("remove_admin", remove_admin),
    ],
    states={
        GET_CHAT_ID_TO_REMOVE: [MessageHandler(filters.TEXT, get_chat_id_to_remove)],
    },
    fallbacks=[],
)
application.add_handler(remove_admin_handler)


def run_telegram_bot():
    """Run the telegram bot"""
    application.run_polling()
