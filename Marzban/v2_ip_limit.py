import ipaddress
import json
import re
import time
from datetime import datetime
import datetime as dt
from threading import Thread
import asyncio
import pytz
import websockets
import requests

INVALID_EMAIL = [
    "API]",
    "Found",
    "(normal)",
    "timeout",
    "EOF",
    "address",
    "INFO",
    "request",
]
INVALID_IPS = ["1.1.1.1", "8.8.8.8", "0.0.0.0"]
INACTIVE_USERS = []
VALID_IPS = []
IP_LOCATION = "Iran"
DATE_TIME_ZONE = "Iran"


def read_config():
    """read the v2iplimit_config.json file"""
    LOAD_CONFIG_JSON = "v2iplimit_config.json"
    try:
        with open(LOAD_CONFIG_JSON, "r") as CONFIG_FILE:
            LOAD_CONFIG_JSON = json.loads(CONFIG_FILE.read())
    except Exception as ex:
        print(ex)
        print("cant find v2iplimit_config.json file ")
        exit()
    global WRITE_LOGS_TF, SEND_LOGS_TO_TEL, LIMIT_NUMBER
    global LOG_FILE_NAME, TELEGRAM_BOT_URL, CHAT_ID, SPECIAL_LIMIT_USERS
    global EXCEPT_USERS, PANEL_USERNAME, PANEL_PASSWORD, PRETTY_PRINT
    global PANEL_DOMAIN, TIME_TO_CHECK, SPECIAL_LIMIT, SERVER_NAME
    WRITE_LOGS_TF = str(LOAD_CONFIG_JSON["WRITE_LOGS_TF"])
    SEND_LOGS_TO_TEL = str(LOAD_CONFIG_JSON["SEND_LOGS_TO_TEL"])
    LIMIT_NUMBER = int(LOAD_CONFIG_JSON["LIMIT_NUMBER"])
    LOG_FILE_NAME = str(LOAD_CONFIG_JSON["LOG_FILE_NAME"])
    TELEGRAM_BOT_URL = str(LOAD_CONFIG_JSON["TELEGRAM_BOT_URL"])
    CHAT_ID = int(LOAD_CONFIG_JSON["CHAT_ID"])
    EXCEPT_USERS = LOAD_CONFIG_JSON["EXCEPT_USERS"]
    PANEL_USERNAME = str(LOAD_CONFIG_JSON["PANEL_USERNAME"])
    PANEL_PASSWORD = str(LOAD_CONFIG_JSON["PANEL_PASSWORD"])
    PANEL_DOMAIN = str(LOAD_CONFIG_JSON["PANEL_DOMAIN"])
    TIME_TO_CHECK = int(LOAD_CONFIG_JSON["TIME_TO_CHECK"])
    SPECIAL_LIMIT = LOAD_CONFIG_JSON["SPECIAL_LIMIT"]
    try:
        SERVER_NAME = str(LOAD_CONFIG_JSON["SERVER_NAME"])
    except KeyError:
        SERVER_NAME = False
    try:
        PRETTY_PRINT = str(LOAD_CONFIG_JSON["PRETTY_PRINT"])
        PRETTY_PRINT = PRETTY_PRINT.lower() == "true"
    except KeyError:
        PRETTY_PRINT = False
    WRITE_LOGS_TF = WRITE_LOGS_TF.lower() == "true"
    SEND_LOGS_TO_TEL = SEND_LOGS_TO_TEL.lower() == "true"
    (SPECIAL_LIMIT_USERS), (SPECIAL_LIMIT_IP) = list(
        user[0] for user in SPECIAL_LIMIT
    ), list(user[1] for user in SPECIAL_LIMIT)
    SPECIAL_LIMIT = {}
    for key in SPECIAL_LIMIT_USERS:
        for value in SPECIAL_LIMIT_IP:
            SPECIAL_LIMIT[key] = value
            SPECIAL_LIMIT_IP.remove(value)
            break

    def get_limit_number():
        """get limit number from json file"""
        return LIMIT_NUMBER

    return get_limit_number()


