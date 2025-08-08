"""
The problem description for this problem is in prompts/food_delivery.md.

To use, read through the problem description linked above - starting just with level 1.
Not looking ahead most accurately simulates how things like CodeSignal progressively show you the problem.

After implementing the first level, run `python food_delivery.py --level 1` and progress through all levels to level 4.

See the main readme for disclaimers and other info.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from collections import deque


@dataclass
class AssignedOrders:
    driver_id: str
    order_id: str


class FoodDeliverySystem:
    def __init__(self):
        self.drivers = deque()
        self.awaiting_orders = deque()
        self.awaiting_priority_orders = deque()
        self.assigned_orders = deque()  # tuple of driver id and order_id

        self.driver_status = {}
        self.order_status = {}

    def _get_next_order(self) -> Optional[str]:
        if self.awaiting_priority_orders:
            return self.awaiting_priority_orders.popleft()
        if self.awaiting_orders:
            return self.awaiting_orders.popleft()
        return None

    def place_order(self, order_id: str, priority: bool = False) -> None:
        """A new food order has been placed."""
        if self.drivers:
            next_driver = self.drivers.popleft()
            self.assigned_orders.append(
                AssignedOrders(order_id=order_id, driver_id=next_driver)
            )
            self.order_status[order_id] = "assigned"
            self.driver_status[next_driver] = "assigned"
        elif priority:
            self.awaiting_priority_orders.append(order_id)
            self.order_status[order_id] = "pending"
        else:
            self.awaiting_orders.append(order_id)
            self.order_status[order_id] = "pending"

    def driver_available(self, driver_id: str) -> None:
        """A new driver is now available to take an order."""
        next_order = self._get_next_order()
        if next_order:
            self.assigned_orders.append(
                AssignedOrders(order_id=next_order, driver_id=driver_id)
            )
            self.driver_status[driver_id] = "assigned"
            self.order_status[next_order] = "assigned"
        else:
            self.drivers.append(driver_id)
            self.driver_status[driver_id] = "waiting"

    def cancel_order(self, order_id: str) -> None:
        """Cancel a pending order. Has no effect if already assigned."""
        if order_id in self.awaiting_orders:
            self.awaiting_orders.remove(order_id)
        elif order_id in self.awaiting_priority_orders:
            self.awaiting_priority_orders.remove(order_id)
        else:
            raise Exception("order not found")

        self.order_status[order_id] = "cancelled"

    def cancel_driver(self, driver_id: str) -> None:
        """Cancel a pending driver. Has no effect if already assigned."""
        if driver_id in self.drivers:
            self.drivers.remove(driver_id)
        else:
            raise Exception("Driver not found")
        self.driver_status[driver_id] = "cancelled"

    def get_assignments(self) -> List[Tuple[str, str]]:
        """Return a list of (order_id, driver_id) pairs that have been assigned."""
        return [(o.order_id, o.driver_id) for o in self.assigned_orders]

    def get_status(self, order_id: str) -> str:
        """Return 'pending', 'cancelled', or 'assigned'"""
        return self.order_status[order_id]

    def get_driver_status(self, driver_id: str) -> str:
        """Return 'waiting', 'cancelled', or 'assigned'"""
        return self.driver_status[driver_id]


if __name__ == "__main__":
    print("Testing delivery")
    fds = FoodDeliverySystem()

    # --- Level 1: Basic FIFO assignment ---
    print("Level 1 test")
    fds.place_order("order1")
    fds.place_order("order2")
    fds.driver_available("driverA")
    fds.driver_available("driverB")
    assert set(fds.get_assignments()) == {("order1", "driverA"), ("order2", "driverB")}

    # --- Level 2: Cancellations ---
    print("Level 2 test")
    fds = FoodDeliverySystem()
    fds.place_order("order1")
    fds.place_order("order2")
    fds.cancel_order("order1")
    fds.driver_available("driverA")
    fds.driver_available("driverB")
    fds.cancel_driver("driverB")
    assert fds.get_assignments() == [("order2", "driverA")]

    # --- Level 3: Priority Orders ---
    print("Level 3 test")
    fds = FoodDeliverySystem()
    fds.place_order("order1")
    fds.place_order("order2")
    fds.place_order("orderP", priority=True)
    fds.driver_available("driverX")
    fds.driver_available("driverY")
    assignments = fds.get_assignments()
    assert ("orderP", "driverX") in assignments or ("orderP", "driverY") in assignments
    assigned_orders = [o for o, _ in assignments]
    assert assigned_orders.index("orderP") < assigned_orders.index("order1")

    # --- Level 4: Status Tracking ---
    print("Level 4 test")
    fds = FoodDeliverySystem()
    fds.place_order("order1")
    fds.place_order("order2", priority=True)
    fds.place_order("order3")
    fds.cancel_order("order3")
    fds.driver_available("driverA")
    fds.driver_available("driverB")
    fds.cancel_driver("driverB")

    # Assignments: order2 -> driverA
    assert fds.get_assignments() == [("order2", "driverA")]

    # Order statuses
    assert fds.get_status("order2") == "assigned"
    assert fds.get_status("order1") == "pending"
    assert fds.get_status("order3") == "cancelled"
    assert (
        fds.get_status("nonexistent") == "pending"
    )  # optional: could raise or return 'pending'

    # Driver statuses
    assert fds.get_driver_status("driverA") == "assigned"
    assert fds.get_driver_status("driverB") == "cancelled"
    assert (
        fds.get_driver_status("ghostDriver") == "waiting"
    )  # optional: depends on your impl
