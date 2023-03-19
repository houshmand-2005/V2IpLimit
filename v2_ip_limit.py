import subprocess
import ipaddress
import json
import re
import time
import os
from datetime import datetime
import uuid
import pytz
import requests

# if you have problem just run this python app with sudo
WRITE_LOGS_TF = True
SEND_LOGS_TO_TEL = False
LIMIT_NUMBER = 2
EN_DIS_USERS = "en_dis_users.json"
LOG_FILE_NAME = "ip_email.log"
CONFIG_FILE = "config.json"  # you must have this file
TELEGRAM_BOT_URL = "https://api.telegram.org/bot[add_your_bot_token_here]/sendMessage"
CHAT_ID = 111111111  # get from here --> @RawDataBot
EXCEPT_EMAIL = ["client@example.com"]  # they dont disable


try:
    import docker

    client = docker.from_env()
except Exception:
    print("run this command: pip install docker")
    exit()
containers = client.containers.list()
try:
    for container in containers:
        container_id = container.id  # get the first container
        break
except Exception:
    print("input your container id(full id like bellow)")
    print(
        "like this one : f33c163ea72f1590eda927024d2d862b6005685822d28e12ab17778f6bcd5d63"
    )
    container_id = input("input your container id:")
input_log_file = f"/var/lib/docker/containers/{container_id}/{container_id}-json.log"
with open(CONFIG_FILE, "r") as CONFIG_FILE:
    json_CONFIG_FILE = json.loads(CONFIG_FILE.read())
list_of_clients = json_CONFIG_FILE["inbounds"][0]["settings"]["clients"]


def dump_user_json(json_data):
    with open(EN_DIS_USERS, "w") as file:
        json.dump(json_data, file, indent=2)


def read_user_json():
    with open(EN_DIS_USERS, "r") as CONFIG_FILE:
        return json.loads(CONFIG_FILE.read())


def save_config(data):
    """save json config"""
    with open("config.json", "w") as file:
        json.dump(data, file, indent=2)
    reset_docker_compose()


def reset_docker_compose():
    """reset docker to apply the changes"""
    subprocess.run(
        "docker-compose restart",
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def enable_user():
    """enable users"""
    index = 0
    for client in list_of_clients:
        try:
            user_json = read_user_json()
        except Exception:
            break
        for item in user_json:
            if client["email"] == user_json[item]["email"]:
                json_CONFIG_FILE["inbounds"][0]["settings"]["clients"][index][
                    "id"
                ] = user_json[item]["id"]
                em_cl = client["email"]
                msg_log = f"\nenable user : {em_cl}"
                print(msg_log)
                write_log(msg_log)
                send_logs_to_telegram(msg_log)
                os.remove(EN_DIS_USERS)
                save_config(json_CONFIG_FILE)
            index += 1


def disable_user(user_email_v2):
    """disable users"""
    index = 0
    for client in list_of_clients:
        if user_email_v2 == client["email"]:
            number_cn = 0
            try:
                user_json = read_user_json()
                number_cn = 0
                for _ in user_json:
                    number_cn += 1
            except Exception:
                pass

            data = {
                number_cn: {
                    "id": json_CONFIG_FILE["inbounds"][0]["settings"]["clients"][index][
                        "id"
                    ],
                    "email": client["email"],
                },
            }
            dump_user_json(data)

            json_CONFIG_FILE["inbounds"][0]["settings"]["clients"][index]["id"] = str(
                uuid.uuid4()
            )
            em_cl = client["email"]
            msg_log = f"\ndisable user : {em_cl}"
            print(msg_log)
            write_log(msg_log)
            send_logs_to_telegram(msg_log)
            save_config(json_CONFIG_FILE)
        index += 1


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


def email_val(email):
    """check if email address is valid or not"""
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    if re.fullmatch(regex, email):
        return True
    return False


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
        time_d = log["time"]
        ip_address = log["log"].split()[2].split(":")[0]
        email = log["log"].split()[-1]
        dont_check = False
        if email_val(email) is False:
            dont_check = True
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            dont_check = True
        if dont_check is False:
            final_log.append([email, ip_address, time_d])
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
            if email not in EXCEPT_EMAIL:
                disable_user(email)
                print("too much ip [", email, "]", " --> ", user_ip)
                full_log = f"\n{country_time}\nWarning: email {email} is associated with multiple IPs: {user_ip}"
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
        time.sleep(360)
        enable_user()
        time.sleep(10)
    except Exception as ex:
        print(ex)
        time.sleep(15)

# |------------------------------------|
# | https://github.com/houshmand-2005/ |
# |------------------------------------|
