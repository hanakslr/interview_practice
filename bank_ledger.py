from collections import defaultdict
from dataclasses import dataclass
import math
from typing import List


@dataclass
class Transfer:
    from_account: str
    to_account: str
    from_currency: str
    to_currency: str
    amount: int


@dataclass
class RecurringTransfer(Transfer):
    start_date: int
    frequency: int


class BankLedger:
    def __init__(self):
        self.account_balances = {}
        self.scheduled_payments: dict[int, List[Transfer]] = defaultdict(
            list
        )  # mapping from day int to list of transactions
        self.recurring_payments: list[RecurringTransfer] = []
        self.day = 0

    @classmethod
    def get_fx_rate(cls, from_currency, to_currency):
        # Simple hardcoded FX table for testing
        fx_table = {
            ("USD", "EUR"): 0.9,
            ("EUR", "USD"): 1.1,
            ("USD", "USD"): 1.0,
            ("EUR", "EUR"): 1.0,
            ("USD", "BTC"): 0.00005,
            ("BTC", "USD"): 20000,
        }
        return fx_table[(from_currency, to_currency)]

    def open_account(self, account_id: str, currencies: List[str] = ["USD"]) -> None:
        """Creates a new account with a zero balance for the specified currencies."""
        if account_id in self.account_balances:
            raise Exception("Account already exists")

        self.account_balances[account_id] = {curr: 0 for curr in currencies}

    def get_balance(self, account_id: str, currency: str) -> int:
        """Returns the current balance of the given account."""

        if account_id not in self.account_balances:
            raise Exception("Unknown account")  # not found

        if currency not in self.account_balances[account_id]:
            raise Exception("Unused currency")

        return self.account_balances[account_id][currency]

    def deposit(self, account_id: str, currency: str, amount: int) -> None:
        if account_id not in self.account_balances:
            raise Exception("Unknown account")

        if currency not in self.account_balances[account_id]:
            self.account_balances[account_id][currency] = amount
        else:
            self.account_balances[account_id][currency] += amount

        return True

    def withdraw(self, account_id: str, currency: str, amount: int) -> bool:
        if account_id not in self.account_balances:
            raise Exception("Unknown account")

        if currency not in self.account_balances[account_id]:
            return False

        if amount > self.account_balances[account_id][currency]:
            return False

        self.account_balances[account_id][currency] -= amount

        return True

    def transfer(
        self,
        from_account: str,
        to_account: str,
        from_currency: str,
        to_currency: str,
        amount: int,
    ) -> bool:
        # From account in from_currency
        if (
            from_account not in self.account_balances
            or to_account not in self.account_balances
        ):
            raise Exception("Account not found")

        if (
            from_currency not in self.account_balances[from_account]
            or self.account_balances[from_account][from_currency] < amount
        ):
            return False

        self.account_balances[from_account][from_currency] -= amount

        # We have a sufficient amount, now we need to convert it and add it to the new account
        if from_currency != to_currency:
            rate = BankLedger.get_fx_rate(from_currency, to_currency)  # float value
            converted_amount = math.floor(amount * rate)
        else:
            converted_amount = amount

        if to_currency not in self.account_balances[to_account]:
            self.account_balances[to_account][to_currency] = converted_amount
        else:
            self.account_balances[to_account][to_currency] += converted_amount

        return True

    def schedule_payment(
        self,
        from_account: str,
        to_account: str,
        from_currency: str,
        to_currency: str,
        amount: int,
        day: int,
    ) -> None:
        self.scheduled_payments[day].append(
            Transfer(
                from_account=from_account,
                to_account=to_account,
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
            )
        )

    def schedule_recurring_payment(
        self,
        from_account: str,
        to_account: str,
        from_currency: str,
        to_currency: str,
        amount: int,
        start_day: int,
        frequency: int,
    ) -> None:
        self.recurring_payments.append(
            RecurringTransfer(
                from_account=from_account,
                to_account=to_account,
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
                start_date=start_day,
                frequency=frequency,
            )
        )

    def process_day(self, day: int) -> None:
        """
        Process all transactions for this day, scheduled ones first, then recurring. Skip those with insufficient funds
        """
        for t in self.scheduled_payments[day]:
            # Prob should mark this as completed somehow.
            self.transfer(
                from_account=t.from_account,
                to_account=t.to_account,
                from_currency=t.from_currency,
                to_currency=t.to_currency,
                amount=t.amount,
            )

        for t in self.recurring_payments:
            # Do we need to execute it today?
            if day >= t.start_date and ((day - t.start_date) % t.frequency) == 0:
                self.transfer(
                    from_account=t.from_account,
                    to_account=t.to_account,
                    from_currency=t.from_currency,
                    to_currency=t.to_currency,
                    amount=t.amount,
                )

    def advance_day(self, to_day: int) -> None:
        """
        Prcess all transfers in between the previous day and the new day (inclusive of the new day)
        """
        for day in range(self.day, to_day):
            self.process_day(day + 1)

        self.day = to_day


