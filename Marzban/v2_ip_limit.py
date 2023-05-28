import ipaddress
import json
import re
import time
from datetime import datetime
import re
from threading import Thread
import asyncio
import pytz
import websockets
import requests


VAL_CONTAINER = ["marzban-marzban-1"]
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


def read_config():
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
    global EXCEPT_USERS, PANEL_USERNAME, PANEL_PASSWORD
    global PANEL_DOMAIN, TIME_TO_CHECK, SPECIAL_LIMIT
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

    if WRITE_LOGS_TF.lower() == "false":
        WRITE_LOGS_TF = False
    else:
        WRITE_LOGS_TF = True

    if SEND_LOGS_TO_TEL.lower() == "false":
        SEND_LOGS_TO_TEL = False
    else:
        SEND_LOGS_TO_TEL = True

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
        return LIMIT_NUMBER

    return get_limit_number()


read_config()


def send_logs_to_telegram(message):
    """send logs to telegram"""
    if SEND_LOGS_TO_TEL:
        send_data = {
            "chat_id": CHAT_ID,
            "text": message,
        }
        try:
            response = requests.post(TELEGRAM_BOT_URL, data=send_data)
        except Exception:
            time.sleep(15)
            response = requests.post(TELEGRAM_BOT_URL, data=send_data)
            if response.status_code != 200:
                print("Failed to send Telegram message")


def write_log(log_info):
    """write logs"""
    if WRITE_LOGS_TF:
        with open(LOG_FILE_NAME, "a") as f:
            f.write(str(log_info))


def get_token():
    """get tokens for other apis"""
    url = f"https://{PANEL_DOMAIN}/api/admin/token"
    payload = {
        "grant_type": "",
        "username": f"{PANEL_USERNAME}",
        "password": f"{PANEL_PASSWORD}",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

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
    payload = {
        "grant_type": "",
        "username": f"{PANEL_USERNAME}",
        "password": f"{PANEL_PASSWORD}",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }
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


def save_data(data=""):
    """save user logs in list"""
    users_list_l.append(data)


def clear_data():
    """clear list of user"""
    users_list_l.clear()


async def get_logs(id=0):
    """run websocket"""
    if id != 0:
        try:
            try:
                async with websockets.connect(
                    f"wss://{PANEL_DOMAIN}/api/node/{id}/logs?token={get_token()}"
                ) as ws:
                    print(f"Establishing connection for node number {id}")
                    while True:
                        response = await ws.recv()
                        read_logs(response)
            except Exception:
                async with websockets.connect(
                    f"ws://{PANEL_DOMAIN}/api/node/{id}/logs?token={get_token()}"
                ) as ws:
                    print(f"Establishing connection for node number {id}")
                    while True:
                        response = await ws.recv()
                        read_logs(response)
        except Exception:
            message = f"Node number {id} doesn't work"
            send_logs_to_telegram(message)
            write_log("\n" + message)
            print(message)
    else:
        try:
            async with websockets.connect(
                f"wss://{PANEL_DOMAIN}/api/core/logs?token={get_token()}"
            ) as ws:
                print("Establishing connection main server")
                while True:
                    response = await ws.recv()
                    read_logs(response)
        except Exception:
            async with websockets.connect(
                f"ws://{PANEL_DOMAIN}/api/core/logs?token={get_token()}"
            ) as ws:
                print("Establishing connection main server")
                while True:
                    response = await ws.recv()
                    read_logs(response)


def get_nodes():
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

        email_m = re.search(r"email:\s*([A-Za-z0-9._%+-]+)", log)
        if email_m:
            email = email_m.group(1)
            email = re.search(r"\.(.*)", email).group(1)
            if email in INVALID_EMAIL:
                dont_check = True
        else:
            dont_check = True

        if dont_check is False:
            save_data([email, ip_address])


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
    useing_now = 0
    country_time_zone = pytz.timezone("iran")  # or another country
    country_time = datetime.now(country_time_zone)
    country_time = country_time.strftime("%d-%m-%y | %H:%M:%S")
    full_report = ""
    active_users = ""
    for email, user_ip in emails_to_ips.items():
        active_users = str(email) + " " + str(user_ip)
        useing_now += len(user_ip)
        full_report += "\n" + active_users
        full_log = ""
        LIMIT_NUMBER = int(read_config())
        if email in SPECIAL_LIMIT_USERS:
            print("special limit -->", SPECIAL_LIMIT, email)
            LIMIT_NUMBER = int(SPECIAL_LIMIT[email])
        if len(user_ip) > LIMIT_NUMBER:
            if email not in EXCEPT_USERS:
                disable_user(email)
                print("too much ip [", email, "]", " --> ", user_ip)
                full_log = f"\n{country_time}\nWarning: user {email} is associated with multiple IPs: {user_ip}"
                send_logs_to_telegram(full_log)
                log_sn = str("\n" + active_users + full_log)
                write_log(log_sn)
        print("--------------------------------")
        print(email, user_ip, "Number of active IPs -->", len(user_ip))
    full_log = (
        f"{full_report}\n{country_time}\nall active users(IPs) : [ {useing_now} ]"
    )
    if useing_now != 0:
        write_log(full_log)
        print(
            f"--------------------------------\n{country_time}"
            + f"\nall active users(IPs) : [ {useing_now} ]"
        )
    useing_now = 0
    clear_data()


def enable_user_th():
    """run enable user func"""
    while True:
        time.sleep(int(TIME_TO_CHECK + TIME_TO_CHECK))
        enable_user()
        read_config()


try:
    get_token()
except Exception:
    print(
        "Wrong url or ip address"
        + "\nplease check your value in v2iplimit_config.json file"
    )
    exit()
Thread(target=get_logs_run).start()
NODES = get_nodes()
threads = []
if NODES:
    for node in NODES:
        Thread(target=get_logs_run, args=(int(node),)).start()
        time.sleep(0.5)
time.sleep(1)
Thread(target=enable_user_th).start()

while True:
    try:
        job()
        time.sleep(int(TIME_TO_CHECK + 3))
    except Exception as ex:
        send_logs_to_telegram(ex)
        write_log("\n" + str(ex))
        print(ex)
        time.sleep(10)

# |------------------------------------|
# | https://github.com/houshmand-2005/ |
# |------------------------------------|
