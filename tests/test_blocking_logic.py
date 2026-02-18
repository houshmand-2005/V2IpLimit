import unittest

from utils.subnets import build_subnet_map, should_block_user


class TestBlockingLogic(unittest.TestCase):
    def test_many_ips_same_subnet_counts_as_one(self):
        ips = ["10.0.1.2", "10.0.1.3", "10.0.1.250", "10.0.1.2"]
        subnet_map = build_subnet_map(ips, ipv4_prefix=24)
        unique_subnets = len(subnet_map)

        self.assertEqual(unique_subnets, 1)
        self.assertFalse(should_block_user(unique_subnets, threshold_subnets=2))

    def test_different_subnets_count_separately(self):
        ips = ["10.0.1.2", "10.0.2.9", "10.0.3.7"]
        subnet_map = build_subnet_map(ips, ipv4_prefix=24)
        unique_subnets = len(subnet_map)

        self.assertEqual(unique_subnets, 3)
        self.assertTrue(should_block_user(unique_subnets, threshold_subnets=3))

    def test_backward_ip_collection_not_lost(self):
        ips = ["10.0.1.2", "10.0.1.3", "10.0.2.9", "10.0.2.9"]
        subnet_map = build_subnet_map(ips)

        collected_ips = [ip for ips_in_subnet in subnet_map.values() for ip in ips_in_subnet]
        self.assertEqual(set(collected_ips), {"10.0.1.2", "10.0.1.3", "10.0.2.9"})
        self.assertEqual(len(subnet_map), 2)


if __name__ == "__main__":
    unittest.main()