read_config()


def send_logs_to_telegram(message):
    """send logs to telegram"""
    if SEND_LOGS_TO_TEL:
        if PRETTY_PRINT:
            messages = message.split("\n")
            shorter_messages = [
                "\n".join(messages[i : i + 100]) for i in range(0, len(messages), 100)
            ]
        else:
            messages = message.split("]")
            shorter_messages = [
                "]".join(messages[i : i + 100]) for i in range(0, len(messages), 100)
            ]
        for message in shorter_messages:
            txt_s = str(message.strip())
            if SERVER_NAME:
                txt_s = str("<b>" + SERVER_NAME + "</b>\n-------\n" + str(txt_s))
            send_data = {
                "chat_id": CHAT_ID,
                "text": txt_s,
                "parse_mode": "HTML",
            }
            try:
                response = requests.post(TELEGRAM_BOT_URL, data=send_data)
            except Exception as ex:
                print(ex)
                time.sleep(15)
                response = requests.post(TELEGRAM_BOT_URL, data=send_data)
                if response.status_code != 200:
                    print("Failed to send Telegram message")


def write_log(log_info):
    """write logs"""
    if WRITE_LOGS_TF:
        with open(LOG_FILE_NAME, "a") as f:
            f.write(str(log_info))


def telegram_log_parser(users_list):
    """make the telegram logs ready"""
    active_users_t = ""
    if users_list:
        sorted_data = sorted(users_list, key=lambda x: x[1], reverse=True)
        for email, user_ip_l, user_ip in sorted_data:
            if PRETTY_PRINT:
                user_ip = ["- " + ip for ip in user_ip]
                user_ip = "\n".join([""] + list(user_ip))
            active_users_t += (
                f"\n {str(email)} <b>[ {str(user_ip_l)} ] IPs : </b> {str(user_ip)} "
            )
        return active_users_t


def get_token():
    """get tokens for other apis"""
    url = f"https://{PANEL_DOMAIN}/api/admin/token"
    payload = {"username": f"{PANEL_USERNAME}", "password": f"{PANEL_PASSWORD}"}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
    except Exception:
        url = url.replace("https://", "http://")
        response = requests.post(url, data=payload, headers=headers)
    json_obj = json.loads(response.text)
    token = json_obj["access_token"]
    return token


def all_user():
    """get the list of all users"""
    payload = {"username": f"{PANEL_USERNAME}", "password": f"{PANEL_PASSWORD}"}
    token = get_token()
    header_value = "Bearer "
    headers = {
        "Accept": "application/json",
        "Authorization": header_value + token,
        "Content-Type": "application/json",
    }
    url = f"https://{PANEL_DOMAIN}/api/users/"
    try:
        response = requests.get(url, data=payload, headers=headers)
    except Exception:
        url = url.replace("https://", "http://")
        response = requests.get(url, data=payload, headers=headers)
    user_inform = json.loads(response.text)
    index = 0
    All_users = []
    try:
        while True:
            All_users.append((user_inform["users"])[index]["username"])
            index += 1
    except Exception:
        pass
    return All_users


def enable_all_user():
    """enable all users"""
    token = get_token()
    header_value = "Bearer "
    headers = {
        "Accept": "application/json",
        "Authorization": header_value + token,
        "Content-Type": "application/json",
    }
    for username in all_user():
        url = f"https://{PANEL_DOMAIN}/api/user/{username}"
        status = {"status": "active"}
        try:
            requests.put(url, data=json.dumps(status), headers=headers)
        except Exception:
            url = url.replace("https://", "http://")
            requests.put(url, data=json.dumps(status), headers=headers)
    print("enable all users")