if __name__ == "__main__":
    print("Level 1")
    ledger = BankLedger()

    # Open two accounts with different currencies
    ledger.open_account("acct1", ["USD", "EUR"])
    ledger.open_account("acct2", ["USD", "BTC"])

    # All balances should be zero initially
    assert ledger.get_balance("acct1", "USD") == 0
    assert ledger.get_balance("acct1", "EUR") == 0
    assert ledger.get_balance("acct2", "USD") == 0
    assert ledger.get_balance("acct2", "BTC") == 0

    # Invalid account
    try:
        ledger.get_balance("acctX", "USD")
        assert False, "Expected exception for unknown account"
    except Exception:
        pass

    # Invalid currency
    try:
        ledger.get_balance("acct1", "JPY")
        assert False, "Expected exception for unknown currency"
    except Exception:
        pass

    print("Level 2")
    ledger = BankLedger()
    ledger.open_account("acct1", ["USD", "EUR", "BTC"])
    ledger.open_account("acct2", ["USD", "EUR", "BTC"])

    # Deposit USD into acct1
    ledger.deposit("acct1", "USD", 100_00)  # $100.00
    assert ledger.get_balance("acct1", "USD") == 100_00

    # Withdraw within balance
    success = ledger.withdraw("acct1", "USD", 40_00)
    assert success
    assert ledger.get_balance("acct1", "USD") == 60_00

    # Withdraw more than balance
    success = ledger.withdraw("acct1", "USD", 100_00)
    assert not success
    assert ledger.get_balance("acct1", "USD") == 60_00

    # Transfer $30 USD → EUR to acct2 (1 USD = 0.9 EUR)
    success = ledger.transfer("acct1", "acct2", "USD", "EUR", 30_00)
    assert success
    # $30 transferred → 27 EUR (rounded down)
    assert ledger.get_balance("acct1", "USD") == 30_00
    assert ledger.get_balance("acct2", "EUR") == 27_00

    # Transfer BTC to BTC
    ledger.deposit("acct1", "BTC", 5_00)
    success = ledger.transfer("acct1", "acct2", "BTC", "BTC", 3_00)
    assert success
    assert ledger.get_balance("acct1", "BTC") == 2_00
    assert ledger.get_balance("acct2", "BTC") == 3_00

    # Fail: insufficient BTC
    assert not ledger.transfer("acct1", "acct2", "BTC", "BTC", 10_00)

    print("Level 3")

    ledger = BankLedger()

    # --- Setup accounts ---
    ledger.open_account("alice")
    ledger.open_account("bob")
    ledger.open_account("charlie")

    # --- Initial deposits ---
    ledger.deposit("alice", "USD", 10000)
    ledger.deposit("bob", "USD", 3000)
    ledger.deposit("charlie", "USD", 0)

    # --- Schedule payments ---
    # Alice schedules a one-time payment to Bob on day 3
    ledger.schedule_payment("alice", "bob", "USD", "USD", 2500, day=3)

    # Bob schedules a recurring payment to Charlie every 2 days starting on day 2
    ledger.schedule_recurring_payment(
        "bob", "charlie", "USD", "USD", 1000, start_day=2, frequency=2
    )

    # --- Check balances before any payments ---
    assert ledger.get_balance("alice", "USD") == 10000
    assert ledger.get_balance("bob", "USD") == 3000
    assert ledger.get_balance("charlie", "USD") == 0

    # --- Advance to day 2: first recurring payment triggers ---
    ledger.advance_day(2)
    assert ledger.get_balance("bob", "USD") == 2000
    assert ledger.get_balance("charlie", "USD") == 1000

    # --- Advance to day 3: one-time payment from Alice triggers ---
    ledger.advance_day(3)
    assert ledger.get_balance("alice", "USD") == 7500
    assert ledger.get_balance("bob", "USD") == 4500

    # --- Advance to day 4: second recurring payment triggers ---
    ledger.advance_day(4)
    assert ledger.get_balance("bob", "USD") == 3500
    assert ledger.get_balance("charlie", "USD") == 2000

    # --- Advance to day 6: third recurring payment triggers ---
    ledger.advance_day(6)
    assert ledger.get_balance("bob", "USD") == 2500
    assert ledger.get_balance("charlie", "USD") == 3000

    # --- Advance to day 8: fourth recurring payment triggers ---
    ledger.advance_day(8)
    assert ledger.get_balance("bob", "USD") == 1500
    assert ledger.get_balance("charlie", "USD") == 4000

    # --- Advance to day 10: fifth recurring payment triggers ---
    ledger.advance_day(10)
    assert ledger.get_balance("bob", "USD") == 500
    assert ledger.get_balance("charlie", "USD") == 5000

    # --- Advance to day 12: sixth recurring payment skipped (insufficient funds) ---
    ledger.advance_day(12)
    assert ledger.get_balance("bob", "USD") == 500  # no change
    assert ledger.get_balance("charlie", "USD") == 5000
