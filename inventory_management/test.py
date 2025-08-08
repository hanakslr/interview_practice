"""
This is a test harness for the problem for the InventorySystem in inventory_management.py.

To run: `python inventory_management/test.py --level {lvl}` where level goes up to 3.
"""

import argparse
from inventory_system import InventorySystem


def test_exec(suite_name: str, tests: list[dict]):
    print("\n-----------------")
    print(f"\n Testing {suite_name}")
    inventory = InventorySystem()

    for test in tests:
        fn = test["fn"]
        args = test["args"]
        expected = test["expected"]

        result = getattr(inventory, fn)(*args)
        print(f"\n{fn}({', '.join(map(str, args))})")
        assert result == expected, f"❌ Expected {expected}, got {result}."
        print(f"✅ Passed: {'(empty)' if result == '' else result}")

    print(f"\n🥳 {suite_name} passes")


def test_level_1():
    """Level 1: Basic Item Management"""

    tests = [
        # 1. Add item "/warehouse/sectionA/item1" with 20 units
        {
            "fn": "add_item",
            "args": ["/warehouse/sectionA/item1", "20"],
            "expected": True,
        },
        # 2. Copy from a non-existing item -> should fail
        {
            "fn": "copy_item",
            "args": ["/not-existing.item", "/warehouse/sectionB/item1"],
            "expected": False,
        },
        # 3. Copy from existing item to new location -> should succeed
        {
            "fn": "copy_item",
            "args": ["/warehouse/sectionA/item1", "/warehouse/sectionB/item1"],
            "expected": True,
        },
        # 4. Try to add an item that already exists -> should fail
        {
            "fn": "add_item",
            "args": ["/warehouse/sectionB/item1", "35"],
            "expected": False,
        },
        # 5. Try to copy to a name that already exists -> should fail
        {
            "fn": "copy_item",
            "args": ["/warehouse/sectionB/item1", "/warehouse/sectionA/item1"],
            "expected": False,
        },
        # 6. Get quantity of an existing item -> should return "20"
        {
            "fn": "get_item_quantity",
            "args": ["/warehouse/sectionB/item1"],
            "expected": "20",
        },
        # 7. Get quantity of a non-existing item -> should return ""
        {"fn": "get_item_quantity", "args": ["/not-existing.item"], "expected": ""},
    ]

    test_exec("Level 1", tests)


def test_level_2():
    """Level 2: Item Search with Prefix and Suffix"""

    tests = [
        # Set up items
        {
            "fn": "add_item",
            "args": ["/warehouse/sectionX/itemA", "50"],
            "expected": True,
        },
        {"fn": "add_item", "args": ["/warehouse/itemB", "25"], "expected": True},
        {
            "fn": "add_item",
            "args": ["/warehouse/sectionY/itemC", "30"],
            "expected": True,
        },
        {
            "fn": "copy_item",
            "args": ["/warehouse/sectionY/itemC", "/warehouse/sectionZ/itemC"],
            "expected": True,
        },
        # Level 2: FIND_ITEM tests
        {
            "fn": "find_item",
            "args": ["/warehouse", "item"],
            "expected": "/warehouse/sectionX/itemA (50), /warehouse/sectionY/itemC (30), /warehouse/sectionZ/itemC (30), /warehouse/itemB (25)",
        },
        # No items match suffix "itemX"
        {"fn": "find_item", "args": ["/warehouse", "itemX"], "expected": ""},
        # No items match prefix "/sectionY"
        {"fn": "find_item", "args": ["/sectionY", "itemC"], "expected": ""},
    ]

    test_exec("Level 2", tests)


def test_level_3():
    """Level 3: User Management and Capacity Control"""

    tests = [
        # User management
        {"fn": "add_user", "args": ["user1", "1500"], "expected": True},  # create user1
        {
            "fn": "add_user",
            "args": ["user1", "1200"],
            "expected": False,
        },  # user1 already exists
        {"fn": "add_user", "args": ["user2", "2500"], "expected": True},  # create user2
        # Add itemBig by user1
        {
            "fn": "add_item_by",
            "args": ["user1", "/sectionA/itemBig", "600"],
            "expected": "900",
        },
        # Add itemMed by user1
        {"fn": "add_item_by", "args": ["user1", "/itemMed", "400"], "expected": "500"},
        # Copy itemMed to sectionA — still owned by user1 (should fail due to capacity)
        {"fn": "copy_item", "args": ["/itemMed", "/sectionA/itemMed"], "expected": ""},
        # Now user1 has used 600 + 400 = 1000, capacity left = 500
        {
            "fn": "add_item_by",
            "args": ["user1", "/itemSmall", "200"],
            "expected": "300",
        },  # succeeds
        # This will fail — not enough capacity
        {
            "fn": "add_item_by",
            "args": ["user1", "/sectionA/itemTiny", "100"],
            "expected": "",
        },
        # user2 adds itemMed — this is distinct from previous itemMed
        {"fn": "add_item_by", "args": ["user2", "/itemMed", "500"], "expected": "2000"},
        # Fail — item already exists
        {
            "fn": "add_item_by",
            "args": ["user1", "/sectionA/itemTiny", "100"],
            "expected": "",
        },
        # Fail — user2 doesn't have enough capacity for 2500
        {
            "fn": "add_item_by",
            "args": ["user2", "/storage/itemHuge", "2500"],
            "expected": "",
        },
        # Fail — user3 doesn't exist
        {
            "fn": "add_item_by",
            "args": ["user3", "/storage/itemHuge", "2500"],
            "expected": "",
        },
        # Expand user1's capacity to 4000 — success
        {"fn": "update_capacity", "args": ["user1", "4000"], "expected": "0"},
        # Shrink user1's capacity to 1000 — must delete 2 items
        {"fn": "update_capacity", "args": ["user1", "1000"], "expected": "2"},
        # Fail — user2 doesn't exist (assumes deletion happened)
        {"fn": "update_capacity", "args": ["user2", "5000"], "expected": ""},
    ]

    test_exec("Level 3", tests)


if __name__ == "__main__":
    print("🔄 Running inventory management")
    parser = argparse.ArgumentParser(
        description="A coding practice problem simulating an inventory management system, where it gets progressively more difficult through 3 levels."
    )

    parser.add_argument(
        "--level",
        type=int,
        default=3,
        help="The number of levels to run (optional - defaults to all)",
    )
    args = parser.parse_args()

    test_suites = [test_level_1, test_level_2, test_level_3]

    for i in range(min(3, args.level)):
        test_suites[i]()