def enable_user():
    """enable users"""
    token = get_token()
    header_value = "Bearer "
    headers = {
        "Accept": "application/json",
        "Authorization": header_value + token,
        "Content-Type": "application/json",
    }
    index = len(INACTIVE_USERS)
    while index != 0:
        username = INACTIVE_USERS.pop(index - 1)
        url = f"https://{PANEL_DOMAIN}/api/user/{username}"
        status = {"status": "active"}
        try:
            requests.put(url, data=json.dumps(status), headers=headers)
        except Exception:
            url = url.replace("https://", "http://")
            requests.put(url, data=json.dumps(status), headers=headers)
        index -= 1
        message = f"\nenable user : {username}"
        send_logs_to_telegram(message)
        write_log(message)
        print(message)


def disable_user(user_email_v2):
    """disable users"""
    token = get_token()
    username = str(user_email_v2)
    header_value = "Bearer "
    headers = {
        "Accept": "application/json",
        "Authorization": header_value + token,
        "Content-Type": "application/json",
    }

    url = f"https://{PANEL_DOMAIN}/api/user/{username}"
    status = {"status": "disabled"}
    try:
        requests.put(url, data=json.dumps(status), headers=headers)
    except Exception:
        url = url.replace("https://", "http://")
        requests.put(url, data=json.dumps(status), headers=headers)
    INACTIVE_USERS.append(user_email_v2)
    message = f"\ndisable user : {username}"
    send_logs_to_telegram(message)
    write_log(message)
    print(message)


# If there was a problem in deactivating users you can activate all users by :
# enable_all_user()

users_list_l = []
last_usage_d = {}


def last_usage(user, last_time):
    """latest active time per user"""
    last_usage_d[str(user)] = str(last_time)


def save_data(data=""):
    """save user logs in list"""
    users_list_l.append(data)


def clear_data():
    """clear list of user"""
    users_list_l.clear()


async def get_logs(id=0):
    """run websocket"""
    if id != 0:
        while True:
            try:
                try:
                    async with websockets.connect(
                        f"wss://{PANEL_DOMAIN}/api/node/{id}/logs?token={get_token()}"
                    ) as ws:
                        message = f"Establishing connection for node number {id}"
                        send_logs_to_telegram(message)
                        print(message)
                        while True:
                            new_log = await ws.recv()
                            lines = new_log.split("\n")
                            for line in lines:
                                read_logs(line)
                except Exception:
                    async with websockets.connect(
                        f"ws://{PANEL_DOMAIN}/api/node/{id}/logs?token={get_token()}"
                    ) as ws:
                        message = f"Establishing connection for node number {id}"
                        send_logs_to_telegram(message)
                        print(message)
                        while True:
                            new_log = await ws.recv()
                            lines = new_log.split("\n")
                            for line in lines:
                                read_logs(line)
            except Exception as ex:
                print(ex)
                message = f"Node number {id} doesn't work"
                send_logs_to_telegram(message)
                write_log("\n" + message)
                print(message)
                await asyncio.sleep(20)
    else:
        while True:
            try:
                try:
                    async with websockets.connect(
                        f"wss://{PANEL_DOMAIN}/api/core/logs?token={get_token()}"
                    ) as ws:
                        message = "Establishing connection main server"
                        send_logs_to_telegram(message)
                        print(message)
                        while True:
                            response = await ws.recv()
                            read_logs(response)
                except Exception:
                    async with websockets.connect(
                        f"ws://{PANEL_DOMAIN}/api/core/logs?token={get_token()}"
                    ) as ws:
                        message = "Establishing connection main server"
                        send_logs_to_telegram(message)
                        print(message)
                        while True:
                            response = await ws.recv()
                            read_logs(response)
            except Exception as ex:
                print(ex)
                message = "main server doesn't work"
                send_logs_to_telegram(message)
                write_log("\n" + message)
                print(message)
                await asyncio.sleep(25)


