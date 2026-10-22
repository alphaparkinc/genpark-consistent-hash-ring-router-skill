"""Example usage for GenPark Consistent Hash Ring Router."""
from client import ConsistentHashRingRouter

def main():
    router = ConsistentHashRingRouter(virtual_node_factor=100)
    print("Adding cache shards to hash ring...")
    router.add_nodes(["cache_shard_us_east", "cache_shard_us_west", "cache_shard_eu_central"])

    keys = [f"prompt_cache_{i}" for i in range(1000)]
    stats = router.get_distribution_stats(keys)
    print("Key Distribution Summary:")
    print(f"Total keys: {stats['total_keys']}, Std Dev: {stats['std_dev']}")
    for node, info in stats["distribution"].items():
        print(f" - {node}: {info['count']} keys ({info['percentage']}%)")

    test_key = "user_conv_48291"
    assigned = router.get_node_for_key(test_key)
    print(f"
Key '{test_key}' routed to: {assigned}")

if __name__ == "__main__":
    main()
