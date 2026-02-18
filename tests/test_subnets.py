"""Tests for subnet utility helpers."""

import unittest

from utils.subnets import build_subnet_map, ip_to_subnet, normalize_ip, unique_ips


class TestSubnetUtils(unittest.TestCase):
    """Validate IP normalization and subnet grouping behavior."""

    def test_ip_to_subnet_ipv4_default_24(self):
        """IPv4 addresses are mapped to /24 by default."""
        self.assertEqual(ip_to_subnet("10.0.1.2"), "10.0.1.0/24")

    def test_ip_to_subnet_ipv6_default_64(self):
        """IPv6 addresses are mapped to /64 by default."""
        self.assertEqual(
            ip_to_subnet("2a01:5ec0:5011:9962:d8ed:c723:c32:ac2a"),
            "2a01:5ec0:5011:9962::/64",
        )

    def test_ip_to_subnet_custom_prefixes(self):
        """Configured prefixes override defaults for v4 and v6."""
        self.assertEqual(ip_to_subnet("10.0.1.2", ipv4_prefix=20), "10.0.0.0/20")
        self.assertEqual(
            ip_to_subnet("2001:db8:abcd:1234::1", ipv6_prefix=56),
            "2001:db8:abcd:1200::/56",
        )

    def test_normalize_ip(self):
        """IPv6 representation is converted to canonical form."""
        self.assertEqual(normalize_ip("2001:0db8::1"), "2001:db8::1")

    def test_unique_ips_dedup(self):
        """Duplicate IPs are removed while preserving first-seen order."""
        ips = ["10.0.1.2", "10.0.1.2", "2001:0db8::1"]
        self.assertEqual(unique_ips(ips), ["10.0.1.2", "2001:db8::1"])

    def test_build_subnet_map_mixed(self):
        """Mixed IPv4/IPv6 addresses are grouped into expected subnets."""
        ips = [
            "10.0.1.2",
            "10.0.1.3",
            "10.0.2.9",
            "2001:db8:abcd:1234::1",
            "2001:db8:abcd:1234::2",
            "2001:db8:abcd:5678::1",
        ]
        subnet_map = build_subnet_map(ips)
        self.assertEqual(len(subnet_map), 4)
        self.assertIn("10.0.1.0/24", subnet_map)
        self.assertIn("10.0.2.0/24", subnet_map)
        self.assertIn("2001:db8:abcd:1234::/64", subnet_map)
        self.assertIn("2001:db8:abcd:5678::/64", subnet_map)


if __name__ == "__main__":
    unittest.main()