def get_nodes():
    """get id of nodes"""
    token = get_token()
    header_value = "Bearer "
    headers = {
        "Accept": "application/json",
        "Authorization": header_value + token,
        "Content-Type": "application/json",
    }
    url = f"https://{PANEL_DOMAIN}/api/nodes"
    try:
        response = requests.get(url, headers=headers)
    except Exception:
        url = url.replace("https://", "http://")
        response = requests.get(url, headers=headers)
    user_inform = json.loads(response.text)
    index = 0
    All_nodes = []
    try:
        while True:
            All_nodes.append(user_inform[index]["id"])
            index += 1
    except Exception:
        pass
    return All_nodes


def get_logs_run(id=0):
    """run websocket func"""
    asyncio.run(get_logs(id))


def check_ip(i_ip_address):
    """check IP location"""
    ip_address = str(i_ip_address)
    params = ["country"]
    try:
        resp = requests.get(
            "http://ip-api.com/json/" + ip_address, params={"fields": ",".join(params)}
        )
        info = resp.json()
        result = info["country"]
    except Exception:
        result = "unknownip2"
    return result


def read_logs(log=""):
    """read all logs and extract data from it"""
    acceptance_match = re.search(r"\baccepted\b", log)
    if acceptance_match:
        dont_check = False
    else:
        dont_check = True
    if dont_check is False:
        ip_address = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", log)
        if ip_address:
            ip_address = ip_address.group(1)
            try:
                ipaddress.ip_address(ip_address)
            except ValueError:
                dont_check = True
            if ip_address in INVALID_IPS:
                dont_check = True
        else:
            dont_check = True
        if dont_check is False:
            email_m = re.search(r"email:\s*([A-Za-z0-9._%+-]+)", log)
            if email_m:
                email = email_m.group(1)
                email = re.search(r"\.(.*)", email).group(1)
                if email in INVALID_EMAIL:
                    dont_check = True
            else:
                dont_check = True
        if dont_check is False:
            if ip_address in VALID_IPS:
                pass
            else:
                loc = check_ip(ip_address)
                if loc != IP_LOCATION:
                    if loc != "unknownip2":
                        INVALID_IPS.append(ip_address)
                        dont_check = True
                    else:
                        VALID_IPS.append(ip_address)
                else:
                    VALID_IPS.append(ip_address)
        if dont_check is False:
            use_time = log.split(" ")
            time_l = use_time[1]
            time_object = datetime.strptime(time_l, "%H:%M:%S").time()
            utc_timezone = pytz.timezone("UTC")
            utc_time = datetime.combine(dt.date.today(), time_object)
            utc_time = utc_timezone.localize(utc_time)
            iran_timezone = pytz.timezone(DATE_TIME_ZONE)  # Convert to your timezone
            iran_time = utc_time.astimezone(iran_timezone)
            use_time = use_time[0] + " | " + str(iran_time.time())
        if dont_check is False:
            save_data([email, ip_address])
            last_usage(email, use_time)


def job():
    """main function"""
    emails_to_ips = {}
    for d in users_list_l:
        email = d[0]
        ip = d[1]
        if email in emails_to_ips:
            if ip not in emails_to_ips[email]:
                emails_to_ips[email].append(ip)
        else:
            emails_to_ips[email] = [ip]
    using_now = 0
    country_time_zone = pytz.timezone(DATE_TIME_ZONE)  # your date zone
    country_time = datetime.now(country_time_zone)
    country_time = country_time.strftime("%d-%m-%y | %H:%M:%S")
    full_report = ""
    full_report_t = ""
    active_users = ""
    active_users_tl = []
    for email, user_ip in emails_to_ips.items():
        active_users = str(email) + " [ " + str(len(user_ip)) + " IPs ]" + str(user_ip)
        active_users_tl.append([email, len(user_ip), user_ip])
        using_now += len(user_ip)
        full_report += "\n" + active_users
        full_log = ""
        full_log_t = ""
        LIMIT_NUMBER = int(read_config())
        if email in SPECIAL_LIMIT_USERS:
            LIMIT_NUMBER = int(SPECIAL_LIMIT[email])
        if len(user_ip) > LIMIT_NUMBER:
            if email not in EXCEPT_USERS:
                disable_user(email)
                print("too much ip [", email, "]", " --> ", user_ip)
                full_log = f"\n{country_time}\nWarning: user {email} is associated with {len(user_ip)} IPs: {user_ip}"
                send_logs_to_telegram(full_log)
                log_sn = str("\n" + active_users + full_log)
                write_log(log_sn)
        print("--------------------------------")
        print(email, user_ip, "Number of active IPs -->", len(user_ip))
    full_log = f"{full_report}\n{country_time}\nall active users(IPs) : [ {using_now} ]"
    full_report_t = telegram_log_parser(active_users_tl)
    full_log_t = f"{full_report_t}\n-------\n{country_time}\n<b>all active users(IPs) : [ {using_now} ]</b>"
    if using_now != 0:
        write_log(full_log)
        send_logs_to_telegram(full_log_t)
        print(
            f"--------------------------------\n{country_time}"
            + f"\nall active users(IPs) : [ {using_now} ]"
        )
    else:
        print("There is no active user")
    using_now = 0
    clear_data()


