"""Check user usage and decide block by number of unique subnets."""

from __future__ import annotations

import asyncio
from typing import Any

from telegram_bot.send_message import send_logs
from utils.logs import logger
from utils.panel_api import disable_user
from utils.read_config import read_config
from utils.subnets import build_subnet_map, normalize_ip, should_block_user
from utils.types import PanelType, UserType

ACTIVE_USERS: dict[str, UserType] | dict = {}


def _parse_prefix(value: Any, default: int, min_value: int, max_value: int) -> int:
    """Parse integer prefix from config with safe fallback."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if parsed < min_value or parsed > max_value:
        return default
    return parsed


def _get_subnet_prefixes(config_data: dict) -> tuple[int, int]:
    """Read subnet prefixes from config, with defaults IPv4=/16, IPv6=/64."""
    ipv4_prefix = _parse_prefix(config_data.get("IPV4_SUBNET_PREFIX"), 16, 0, 32)
    ipv6_prefix = _parse_prefix(config_data.get("IPV6_SUBNET_PREFIX"), 64, 0, 128)
    return ipv4_prefix, ipv6_prefix


def _get_user_subnet_limit(config_data: dict, user_name: str) -> int:
    """Resolve subnet threshold with backward-compatible fallbacks."""
    general_subnet_limit = int(
        config_data.get("GENERAL_SUBNET_LIMIT", config_data.get("GENERAL_LIMIT", 0))
    )
    special_subnet_limit = config_data.get("SPECIAL_SUBNET_LIMIT", {})
    if user_name in special_subnet_limit:
        return int(special_subnet_limit[user_name])

    # Backward compatibility: if subnet-specific map is absent, reuse SPECIAL_LIMIT.
    special_limit = config_data.get("SPECIAL_LIMIT", {})
    if user_name in special_limit:
        return int(special_limit[user_name])

    return general_subnet_limit


def _limit_list(items: list[str], max_items: int = 10) -> str:
    """Format compact list with truncation."""
    if not items:
        return "-"
    if len(items) <= max_items:
        return ", ".join(items)
    shown = ", ".join(items[:max_items])
    return f"{shown}, ... (+{len(items) - max_items} more)"


def _canonicalize_ips(raw_ips: list[str], user_email: str) -> list[str]:
    """Convert valid IPs to canonical form and skip invalid addresses."""
    normalized: list[str] = []
    for raw_ip in raw_ips:
        try:
            normalized.append(normalize_ip(raw_ip))
        except ValueError:
            logger.warning("Invalid IP skipped for user '%s': %s", user_email, raw_ip)
    return normalized


def _build_user_stats(data: UserType, email: str, prefixes: tuple[int, int]) -> dict[str, Any]:
    """Build complete per-user stats used for reporting and blocking."""
    ipv4_prefix, ipv6_prefix = prefixes
    canonical_ips = _canonicalize_ips(data.ip, email)
    subnet_to_ips = build_subnet_map(
        canonical_ips,
        ipv4_prefix=ipv4_prefix,
        ipv6_prefix=ipv6_prefix,
    )
    ip_list = [ip for subnet_ips in subnet_to_ips.values() for ip in subnet_ips]
    return {
        "ips": ip_list,
        "subnets": list(subnet_to_ips.keys()),
        "subnet_to_ips": subnet_to_ips,
        "unique_ip_count": len(ip_list),
        "unique_subnet_count": len(subnet_to_ips),
    }


def _render_user_message(email: str, stats: dict[str, Any]) -> str:
    """Render a compact per-user report including subnet-to-IP mapping."""
    subnet_lines = [
        f"- <code>{subnet}</code> -> {_limit_list(stats['subnet_to_ips'][subnet], 4)}"
        for subnet in stats["subnets"][:8]
    ]
    if len(stats["subnets"]) > 8:
        subnet_lines.append(f"- ... (+{len(stats['subnets']) - 8} more subnets)")

    return (
        f"<code>{email}</code>\n"
        f"IPs ({stats['unique_ip_count']}): {_limit_list(stats['ips'], 10)}\n"
        f"Subnets ({stats['unique_subnet_count']}): {_limit_list(stats['subnets'], 8)}\n"
        "Subnet -> IPs:\n"
        + "\n".join(subnet_lines)
    )


async def check_ip_used(config_data: dict | None = None) -> dict[str, dict[str, Any]]:
    """Build per-user IP/subnet stats and send compact report to bot."""
    config_data = config_data or await read_config()
    prefixes = _get_subnet_prefixes(config_data)

    all_users_log = {
        email: _build_user_stats(ACTIVE_USERS[email], email, prefixes)
        for email in list(ACTIVE_USERS.keys())
    }
    all_users_log = dict(
        sorted(
            all_users_log.items(),
            key=lambda item: item[1]["unique_subnet_count"],
            reverse=True,
        )
    )

    messages = [
        _render_user_message(email, stats)
        for email, stats in all_users_log.items()
        if stats["unique_subnet_count"] > 0 or stats["unique_ip_count"] > 0
    ]

    total_ips = sum(stats["unique_ip_count"] for stats in all_users_log.values())
    total_subnets = sum(stats["unique_subnet_count"] for stats in all_users_log.values())
    messages.append(
        "---------\n"
        f"Count Of All Active IPs: <b>{total_ips}</b>\n"
        f"Count Of All Active Subnets: <b>{total_subnets}</b>"
    )
    messages.append("<code>github.com/houshmand-2005/V2IpLimit/</code>")

    chunks = ["\n\n".join(messages[i : i + 25]) for i in range(0, len(messages), 25)]
    for message in chunks:
        await send_logs(message)

    return all_users_log


async def check_users_usage(panel_data: PanelType):
    """Check active users and disable those above subnet threshold."""
    config_data = await read_config()
    all_users_log = await check_ip_used(config_data)
    except_users = config_data.get("EXCEPT_USERS", [])

    for user_name, user_stats in all_users_log.items():
        if user_name in except_users:
            continue

        threshold_subnets = _get_user_subnet_limit(config_data, user_name)
        unique_subnet_count = user_stats["unique_subnet_count"]
        if not should_block_user(unique_subnet_count, threshold_subnets):
            continue

        message = (
            f"User {user_name} has {unique_subnet_count} active subnets "
            f"(threshold={threshold_subnets}). "
            f"Subnets: {set(user_stats['subnets'])}. "
            f"IPs: {set(user_stats['ips'])}"
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
    """Run user-usage checks in configured intervals."""
    while True:
        await check_users_usage(panel_data)
        data = await read_config()
        await asyncio.sleep(int(data["CHECK_INTERVAL"]))
