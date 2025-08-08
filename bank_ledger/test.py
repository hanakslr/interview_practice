"""
This is a test harness for the problem for the BankLedger in bank_ledger.py.

To run: `python bank_ledger/test.py --level {lvl}` where level goes up to 3.
"""

import argparse
from bank_system import BankLedger


def test_exec(suite_name: str, tests: list[dict]):
    print("\n-----------------")
    print(f"\n Testing {suite_name}")
    ledger = BankLedger()

    for test in tests:
        fn = test["fn"]
        args = test["args"]
        expected = test["expected"]

        if "exception" in test and test["exception"]:
            # Test that an exception is raised
            try:
                getattr(ledger, fn)(*args)
                assert False, (
                    f"❌ Expected exception for {fn}({', '.join(map(str, args))})"
                )
            except Exception:
                print(
                    f"✅ Passed: {fn}({', '.join(map(str, args))}) - Expected exception raised"
                )
        else:
            result = getattr(ledger, fn)(*args)
            print(f"\n{fn}({', '.join(map(str, args))})")
            assert result == expected, f"❌ Expected {expected}, got {result}."
            print(f"✅ Passed: {'(empty)' if result == '' else result}")

    print(f"\n🥳 {suite_name} passes")


def test_level_1():
    """Level 1: Account Management and Basic Operations"""

    tests = [
        {"fn": "open_account", "args": ["acct1", ["USD", "EUR"]], "expected": None},
        {"fn": "open_account", "args": ["acct2", ["USD", "BTC"]], "expected": None},
        {"fn": "get_balance", "args": ["acct1", "USD"], "expected": 0},
        {"fn": "get_balance", "args": ["acct1", "EUR"], "expected": 0},
        {"fn": "get_balance", "args": ["acct2", "USD"], "expected": 0},
        {"fn": "get_balance", "args": ["acct2", "BTC"], "expected": 0},
        {
            "fn": "get_balance",
            "args": ["acctX", "USD"],
            "expected": None,
            "exception": True,
        },
        {
            "fn": "get_balance",
            "args": ["acct1", "JPY"],
            "expected": None,
            "exception": True,
        },
    ]

    test_exec("Level 1", tests)


def test_level_2():
    """Level 2: Deposits, Withdrawals, and Transfers"""

    tests = [
        {
            "fn": "open_account",
            "args": ["acct1", ["USD", "EUR", "BTC"]],
            "expected": None,
        },
        {
            "fn": "open_account",
            "args": ["acct2", ["USD", "EUR", "BTC"]],
            "expected": None,
        },
        {"fn": "deposit", "args": ["acct1", "USD", 10000], "expected": True},
        {"fn": "get_balance", "args": ["acct1", "USD"], "expected": 10000},
        {"fn": "withdraw", "args": ["acct1", "USD", 4000], "expected": True},
        {"fn": "get_balance", "args": ["acct1", "USD"], "expected": 6000},
        {"fn": "withdraw", "args": ["acct1", "USD", 10000], "expected": False},
        {"fn": "get_balance", "args": ["acct1", "USD"], "expected": 6000},
        {
            "fn": "transfer",
            "args": ["acct1", "acct2", "USD", "EUR", 3000],
            "expected": True,
        },
        {"fn": "get_balance", "args": ["acct1", "USD"], "expected": 3000},
        {
            "fn": "get_balance",
            "args": ["acct2", "EUR"],
            "expected": 2700,
        },  # 3000 * 0.9 = 2700
        {"fn": "deposit", "args": ["acct1", "BTC", 500], "expected": True},
        {
            "fn": "transfer",
            "args": ["acct1", "acct2", "BTC", "BTC", 300],
            "expected": True,
        },
        {"fn": "get_balance", "args": ["acct1", "BTC"], "expected": 200},
        {"fn": "get_balance", "args": ["acct2", "BTC"], "expected": 300},
        {
            "fn": "transfer",
            "args": ["acct1", "acct2", "BTC", "BTC", 1000],
            "expected": False,
        },
    ]

    test_exec("Level 2", tests)


def test_level_3():
    """Level 3: Scheduled and Recurring Payments"""

    tests = [
        {"fn": "open_account", "args": ["alice"], "expected": None},
        {"fn": "open_account", "args": ["bob"], "expected": None},
        {"fn": "open_account", "args": ["charlie"], "expected": None},
        {"fn": "deposit", "args": ["alice", "USD", 10000], "expected": True},
        {"fn": "deposit", "args": ["bob", "USD", 3000], "expected": True},
        {"fn": "deposit", "args": ["charlie", "USD", 0], "expected": True},
        {
            "fn": "schedule_payment",
            "args": ["alice", "bob", "USD", "USD", 2500, 3],
            "expected": None,
        },
        {
            "fn": "schedule_recurring_payment",
            "args": ["bob", "charlie", "USD", "USD", 1000, 2, 2],
            "expected": None,
        },
        # Check initial balances
        {"fn": "get_balance", "args": ["alice", "USD"], "expected": 10000},
        {"fn": "get_balance", "args": ["bob", "USD"], "expected": 3000},
        {"fn": "get_balance", "args": ["charlie", "USD"], "expected": 0},
        # Advance to day 2: first recurring payment triggers
        {"fn": "advance_day", "args": [2], "expected": None},
        {"fn": "get_balance", "args": ["bob", "USD"], "expected": 2000},
        {"fn": "get_balance", "args": ["charlie", "USD"], "expected": 1000},
        # Advance to day 3: one-time payment from Alice triggers
        {"fn": "advance_day", "args": [3], "expected": None},
        {"fn": "get_balance", "args": ["alice", "USD"], "expected": 7500},
        {"fn": "get_balance", "args": ["bob", "USD"], "expected": 4500},
        # Advance to day 4: second recurring payment triggers
        {"fn": "advance_day", "args": [4], "expected": None},
        {"fn": "get_balance", "args": ["bob", "USD"], "expected": 3500},
        {"fn": "get_balance", "args": ["charlie", "USD"], "expected": 2000},
        # Advance to day 12: recurring payment skipped (insufficient funds)
        {"fn": "advance_day", "args": [12], "expected": None},
        {
            "fn": "get_balance",
            "args": ["bob", "USD"],
            "expected": 500,
        },  # no change - insufficient funds
        {"fn": "get_balance", "args": ["charlie", "USD"], "expected": 5000},
    ]

    test_exec("Level 3", tests)


if __name__ == "__main__":
    print("🔄 Running bank ledger")
    parser = argparse.ArgumentParser(
        description="A coding practice problem simulating a bank ledger system, where it gets progressively more difficult through 3 levels."
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