def delete_valid_list():
    """delete the cache of valid ips"""
    while True:
        time.sleep(11000)
        print("delete valid list and recreate it")
        VALID_IPS.clear()


def enable_user_th():
    """run enable user func"""
    while True:
        time.sleep(int(TIME_TO_CHECK + TIME_TO_CHECK))
        enable_user()
        read_config()


def get_updates(offset=None):
    """get updates form telegram"""
    BASE_URL = TELEGRAM_BOT_URL.rstrip("/sendMessage") + "/"
    url = BASE_URL + "getUpdates"
    params = {"offset": offset, "timeout": 30}
    response = requests.get(url, params=params)
    data = response.json()
    return data["result"]


def user_command(user):
    """get the latest usage of user"""
    if last_usage_d.get(user):
        send_logs_to_telegram(str(user) + " : " + str(last_usage_d.get(user)))
    else:
        send_logs_to_telegram("User not found")


def handle_updates(updates):
    """handle commands"""
    for update in updates:
        if "message" in update:
            message = update["message"]
            text = message.get("text")
            if text:
                lower_text = text.lower()
                if lower_text.startswith("/usagetime"):
                    parts = text.split(" ")
                    if len(parts) > 1:
                        username = parts[1]
                        user_command(username)
                if lower_text.startswith("/programmer"):
                    send_logs_to_telegram(
                        "<code>Houshmand</code>\n<a>github.com/houshmand-2005/V2IpLimit/</a>"
                    )


def telegram_updater():
    """telegram bot"""
    offset = None
    if SEND_LOGS_TO_TEL:
        while True:
            try:
                updates = get_updates(offset)
                if updates:
                    handle_updates(updates)
                    offset = updates[-1]["update_id"] + 1
            except Exception as ex:
                print(ex)
                time.sleep(1)
    else:
        time.sleep(20)


try:
    get_token()
except Exception:
    print(
        "Wrong url or ip address"
        + "\nplease check your value in v2iplimit_config.json file"
    )
    exit()
Thread(target=get_logs_run).start()
time.sleep(1)
NODES = get_nodes()
threads = []
if NODES:
    for node in NODES:
        Thread(target=get_logs_run, args=(int(node),)).start()
        time.sleep(2)

time.sleep(10)
print("in progress ...")
time.sleep(10)
Thread(target=telegram_updater).start()
Thread(target=enable_user_th).start()
Thread(target=delete_valid_list).start()

while True:
    try:
        print("-----run------")
        job()
        print("-----done-----")
        time.sleep(int(TIME_TO_CHECK + 3))
    except Exception as ex:
        send_logs_to_telegram(ex)
        write_log("\n" + str(ex))
        print(ex)
        time.sleep(10)

# |------------------------------------|
# | https://github.com/houshmand-2005/ |
# |------------------------------------|
