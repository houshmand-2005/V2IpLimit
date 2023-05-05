import ipaddress
import json
import re
import time
from datetime import datetime
import pytz
import requests

LOAD_CONFIG_JSON = "v2iplimit_config.json"
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
INVALID_IPS = ["1.1.1.1", "8.8.8.8"]

INACTIVE_USERS = []

try:
    with open(LOAD_CONFIG_JSON, "r") as CONFIG_FILE:
        LOAD_CONFIG_JSON = json.loads(CONFIG_FILE.read())
except Exception as ex:
    print(ex)
    print("cant find v2iplimit_config.json file ")
    exit()

WRITE_LOGS_TF = bool(LOAD_CONFIG_JSON["WRITE_LOGS_TF"])
SEND_LOGS_TO_TEL = bool(LOAD_CONFIG_JSON["SEND_LOGS_TO_TEL"])
LIMIT_NUMBER = int(LOAD_CONFIG_JSON["LIMIT_NUMBER"])
LOG_FILE_NAME = str(LOAD_CONFIG_JSON["LOG_FILE_NAME"])
TELEGRAM_BOT_URL = str(LOAD_CONFIG_JSON["TELEGRAM_BOT_URL"])
CHAT_ID = int(LOAD_CONFIG_JSON["CHAT_ID"])
EXCEPT_USERS = LOAD_CONFIG_JSON["EXCEPT_USERS"]
CONTAINER_ID = str(LOAD_CONFIG_JSON["CONTAINER_ID"])
PANEL_USERNAME = str(LOAD_CONFIG_JSON["PANEL_USERNAME"])
PANEL_PASSWORD = str(LOAD_CONFIG_JSON["PANEL_PASSWORD"])
PANEL_DOMAIN = str(LOAD_CONFIG_JSON["PANEL_DOMAIN"])
TIME_TO_CHECK = int(LOAD_CONFIG_JSON["TIME_TO_CHECK"])

if CONTAINER_ID == "auto":
    try:
        import docker  # pip install docker

        client = docker.from_env()
        containers = client.containers.list()
    except Exception:
        print("run this command: pip install docker")
        exit()
    try:
        for container in containers:
            if str(container.name) not in VAL_CONTAINER:
                print(
                    "The program could not find the container automatically."
                    + " Enter the container id manually"
                )
                exit()
            if str(container.name) in VAL_CONTAINER:
                container_id = container.id
            break
    except Exception:
        print("input your container id(full id like bellow)")
        print(
            "like this one : f33c163ga72f1590eda927024d2d862b6205655822d28e12ab10078f6bcd5d63"
        )
        container_id = input("input your container id:")
else:
    container_id = CONTAINER_ID
print(f"container id : {container_id}")
input_log_file = f"/var/lib/docker/containers/{container_id}/{container_id}-json.log"


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
    url = f"https://{PANEL_DOMAIN}/api/admin/token"
    payload = {
        "grant_type": "",
        "username": PANEL_USERNAME,
        "password": PANEL_PASSWORD,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = requests.post(url, data=payload, headers=headers)
    json_obj = json.loads(response.text)
    token = json_obj["access_token"]
    return token


def all_user():
    payload = {
        "grant_type": "",
        "username": PANEL_USERNAME,
        "password": PANEL_PASSWORD,
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
    """enable users"""
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
        response = requests.put(url, data=json.dumps(status), headers=headers)
        print(response.status_code)


def enable_user():
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
        print()
        url = f"https://{PANEL_DOMAIN}/api/user/{username}"
        status = {"status": "active"}
        response = requests.put(url, data=json.dumps(status), headers=headers)
        print(response.status_code)
        index -= 1
        send_logs_to_telegram(f"enable user : {username}")
        write_log(f"enable user : {username}")


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
    response = requests.put(url, data=json.dumps(status), headers=headers)
    print(response.status_code)
    INACTIVE_USERS.append(user_email_v2)
    send_logs_to_telegram(f"disable user : {username}")
    write_log(f"disable user : {username}")


# If there was a problem in deactivating users you can activate all users by :
# enable_all_user()


def job():
    """main function"""
    data = []
    try:
        with open(input_log_file, "r") as f:
            for line in f:
                obj = json.loads(line)
                data.append(obj)
    except Exception as ex:
        print(ex)
    final_log = []
    for log in data:
        dont_check = False
        email = ""
        ip_address = ""
        logm = log["log"]
        if "accepted" in logm:
            ip_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            ip_match = re.search(ip_pattern, logm)
            try:
                ip_address = ip_match.group(1)
            except Exception:
                dont_check = True
            try:
                email = re.search(r"email: (\S+)", logm).group(1)
            except Exception:
                dont_check = True
        if email in INVALID_EMAIL:
            dont_check = True
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            dont_check = True
        if ip_address in INVALID_IPS:
            dont_check = True
        if dont_check is False:
            final_log.append([email, ip_address])
    emails_to_ips = {}
    for d in final_log:
        email = d[0]
        ip = d[1]
        if email in emails_to_ips:
            if ip not in emails_to_ips[email]:
                emails_to_ips[email].append(ip)
        else:
            emails_to_ips[email] = [ip]
    using_now = 0
    country_time_zone = pytz.timezone("iran")  # or another country
    country_time = datetime.now(country_time_zone)
    country_time = country_time.strftime("%d-%m-%y | %H:%M:%S")
    full_report = ""
    active_users = ""
    for email, user_ip in emails_to_ips.items():
        active_users = str(email) + " " + str(user_ip)
        print(active_users)
        using_now += len(user_ip)
        full_report += "\n" + active_users
        full_log = ""
        if len(user_ip) > LIMIT_NUMBER:
            if email not in EXCEPT_USERS:
                disable_user(email)
                print("too much ip [", email, "]", " --> ", user_ip)
                full_log = f"\n{country_time}\nWarning: user {email} is associated with multiple IPs: {user_ip}"
                send_logs_to_telegram(full_log)
                log_sn = str("\n" + active_users + full_log)
                write_log(log_sn)
    full_log = f"{full_report}\n{country_time}\nall active users : [ {using_now} ]"
    write_log(full_log)
    send_logs_to_telegram(full_log)
    using_now = 0
    with open(input_log_file, "w") as f:
        f.write("")


while True:
    try:
        print("----[start scanning]----")
        job()
        print("---------[done]---------")
        time.sleep(TIME_TO_CHECK)
        enable_user()
        time.sleep(5)
    except Exception as ex:
        print(ex)
        time.sleep(10)

# |------------------------------------|
# | https://github.com/houshmand-2005/ |
# |------------------------------------|
