"""
This is a test harness for the problem for the ChatSystem in chat/chat_system.py.
"""

import argparse
from chat_system import ChatSystem


def test_exec(suite_name: str, tests: list[dict]):
    print("\n-----------------")
    print(f"\n Testing {suite_name}")
    cs = ChatSystem()

    for test in tests:
        fn = test["fn"]
        args = test["args"]
        expected = test["expected"]

        result = getattr(cs, fn)(*args)
        print(f"\n{fn}({', '.join(map(str, args))})")
        assert result == expected, f"❌ Expected {expected}, got {result}."
        print(f"✅ Passed: {'(empty)' if result == '' else result}")

    print(f"\n🥳 {suite_name} passes")


def test_level_1():
    tests = [
        {"fn": "send_message", "args": ["Alice", "msg1", "Hello Bob!"], "expected": ""},
        {
            "fn": "send_message",
            "args": ["Alice", "msg2", "How are you?"],
            "expected": "",
        },
        {"fn": "get_message", "args": ["Alice", "msg1"], "expected": "Hello Bob!"},
        {"fn": "get_message", "args": ["Alice", "msg3"], "expected": ""},
        {"fn": "delete_message", "args": ["Alice", "msg1"], "expected": True},
        {"fn": "delete_message", "args": ["Alice", "msg3"], "expected": False},
    ]

    test_exec("Level 1", tests)


def test_level_2():
    tests = [
        {
            "fn": "send_message",
            "args": ["Alice", "msg10", "Meeting at 5"],
            "expected": "",
        },
        {
            "fn": "send_message",
            "args": ["Alice", "msg20", "See you soon"],
            "expected": "",
        },
        {
            "fn": "send_message",
            "args": ["Alice", "note1", "Buy groceries"],
            "expected": "",
        },
        {
            "fn": "list_messages_by_prefix",
            "args": ["Alice", "msg"],
            "expected": "msg10(Meeting at 5), msg20(See you soon)",
        },
        {
            "fn": "list_messages",
            "args": ["Alice"],
            "expected": "msg10(Meeting at 5), msg20(See you soon), note1(Buy groceries)",
        },
        {"fn": "list_messages_by_prefix", "args": ["Bob", ""], "expected": ""},
    ]

    test_exec("Level 2", tests)


def test_level_3():
    tests = [
        {
            "fn": "send_message_with_expiry",
            "args": ["Alice", "msg1", "See you soon", 11, 10],
            "expected": None,
        },
        {
            "fn": "send_message_at",
            "args": ["Alice", "msg2", "Good morning!", 4],
            "expected": None,
        },
        {"fn": "delete_message_at", "args": ["Alice", "msg1", 8], "expected": True},
        {"fn": "get_message_at", "args": ["Alice", "msg1", 12], "expected": ""},
        {
            "fn": "list_messages_at",
            "args": ["Alice", 13],
            "expected": "msg2(Good morning!)",
        },
    ]

    test_exec("Level 3", tests)


def test_level_4():
    tests = [
        {
            "fn": "send_message_with_expiry",
            "args": ["Bob", "msg1", "Meeting at 5", 60, 30],
            "expected": None,
        },
        {"fn": "zip_messages", "args": [70], "expected": 1},
        {
            "fn": "send_message_with_expiry",
            "args": ["Bob", "msg2", "Dinner at 8", 75, 20],
            "expected": None,
        },
        {"fn": "unzip_messages", "args": [100, 70], "expected": ""},
        {
            "fn": "list_messages_at",
            "args": ["Bob", 100],
            "expected": "msg1(Meeting at 5)",
        },
    ]

    test_exec("Level 4", tests)


if __name__ == "__main__":
    print("🔄 Running chat")
    parser = argparse.ArgumentParser(
        description="A coding practice problem simulating a chat messaging system, where it get progressively more difficult through 4 levels."
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
