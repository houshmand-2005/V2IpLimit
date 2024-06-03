"""
This module contains the main functionality of a Telegram bot.
It includes functions for adding admins,
listing admins, setting special limits, and creating a config and more...
"""

import asyncio
import os
import sys

try:
    from telegram import Update
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        ContextTypes,
        ConversationHandler,
        MessageHandler,
        filters,
    )
except ImportError:
    print(
        "Module 'python-telegram-bot' is not installed use:"
        + " 'pip install python-telegram-bot' to install it"
    )
    sys.exit()

from telegram_bot.utils import (
    add_admin_to_config,
    add_base_information,
    add_except_user,
    check_admin,
    get_special_limit_list,
    handel_special_limit,
    read_json_file,
    remove_admin_from_config,
    remove_except_user_from_config,
    save_check_interval,
    save_general_limit,
    save_time_to_active_users,
    show_except_users_handler,
    write_country_code_json,
)
from utils.read_config import read_config

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
    SET_COUNTRY_CODE,
    SET_EXCEPT_USERS,
    REMOVE_EXCEPT_USER,
    GET_GENERAL_LIMIT_NUMBER,
    GET_CHECK_INTERVAL,
    GET_TIME_TO_ACTIVE_USERS,
) = range(15)

data = asyncio.run(read_config())
try:
    bot_token = data["BOT_TOKEN"]
except KeyError as exc:
    raise ValueError("BOT_TOKEN is missing in the config file.") from exc
application = ApplicationBuilder().token(bot_token).build()


START_MESSAGE = """
✨<b>Commands List:</b>\n<b>/start</b> \n<code>start the bot</code>
<b>/create_config</b>
<code>Config panel information (username, password, ...)</code>
<b>/set_special_limit</b>
<code>set each user ip limit like: test_user limit: 5 ips</code>
<b>/show_special_limit</b> \n<code>show special limit list</code>
<b>/add_admin</b><code>
Giving access to another chat ID and creating a new admin for the bot</code>
<b>/admins_list</b>\n<code>Show the list of active bot admins</code>
<b>/remove_admin</b>\n<code>An admin's access will be removed from this bot</code>
<b>/country_code</b>\n<code>Set your country, Only IPs related to that country
are counted (to increase accuracy)</code>
<b>/set_except_user</b>\n<code>Set a user to except list</code>
<b>/remove_except_user</b>\n<code>Remove a user from except list</code>
<b>/show_except_users</b>\n<code>Show the list of except users</code>
<b>/set_general_limit_number</b>\n<code>Set the general limit number
(if user not in special limit list then this is they limit number)</code>
<b>/set_check_interval</b>\n<code>Set the check interval time </code>
<b>/set_time_to_active_users</b>\n<code>Set the time to active users</code>
<b>/backup</b> \n<code>Sends 'config.json' file</code>"""


async def send_logs(msg):
    """Send logs to all admins."""
    admins = await check_admin()
    for admin in admins:
        try:
            await application.bot.sendMessage(
                chat_id=admin, text=msg, parse_mode="HTML"
            )
        except Exception as error:  # pylint: disable=broad-except
            print(f"Failed to send message to admin {admin}: {error}")


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
        await update.message.reply_html(text=f"Admins: \n- {admins_str}")
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
    await update.message.reply_html(text=START_MESSAGE)


