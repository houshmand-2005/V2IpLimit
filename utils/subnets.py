"""Utilities for IP normalization and subnet grouping."""

from __future__ import annotations

import ipaddress
from collections import OrderedDict


def normalize_ip(ip: str) -> str:
    """Return canonical string representation of an IP address."""
    return str(ipaddress.ip_address(ip))


def ip_to_subnet(ip: str, ipv4_prefix: int = 16, ipv6_prefix: int = 64) -> str:
    """Convert IP to subnet CIDR string using configurable prefixes."""
    ip_obj = ipaddress.ip_address(ip)
    prefix = ipv4_prefix if ip_obj.version == 4 else ipv6_prefix
    return str(ipaddress.ip_network(f"{ip_obj}/{prefix}", strict=False))


def unique_ips(ips: list[str]) -> list[str]:
    """Return de-duplicated canonical IPs preserving first-seen order."""
    dedup = OrderedDict()
    for ip in ips:
        dedup.setdefault(normalize_ip(ip), True)
    return list(dedup.keys())


def should_block_user(unique_subnet_count: int, threshold_subnets: int) -> bool:
    """Decision function: block if unique subnets reaches threshold."""
    return unique_subnet_count >= threshold_subnets


def build_subnet_map(
    ips: list[str], ipv4_prefix: int = 16, ipv6_prefix: int = 64
) -> dict[str, list[str]]:
    """Build mapping subnet -> list of unique canonical IPs in that subnet."""
    grouped: dict[str, list[str]] = OrderedDict()
    for ip in unique_ips(ips):
        subnet = ip_to_subnet(ip, ipv4_prefix=ipv4_prefix, ipv6_prefix=ipv6_prefix)
        grouped.setdefault(subnet, []).append(ip)
    return grouped
