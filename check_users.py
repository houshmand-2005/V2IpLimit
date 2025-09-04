import requests
import time
import json
from collections import defaultdict
import os

CONFIG_PATH = "/root/V2IpLimit/config.json"
BACKUP_PATH = "/root/config.json" 
DB_PATH = "/root/V2IpLimit/SPECIAL_LIMIT_DB.json" 
# دامنه های دریافت شده از ربات میزا
URLS = [
    "https://********/.php",
    "https://********/.php",
    "https://********/.php"
]

def load_json_file(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json_file(path, data):
    try:
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving {path}: {e}")

def fetch_data():
    config = load_json_file(CONFIG_PATH)
    db_data = load_json_file(DB_PATH)

    special_limit = config.get("SPECIAL_LIMIT", {})

    new_entries = 0

    for url in URLS:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            for entry in data:
                username = entry.get("username", "Unknown")
                limit = entry.get("limit", 0)

                if username not in special_limit and limit != 1:
                    special_limit[username] = limit

               
                if username not in db_data and limit != 1:
                    db_data[username] = limit
                    new_entries += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")

    config["SPECIAL_LIMIT"] = special_limit
    save_json_file(CONFIG_PATH, config)
    save_json_file(BACKUP_PATH, config)
    save_json_file(DB_PATH, db_data)

    print(json.dumps(special_limit, indent=4))
    if new_entries:
        print(f"{new_entries} new entries added to {DB_PATH}")

if __name__ == "__main__":
    while True:
        fetch_data()
        time.sleep(300) 