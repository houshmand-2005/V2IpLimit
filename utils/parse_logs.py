"""
This module contains functions to parse and validate logs.
"""

import ipaddress
import random
import re

from utils.check_usage import ACTIVE_USERS
from utils.types import UserType

try:
    import httpx
except ImportError:
    print("Module 'httpx' is not installed use: 'pip install httpx' to install it")

from utils.logs import logger

INVALID_EMAILS = [
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
IP_LOCATION = []
VALID_IPS = []
IP_LOCATION = "IR"

# TODO: add nodes ip and panel ip to the invalid ips
# TODO: check ip v6 to match location too!

CACHE = {}

API_ENDPOINTS = {
    "http://ip-api.com/json/": "countryCode",
    "https://ipinfo.io/": "country",
    "https://api.iplocation.net/?ip=": "country_code2",
    "https://ipapi.co/": None,
}


async def remove_id_from_username(username: str) -> str:
    """
    Remove the ID from the start of the username.
    Args:
        username (str): The username string from which to remove the ID.

    Returns:
        str: The username with the ID removed.
    """
    return re.sub(r"^\d+\.", "", username)


async def check_ip(ip_address: str) -> None | str:
    """
    Check the geographical location of an IP address.

    Get the location of the IP address.
    The result is cached to avoid unnecessary requests for the same IP address.

    Args:
        ip_address (str): The IP address to check.

    Returns:
        str: The country code of the IP address location, or None
    """
    if ip_address in CACHE:
        return CACHE[ip_address]
    endpoint, key = random.choice(list(API_ENDPOINTS.items()))
    url = endpoint + ip_address
    if "ipapi.co" in endpoint:
        url += "/country"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=2)
        info = resp.json()
        country = info.get(key) if key else resp.text
        if country:
            CACHE[ip_address] = country
        return country
    except Exception:  # pylint: disable=broad-except
        return None


async def is_valid_ip(ip: str) -> bool:
    """
    Check if a string is a valid IP address.

    This function uses the ipaddress module to try to create an IP address object from the string.

    Args:
        ip (str): The string to check.

    Returns:
        bool: True if the string is a valid IP address, False otherwise.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


IP_V6_REGEX = re.compile(r"\[([0-9a-fA-F:]+)\]:\d+\s+accepted")
IP_V4_REGEX = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
EMAIL_REGEX = re.compile(r"email:\s*([A-Za-z0-9._%+-]+)")


async def parse_logs(log: str) -> list[UserType] | list:
    """
    Asynchronously parse logs to extract and validate IP addresses and emails.

    Args:
        log (str): The log to parse.

    Returns:
        list[UserType]
    """

    lines = log.splitlines()
    for line in lines:
        if "accepted" not in line:
            continue
        if "BLOCK]" in line:
            continue
        ip_v6_match = IP_V6_REGEX.search(line)
        ip_v4_match = IP_V4_REGEX.search(line)
        email_match = EMAIL_REGEX.search(line)
        if ip_v6_match:
            ip = ip_v6_match.group(1)
        elif ip_v4_match:
            ip = ip_v4_match.group(1)
        else:
            continue
        is_valid_ip_test = await is_valid_ip(ip)
        if is_valid_ip_test:
            country = await check_ip(ip)
            if country and country == IP_LOCATION:
                VALID_IPS.append(country)
            elif country and country != IP_LOCATION:
                INVALID_IPS.append(ip)
                continue
        if email_match:
            email = email_match.group(1)
            email = await remove_id_from_username(email)
            if email in INVALID_EMAILS:
                continue
        else:
            continue

        user = ACTIVE_USERS.get(email)
        if user:
            user.ip.append(ip)
        else:
            user = ACTIVE_USERS.setdefault(
                email,
                UserType(name=email, ip=[ip]),
            )

    return ACTIVE_USERS
