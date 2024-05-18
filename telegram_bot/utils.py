"""
This module contains utility functions for reading and writing to a JSON file,
managing admin IDs, and handling special limits for users and more...
"""

import json
import os
import sys

from utils.types import PanelType

try:
    import httpx
except ImportError:
    print("Module 'httpx' is not installed use: 'pip install httpx' to install it")
    sys.exit()


async def get_token(panel_data: PanelType) -> PanelType | ValueError:
    """
    Duplicate function to handel 'circular import' error
    """
    # pylint: disable=duplicate-code
    payload = {
        "username": f"{panel_data.panel_username}",
        "password": f"{panel_data.panel_password}",
    }
    for scheme in ["https", "http"]:
        url = f"{scheme}://{panel_data.panel_domain}/api/admin/token"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload, timeout=5)
                response.raise_for_status()
            json_obj = response.json()
            panel_data.panel_token = json_obj["access_token"]
            return panel_data
        except Exception:  # pylint: disable=broad-except
            continue
    message = (
        "Failed to get token. make sure the panel is running "
        + "and the username and password are correct."
    )
    raise ValueError(message)


async def read_json_file() -> json.load:
    """
    Reads and returns the content of the config.json file.

    Returns:
        The content of the config.json file.
    """
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def write_json_file(data: dict):
    """
    Writes the given data to the config.json file.

    Args:
        data: The data to write to the file.
    """
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


async def add_admin_to_config(new_admin_id: int) -> int | None:
    """
    Adds a new admin ID to the config.json file.

    Args:
        new_admin_id: The ID of the new admin.

    Returns:
        The ID of the new admin if it was added, None otherwise.
    """
    if os.path.exists("config.json"):
        data = await read_json_file()
        admins = data.get("ADMINS", [])
        if int(new_admin_id) not in admins:
            admins.append(int(new_admin_id))
            data["ADMINS"] = admins
            await write_json_file(data)
            return new_admin_id
    else:
        data = {"ADMINS": [new_admin_id]}
        await write_json_file(data)
        return new_admin_id
    return None


async def check_admin() -> list:
    """
    Checks and returns the list of admins from the config.json file.

    Returns:
        The list of admins.
    """
    if os.path.exists("config.json"):
        data = await read_json_file()
        return data.get("ADMINS", [])


async def handel_special_limit(username: str, limit: int) -> list[int, int]:
    """
    Handles the special limit for a given username.

    Args:
        username: The username to handle the special limit for.
        limit: The limit to set.

    Returns:
        A list where the first element is a flag indicating whether the limit was set before,
        and the second element is the new limit.
    """
    set_before = 0
    if os.path.exists("config.json"):
        data = await read_json_file()
        special_limit: dict[str:int] = data.get("SPECIAL_LIMIT", {})
        if special_limit.get(username):
            set_before = 1
        special_limit[username] = limit
        data["SPECIAL_LIMIT"] = special_limit
        await write_json_file(data)
        return [set_before, special_limit[username]]
    data = {"SPECIAL_LIMIT": {username: limit}}
    await write_json_file(data)
    return [0, special_limit[username]]


async def remove_admin_from_config(admin_id: int) -> bool:
    """
    Removes an admin from the configuration.

    Args:
        admin_id (int): The ID of the admin to be removed.

    Returns:
        bool: True if the admin was successfully removed, False otherwise.
    """
    data = await read_json_file()
    admins = data.get("ADMINS", [])
    if admin_id in admins:
        admins.remove(admin_id)
        data["admins"] = admins
        await write_json_file(data)
        return True
    return False


async def add_base_information(domain: str, password: str, username: str):
    """
    Adds base information including domain, password, and username.

    Args:
        domain (str): The domain for the panel.
        password (str): The password for the panel.
        username (str): The username for the panel.

    Returns:
        None
    """
    await get_token(
        PanelType(panel_domain=domain, panel_password=password, panel_username=username)
    )
    data = {
        "PANEL_DOMAIN": domain,
        "PANEL_USERNAME": username,
        "PANEL_PASSWORD": password,
    }
    await write_json_file(data)


async def get_special_limit_list() -> list:
    """
    This function reads config file, retrieves the list of special limits,
    and returns this list in a format suitable for messaging (split into shorter messages).

    Returns:
        list
    """
    data = await read_json_file()
    special_list = data.get("SPECIAL_LIMIT", {})
    special_list = "\n".join(
        [f"{key} : {value}" for key, value in special_list.items()]
    )
    messages = special_list.split("\n")
    shorter_messages = [
        "\n".join(messages[i : i + 100]) for i in range(0, len(messages), 100)
    ]
    return shorter_messages