from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    content: str
    timestamp: Optional[int] = None
    expiry: Optional[int] = None

    def is_valid_at(self, timestamp: int):
        if self.expiry is None:
            return True

        if timestamp < self.timestamp + self.expiry:
            return True

        return False


class ChatSystem:
    def __init__(self):
        self.user_messages = defaultdict(set)
        self.messages: dict[str, Message] = {}
        self.backups = {}  # key = timestamp, value= user_messages: {}, messages: {}

    def send_message(self, user_id: str, message_id: str, message: str):
        self.messages[message_id] = Message(content=message)
        self.user_messages[user_id].add(message_id)

        return ""

    def get_message(self, user_id: str, message_id: str) -> str:
        if message_id in self.user_messages[user_id]:
            return self.messages[message_id].content

        return ""

    def delete_message(self, user_id: str, message_id: str) -> bool:
        if message_id in self.user_messages[user_id]:
            del self.messages[message_id]
            self.user_messages[user_id].remove(message_id)
            return True
        return False

    def list_messages(self, user_id: str) -> str:
        return ", ".join(
            [
                f"{msg_id}({self.messages[msg_id].content})"
                for msg_id in sorted(self.user_messages[user_id])
            ]
        )

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> str:
        return ", ".join(
            [
                f"{msg_id}({self.messages[msg_id].content})"
                for msg_id in sorted(self.user_messages[user_id])
                if msg_id.startswith(prefix)
            ]
        )

    def send_message_at(
        self, user_id: str, message_id: str, message: str, timestamp: int
    ):
        return self.send_message_with_expiry(
            user_id=user_id,
            message_id=message_id,
            message=message,
            timestamp=timestamp,
            expiry=None,
        )

    def send_message_with_expiry(
        self, user_id: str, message_id: str, message: str, timestamp: int, expiry: int
    ):
        self.messages[message_id] = Message(
            content=message, timestamp=timestamp, expiry=expiry
        )
        self.user_messages[user_id].add(message_id)

    def delete_message_at(self, user_id: str, message_id: str, timestamp: int) -> bool:
        if message_id not in self.user_messages[user_id]:
            return False

        msg = self.messages[message_id]
        if msg and (msg.expiry is None or timestamp < (msg.timestamp + msg.expiry)):
            self.delete_message(user_id, message_id)
            return True

        return False  # not found or already expired

    def get_message_at(self, user_id: str, message_id: str, timestamp: int) -> str:
        if message_id not in self.user_messages[user_id]:
            print("not found")
            return ""

        msg = self.messages[message_id]
        if msg and msg.is_valid_at(timestamp):
            print(msg.content)
            return msg.content

        return ""

    def list_messages_at(self, user_id: str, timestamp: int) -> str:
        res = ", ".join(
            [
                f"{msg_id}({self.messages[msg_id].content})"
                for msg_id in sorted(self.user_messages[user_id])
                if self.messages[msg_id].is_valid_at(timestamp)
            ]
        )

        print(res)

        return res

    def list_messages_by_prefix_at(
        self, user_id: str, prefix: str, timestamp: int
    ) -> str:
        return ", ".join(
            [
                f"{msg_id}({self.messages[msg_id].content})"
                for msg_id in sorted(self.user_messages[user_id])
                if msg_id.startswith(prefix)
                and self.messages[msg_id].is_valid_at(timestamp)
            ]
        )

    def zip_messages(self, timestamp: int) -> str:
        valid_msgs = {
            msg_id: msg
            for msg_id, msg in self.messages.items()
            if msg.is_valid_at(timestamp)
        }

        bu_users = {}
        for user in self.user_messages:
            bu_users[user] = [
                msg_id for msg_id in self.user_messages[user] if msg_id in valid_msgs
            ]

        self.backups[timestamp] = {"user_messages": bu_users, "messages": valid_msgs}

        return len(valid_msgs.keys())

    def unzip_messages(self, restore_timestamp: int, backup_timestamp: int) -> str:
        # find self.backups at or before backup_timestamp
        restore_from = None
        for b in reversed(self.backups):
            if b <= backup_timestamp:
                restore_from = b
                break

        if not restore_from:
            return ""

        self.user_messages = self.backups[b]["user_messages"]
        self.messages = self.backups[b]["messages"]

        for m in self.messages.values():
            if m.timestamp:
                m.timestamp = restore_timestamp

        return ""


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
    # Tests same thing as level 1, but using
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
    # Tests same thing as level 2, but using the test_exec pattern
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
    # Tests same thing as level 3, but using the test_exec pattern
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
    # Tests same thing as level 4, but using the test_exec pattern
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
    print("Running chat")
    test_level_1()
    test_level_2()
    test_level_3()
    test_level_4()