async def create_config(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Add panel domain, username, and password to add into the config file.
    """
    check = await check_admin_privilege(update)
    if check:
        return check
    if os.path.exists("config.json"):
        json_data = await read_json_file()
        domain = json_data.get("PANEL_DOMAIN")
        username = json_data.get("PANEL_USERNAME")
        password = json_data.get("PANEL_PASSWORD")
        if domain and username and password:
            await update.message.reply_html(text="You set configuration before!")
            await update.message.reply_html(
                text="After changing the configuration, you need to <b>restart</b> the bot.\n"
                + "Only this command needs restart other commands <b>don't need it.</b>"
            )
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
    if update.message.text.lower() in ["yes", "y"]:
        await update.message.reply_html(
            text="So now give me your <b>panel address!</b>\n"
            + "Send The Domain or Ip with Port\n"
            + "like: <code>sub.domain.com:8333</code> Or <code>95.12.153.87:443</code> \n"
            + "<b>without</b> <code>https://</code> or <code>http://</code> or anything else",
        )
        return GET_DOMAIN
    await update.message.reply_html(
        text=f"<code>{update.message.text}</code> received.\n"
        "Use <b>/create_config</b> when you change your mind."
    )
    return ConversationHandler.END


async def get_domain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get panel domain form user"""
    context.user_data["domain"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your Username: (For example: 'admin')",
    )
    return GET_USERNAME


async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get panel username form user"""
    context.user_data["username"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your Password: (For example: 'admin1234')",
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


async def show_special_limit_function(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
):
    """Show special limit list for all users."""
    check = await check_admin_privilege(update)
    if check:
        return check
    out_put = await get_special_limit_list()
    if out_put:
        for user in out_put:
            await update.message.reply_html(text=user)
    else:
        await update.message.reply_html(text="No special limit found!")


async def set_country_code(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Set the country code for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_html(
        "1. <code>IR</code> (Iran)\n"
        + "2. <code>RU</code> (Russia)\n"
        + "3. <code>CN</code> (China)\n"
        + "4. <code>None</code>, don't check the location\n"
        + "<b>just send the number of the country code like: <code>2</code> or <code>1</code></b>"
    )
    return SET_COUNTRY_CODE


async def write_country_code(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Write the country code to the config file."""
    country_code = update.message.text.strip()
    country_codes = {"1": "IR", "2": "RU", "3": "CN", "4": "None"}
    selected_country = country_codes.get(country_code, "None")
    await update.message.reply_html(
        f"Country code <code>{selected_country}</code> set successfully!"
    )
    await write_country_code_json(selected_country)
    return ConversationHandler.END


async def send_backup(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Send the backup file to the user."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_document(
        document=open("config.json", "r", encoding="utf8"),  # pylint: disable=consider-using-with
        caption="Here is the backup file!",
    )


async def set_except_users(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Set the except users for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_html(
        "Send the except (<code>users in this list have no limitation</code>) user:"
    )
    return SET_EXCEPT_USERS


async def set_except_users_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Write the except users to the config file."""
    except_user = update.message.text.strip()
    await add_except_user(except_user)
    await update.message.reply_html(
        f"Except user <code>{except_user}</code> added successfully!"
    )
    return ConversationHandler.END


async def remove_except_user(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """remove the except users for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_html("Send the except user to remove:")
    return REMOVE_EXCEPT_USER


async def remove_except_user_handler(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
):
    """remove the except users from the config file."""
    except_user = await remove_except_user_from_config(update.message.text.strip())
    if except_user:
        await update.message.reply_html(
            f"Except user <code>{except_user}</code> removed successfully!"
        )

    else:
        await update.message.reply_html(
            f"Except user <code>{except_user}</code> not found!"
        )
    return ConversationHandler.END


async def show_except_users(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Show the except users for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    messages = await show_except_users_handler()
    if messages:
        for message in messages:
            await update.message.reply_html(text=message)
    else:
        await update.message.reply_html(text="No except user found!")
    return ConversationHandler.END


async def get_general_limit_number(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """Get the general limit number for the bot."""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_text("Please send the general limit number:")
    return GET_GENERAL_LIMIT_NUMBER


async def get_general_limit_number_handler(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
):
    """Write the general limit number to the config file."""
    try:
        limit_number = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/set_general_limit_number</b>"
        )
        return ConversationHandler.END
    await save_general_limit(limit_number)
    await update.message.reply_text(f"General LIMIT_NUMBER set to {limit_number}")
    return ConversationHandler.END


async def get_check_interval(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """get the 'check_interval' variable that handel how often the bot check the users"""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_text(
        "Please send the check interval time like 210 (its recommended to set it to 240 seconds)"
    )
    return GET_CHECK_INTERVAL


async def get_check_interval_handler(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
):
    """save the 'check_interval' variable"""
    try:
        check_interval = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/set_check_interval</b>"
        )
        return ConversationHandler.END
    await save_check_interval(check_interval)
    await update.message.reply_text(f"CHECK_INTERVAL set to {check_interval}")
    return ConversationHandler.END


async def get_time_to_active_users(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """get the 'time_to_active' variable that handel how long user be not be active"""
    check = await check_admin_privilege(update)
    if check:
        return check
    await update.message.reply_text(
        "Please send the time to active users: like 600 (its in seconds)"
    )
    return GET_TIME_TO_ACTIVE_USERS


async def get_time_to_active_users_handler(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
):
    """save the 'time_to_active' variable"""
    try:
        time_to_active_users = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/set_time_to_active_users</b>"
        )
        return ConversationHandler.END
    await save_time_to_active_users(time_to_active_users)
    await update.message.reply_text(
        f"TIME_TO_ACTIVE_USERS set to {time_to_active_users}"
    )
    return ConversationHandler.END


application.add_handler(CommandHandler("start", start))
application.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("create_config", create_config)],
        states={
            GET_CONFIRMATION: [MessageHandler(filters.TEXT, get_confirmation)],
            GET_DOMAIN: [MessageHandler(filters.TEXT, get_domain)],
            GET_USERNAME: [MessageHandler(filters.TEXT, get_username)],
            GET_PASSWORD: [MessageHandler(filters.TEXT, get_password)],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("set_special_limit", set_special_limit),
        ],
        states={
            GET_SPECIAL_LIMIT: [MessageHandler(filters.TEXT, get_special_limit)],
            GET_LIMIT_NUMBER: [MessageHandler(filters.TEXT, get_limit_number)],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("set_time_to_active_users", get_time_to_active_users),
        ],
        states={
            GET_TIME_TO_ACTIVE_USERS: [
                MessageHandler(filters.TEXT, get_time_to_active_users_handler)
            ],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("set_check_interval", get_check_interval),
        ],
        states={
            GET_CHECK_INTERVAL: [
                MessageHandler(filters.TEXT, get_check_interval_handler)
            ],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("set_general_limit_number", get_general_limit_number),
        ],
        states={
            GET_GENERAL_LIMIT_NUMBER: [
                MessageHandler(filters.TEXT, get_general_limit_number_handler)
            ],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("remove_except_user", remove_except_user),
        ],
        states={
            REMOVE_EXCEPT_USER: [
                MessageHandler(filters.TEXT, remove_except_user_handler)
            ],
        },
        fallbacks=[],
    )
)

application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("country_code", set_country_code),
        ],
        states={
            SET_COUNTRY_CODE: [MessageHandler(filters.TEXT, write_country_code)],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("set_except_user", set_except_users),
        ],
        states={
            SET_EXCEPT_USERS: [MessageHandler(filters.TEXT, set_except_users_handler)],
        },
        fallbacks=[],
    )
)

application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("show_special_limit", show_special_limit_function),
        ],
        states={},
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("add_admin", add_admin),
        ],
        states={
            GET_CHAT_ID: [MessageHandler(filters.TEXT, get_chat_id)],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("remove_admin", remove_admin),
        ],
        states={
            GET_CHAT_ID_TO_REMOVE: [
                MessageHandler(filters.TEXT, get_chat_id_to_remove)
            ],
        },
        fallbacks=[],
    )
)
application.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler("backup", send_backup),
        ],
        states={},
        fallbacks=[],
    )
)
application.add_handler(CommandHandler("admins_list", admins_list))
application.add_handler(CommandHandler("show_except_users", show_except_users))
unknown_handler = MessageHandler(filters.TEXT, start)
application.add_handler(unknown_handler)
unknown_handler_command = MessageHandler(filters.COMMAND, start)
application.add_handler(unknown_handler_command)
