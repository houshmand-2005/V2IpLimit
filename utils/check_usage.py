"""
This module checks if a user (name and IP address)
appears more than two times in the ACTIVE_USERS list.
It also handles CDN scenarios by grouping IPs from the same subnet
and counting each subnet as a single connection.
"""

import asyncio
import ipaddress
from collections import Counter

from telegram_bot.send_message import send_logs
from utils.logs import logger
from utils.panel_api import disable_user
from utils.read_config import read_config
from utils.types import PanelType, UserType

ACTIVE_USERS: dict[str, UserType] | dict = {}


def group_ips_by_subnet(ip_list: list[str]) -> list[str]:
    """
    Group IPs by their /24 subnet and return unique subnets.
    This helps handle CDN scenarios where multiple IPs come from the same subnet.
    
    Args:
        ip_list (list[str]): List of IP addresses
        
    Returns:
        list[str]: List of unique subnet representations (e.g., "140.248.74.x")
    """
    subnet_groups = {}
    
    for ip in ip_list:
        try:
            # Parse the IP address
            ip_obj = ipaddress.ip_address(ip)
            
            # For IPv4, group by /24 subnet (first 3 octets)
            if ip_obj.version == 4:
                # Get the network address for /24 subnet
                network = ipaddress.ip_network(f"{ip}/24", strict=False)
                subnet_key = f"{network.network_address.exploded.rsplit('.', 1)[0]}.x"
            else:
                # For IPv6, use the full IP as is (less common for CDN scenarios)
                subnet_key = str(ip_obj)
            
            if subnet_key not in subnet_groups:
                subnet_groups[subnet_key] = []
            subnet_groups[subnet_key].append(ip)
            
        except ValueError:
            # If IP parsing fails, treat as individual IP
            subnet_key = ip
            if subnet_key not in subnet_groups:
                subnet_groups[subnet_key] = []
            subnet_groups[subnet_key].append(ip)
    
    # Return the subnet representations
    return list(subnet_groups.keys())


async def check_ip_used() -> dict:
    """
    This function checks if a user (name and IP address)
    appears more than two times in the ACTIVE_USERS list.
    It also groups IPs by subnet to handle CDN scenarios where
    multiple IPs come from the same network range.
    """
    all_users_log = {}
    for email in list(ACTIVE_USERS.keys()):
        data = ACTIVE_USERS[email]
        ip_counts = Counter(data.ip)
        data.ip = list({ip for ip in data.ip if ip_counts[ip] > 2})
        
        # Group IPs by subnet to handle CDN scenarios
        subnet_ips = group_ips_by_subnet(data.ip)
        all_users_log[email] = subnet_ips
        logger.info(data)
    
    total_ips = sum(len(ips) for ips in all_users_log.values())
    all_users_log = dict(
        sorted(
            all_users_log.items(),
            key=lambda x: len(x[1]),
            reverse=True,
        )
    )
    messages = [
        f"<code>{email}</code> with <code>{len(ips)}</code> active ip  \n- "
        + "\n- ".join(ips)
        for email, ips in all_users_log.items()
        if ips
    ]
    logger.info("Number of all active ips: %s", str(total_ips))
    messages.append(f"---------\nCount Of All Active IPs: <b>{total_ips}</b>")
    messages.append("<code>github.com/houshmand-2005/V2IpLimit/</code>")
    shorter_messages = [
        "\n".join(messages[i : i + 100]) for i in range(0, len(messages), 100)
    ]
    for message in shorter_messages:
        await send_logs(message)
    return all_users_log


async def check_users_usage(panel_data: PanelType):
    """
    checks the usage of active users.
    Limits are now applied to subnet counts rather than individual IP counts
    to handle CDN scenarios properly.
    """
    config_data = await read_config()
    all_users_log = await check_ip_used()
    except_users = config_data.get("EXCEPT_USERS", [])
    special_limit = config_data.get("SPECIAL_LIMIT", {})
    limit_number = config_data["GENERAL_LIMIT"]
    for user_name, user_ip in all_users_log.items():
        if user_name not in except_users:
            user_limit_number = int(special_limit.get(user_name, limit_number))
            # user_ip now contains subnet representations, so len() gives us subnet count
            if len(set(user_ip)) > user_limit_number:
                message = (
                    f"User {user_name} has {str(len(set(user_ip)))}"
                    + f" active ips. {str(set(user_ip))}"
                )
                logger.warning(message)
                await send_logs(str("<b>Warning: </b>" + message))
                try:
                    await disable_user(panel_data, UserType(name=user_name, ip=[]))
                except ValueError as error:
                    print(error)
    ACTIVE_USERS.clear()
    all_users_log.clear()


async def run_check_users_usage(panel_data: PanelType) -> None:
    """run check_ip_used() function and then run check_users_usage()"""
    while True:
        await check_users_usage(panel_data)
        data = await read_config()
        await asyncio.sleep(int(data["CHECK_INTERVAL"]))
