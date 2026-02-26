"""Tests for subnet-based blocking decisions."""

import unittest

from utils.subnets import build_subnet_map, should_block_user


class TestBlockingLogic(unittest.TestCase):
    """Ensure blocking decisions are based on unique subnet count."""

    def test_many_ips_same_subnet_counts_as_one(self):
        """Multiple IPs in one subnet should count as a single subnet."""
        ips = ["10.0.1.2", "10.0.1.3", "10.0.1.250", "10.0.1.2"]
        subnet_map = build_subnet_map(ips, ipv4_prefix=24)
        unique_subnets = len(subnet_map)

        self.assertEqual(unique_subnets, 1)
        self.assertFalse(should_block_user(unique_subnets, threshold_subnets=2))

    def test_different_subnets_count_separately(self):
        """Distinct /16 subnets should be counted independently."""
        ips = ["10.0.1.2", "10.1.2.9", "10.2.3.7"]
        subnet_map = build_subnet_map(ips)
        unique_subnets = len(subnet_map)

        self.assertEqual(unique_subnets, 3)
        self.assertTrue(should_block_user(unique_subnets, threshold_subnets=3))

    def test_backward_ip_collection_not_lost(self):
        """IP collection is preserved while subnet counting remains deduplicated."""
        ips = ["10.0.1.2", "10.0.1.3", "10.0.2.9", "10.0.2.9"]
        subnet_map = build_subnet_map(ips)

        collected_ips = [ip for ips_in_subnet in subnet_map.values() for ip in ips_in_subnet]
        self.assertEqual(set(collected_ips), {"10.0.1.2", "10.0.1.3", "10.0.2.9"})
        self.assertEqual(len(subnet_map), 1)

    def test_unique_subnets_reduced_for_ip_churn_inside_one_16(self):
        """IP churn inside a single /16 yields fewer unique subnets than /24 logic."""
        ips = ["192.168.1.10", "192.168.2.11", "192.168.250.12"]

        subnet_map_24 = build_subnet_map(ips, ipv4_prefix=24)
        subnet_map_16 = build_subnet_map(ips)

        self.assertEqual(len(subnet_map_24), 3)
        self.assertEqual(len(subnet_map_16), 1)
        self.assertIn("192.168.0.0/16", subnet_map_16)


if __name__ == "__main__":
    unittest.main()
