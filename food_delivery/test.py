"""
This is a test harness for the problem for the FoodDeliverySystem in food_delivery/food_delivery.py.
"""

import argparse
from food_delivery_system import FoodDeliverySystem


def test_exec(suite_name: str, tests: list[dict]):
    print("\n-----------------")
    print(f"\n Testing {suite_name}")
    fds = FoodDeliverySystem()

    for test in tests:
        fn = test["fn"]
        args = test["args"]
        expected = test["expected"]

        result = getattr(fds, fn)(*args)
        print(f"\n{fn}({', '.join(map(str, args))})")

        if "assert_function" in test:
            # Custom assertion for more complex checks
            test["assert_function"](result, expected, fds)
            print(f"✅ Passed: {result} ")
        else:
            assert result == expected, f"❌ Expected {expected}, got {result}."
            print(f"✅ Passed: {'(empty)' if result == '' else result}")

    print(f"\n🥳 {suite_name} passes")


def test_level_1():
    """Level 1: Basic FIFO assignment"""

    def check_assignments(result, expected, fds):
        assignments = fds.get_assignments()
        assert set(assignments) == expected, (
            f"❌ Expected {expected}, got {set(assignments)}."
        )

    tests = [
        {"fn": "place_order", "args": ["order1"], "expected": None},
        {"fn": "place_order", "args": ["order2"], "expected": None},
        {"fn": "driver_available", "args": ["driverA"], "expected": None},
        {"fn": "driver_available", "args": ["driverB"], "expected": None},
        {
            "fn": "get_assignments",
            "args": [],
            "expected": {("order1", "driverA"), ("order2", "driverB")},
            "assert_function": check_assignments,
        },
    ]

    test_exec("Level 1", tests)


def test_level_2():
    """Level 2: Cancellations"""
    tests = [
        {"fn": "place_order", "args": ["order1"], "expected": None},
        {"fn": "place_order", "args": ["order2"], "expected": None},
        {"fn": "cancel_order", "args": ["order1"], "expected": None},
        {"fn": "driver_available", "args": ["driverA"], "expected": None},
        {"fn": "driver_available", "args": ["driverB"], "expected": None},
        {"fn": "cancel_driver", "args": ["driverB"], "expected": None},
        {"fn": "get_assignments", "args": [], "expected": [("order2", "driverA")]},
    ]

    test_exec("Level 2", tests)


def test_level_3():
    """Level 3: Priority Orders"""

    def check_priority_assignment(result, expected, fds):
        assignments = fds.get_assignments()
        # Check that priority order is assigned
        priority_assigned = any("orderP" in assignment for assignment in assignments)
        assert priority_assigned, "❌ Priority order should be assigned"

        # Check that priority order comes before regular orders
        assigned_orders = [o for o, _ in assignments]
        if "orderP" in assigned_orders and "order1" in assigned_orders:
            assert assigned_orders.index("orderP") < assigned_orders.index("order1"), (
                "❌ Priority order should come before regular orders"
            )

    tests = [
        {"fn": "place_order", "args": ["order1"], "expected": None},
        {"fn": "place_order", "args": ["order2"], "expected": None},
        {"fn": "place_order", "args": ["orderP", True], "expected": None},
        {"fn": "driver_available", "args": ["driverX"], "expected": None},
        {"fn": "driver_available", "args": ["driverY"], "expected": None},
        {
            "fn": "get_assignments",
            "args": [],
            "expected": None,
            "assert_function": check_priority_assignment,
        },
    ]

    test_exec("Level 3", tests)


def test_level_4():
    """Level 4: Status Tracking"""
    tests = [
        {"fn": "place_order", "args": ["order1"], "expected": None},
        {"fn": "place_order", "args": ["order2", True], "expected": None},
        {"fn": "place_order", "args": ["order3"], "expected": None},
        {"fn": "cancel_order", "args": ["order3"], "expected": None},
        {"fn": "driver_available", "args": ["driverA"], "expected": None},
        {"fn": "driver_available", "args": ["driverB"], "expected": None},
        {"fn": "driver_available", "args": ["driverC"], "expected": None},
        {"fn": "cancel_driver", "args": ["driverC"], "expected": None},
        {"fn": "place_order", "args": ["order4"], "expected": None},
        {
            "fn": "get_assignments",
            "args": [],
            "expected": [("order2", "driverA"), ("order1", "driverB")],
        },
        {"fn": "get_status", "args": ["order2"], "expected": "assigned"},
        {"fn": "get_status", "args": ["order4"], "expected": "pending"},
        {"fn": "get_status", "args": ["order3"], "expected": "cancelled"},
        {"fn": "get_driver_status", "args": ["driverA"], "expected": "assigned"},
        {"fn": "get_driver_status", "args": ["driverC"], "expected": "cancelled"},
    ]

    test_exec("Level 4", tests)


if __name__ == "__main__":
    print("🔄 Running food delivery")
    parser = argparse.ArgumentParser(
        description="A coding practice problem simulating a food delivery system, where it gets progressively more difficult through 4 levels."
    )

    parser.add_argument(
        "--level",
        type=int,
        default=4,
        help="The number of levels to run (optional - defaults to all)",
    )
    args = parser.parse_args()

    test_suites = [test_level_1, test_level_2, test_level_3, test_level_4]

    for i in range(min(4, args.level)):
        test_suites[i]()
