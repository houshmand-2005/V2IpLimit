"""
Read config file and return data.
"""
# pylint: disable=global-statement

import json
import os
import sys
import time

CONFIG_DATA = None
LAST_READ_TIME = 0


async def read_config(
    check_required_elements=None,
) -> dict:
    """
    read and return data from a JSON file.
    """
    global CONFIG_DATA
    global LAST_READ_TIME
    config_file = "config.json"

    if not os.path.exists(config_file):
        print("Config file not found.")
        sys.exit()
    file_mod_time = os.path.getmtime(config_file)
    if CONFIG_DATA is None or file_mod_time > LAST_READ_TIME:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                CONFIG_DATA = json.load(f)
        except json.JSONDecodeError as error:
            print(
                "Error decoding the config.json file. Please check its syntax.", error
            )
            sys.exit()
        if "BOT_TOKEN" not in CONFIG_DATA:
            print("BOT_TOKEN is not set in the config.json file.")
            sys.exit()
        if "ADMINS" not in CONFIG_DATA:
            print("ADMINS is not set in the config.json file.")
            sys.exit()
        LAST_READ_TIME = time.time()
    if check_required_elements:
        required_elements = [
            "PANEL_DOMAIN",
            "PANEL_USERNAME",
            "PANEL_PASSWORD",
            "CHECK_INTERVAL",
            "TIME_TO_ACTIVE_USERS",
            "IP_LOCATION",
            "GENERAL_LIMIT",
        ]
        for element in required_elements:
            if element not in CONFIG_DATA:
                raise ValueError(
                    f"Missing required element '{element}' in the config file."
                )
    return CONFIG_DATA
