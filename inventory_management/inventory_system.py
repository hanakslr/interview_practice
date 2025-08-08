from collections import defaultdict
from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    quantity: int
    owner_id: Optional[str]


class InventorySystem:
    def __init__(self):
        self.items: dict[str, Item] = {}
        self.users = {}

    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self.users:
            return False

        self.users[user_id] = capacity
        return True

    def add_item(self, name: str, quantity: int, owner_id=None) -> bool:
        if name in self.items:
            return False

        self.items[name] = Item(quantity=quantity, owner_id=owner_id)
        return True

    def _get_usage_for_user(self, user_id):
        return sum([qty for qty, i in self.items.items() if i.owner_id == user_id])

    def add_item_by(self, user_id: str, name: str, quantity: int) -> bool:
        """
        Can either have users keep track of their items
        or items keep track of their owners

        """
        if user_id not in self.users or quantity > self.users[user_id]:
            return False

        quantity = int(quantity)

        # Get the qty they already have
        allocated = self._get_usage_for_user(user_id=user_id)

        if quantity + allocated > self.users[user_id]:
            return False

        can_add = self.add_item(name, quantity, user_id)

        if can_add:
            return quantity
        return ""

    def update_capacity(self, user_id: str, capacity: int) -> str:
        if user_id not in self.users:
            return ""
        capacity = int(capacity)

        usage = self._get_usage_for_user(user_id)

        if usage <= capacity:
            return "0"

        sorted_items = sorted(
            [
                (i.quantity, name)
                for name, i in self.items.items()
                if i.owner_id == user_id
            ]
        )

        removed_count = 0

        while (usage - removed_count) > capacity:
            rem = sorted_items.pop()
            self.items[rem[1]] = None
            removed_count += rem[0]

        return removed_count

    def copy_item(self, name_from: str, name_to: str) -> str:
        if name_to in self.items:
            return False

        if name_from not in self.items:
            return False

        self.items[name_to] = self.items[name_from]

        return True

    def get_item_quantity(self, name: str) -> str:
        item = self.items.get(name, None)

        if not item:
            return ""

        return item.quantity

    def find_item(self, prefix: str, suffix: str) -> str:
        """
        output should be in descending order, in order of ties do lexographically
        """

        matching = defaultdict(list)

        for item_name, i in self.items.items():
            parts = item_name.strip("/").split("/")

            if parts[0].startswith(prefix.strip("/")) and parts[-1].startswith(suffix):
                matching[i.quantity].append(item_name)

        matching = dict(sorted(matching.items(), reverse=True))

        res = []

        for qty, items in matching.items():
            res.append(", ".join([f"{item} ({qty})" for item in sorted(items)]))

        return ", ".join(res)


def test_inventory_system_level1():
    print("Level 1")
    inventory = InventorySystem()

    # 1. Add item "/warehouse/sectionA/item1" with 20 units
    assert inventory.add_item("/warehouse/sectionA/item1", "20") == True

    # 2. Copy from a non-existing item -> should fail
    assert (
        inventory.copy_item("/not-existing.item", "/warehouse/sectionB/item1") == False
    )

    # 3. Copy from existing item to new location -> should succeed
    assert (
        inventory.copy_item("/warehouse/sectionA/item1", "/warehouse/sectionB/item1")
        == True
    )

    # 4. Try to add an item that already exists -> should fail
    assert inventory.add_item("/warehouse/sectionB/item1", "35") == False

    # 5. Try to copy to a name that already exists -> should fail
    assert (
        inventory.copy_item("/warehouse/sectionB/item1", "/warehouse/sectionA/item1")
        == False
    )

    # 6. Get quantity of an existing item -> should return "20"
    assert inventory.get_item_quantity("/warehouse/sectionB/item1") == "20"

    # 7. Get quantity of a non-existing item -> should return ""
    assert inventory.get_item_quantity("/not-existing.item") == ""


def test_inventory_system_level2():
    print("level 2")
    inventory = InventorySystem()

    # Level 1 operations
    assert inventory.add_item("/warehouse/sectionX/itemA", "50") == True
    assert inventory.add_item("/warehouse/itemB", "25") == True
    assert inventory.add_item("/warehouse/sectionY/itemC", "30") == True
    assert (
        inventory.copy_item("/warehouse/sectionY/itemC", "/warehouse/sectionZ/itemC")
        == True
    )

    # Level 2: FIND_ITEM
    res = inventory.find_item("/warehouse", "item")
    print(f"{res=}")
    assert res == (
        "/warehouse/sectionX/itemA (50), /warehouse/sectionY/itemC (30), /warehouse/sectionZ/itemC (30), /warehouse/itemB (25)"
    )

    # No items match suffix "itemX"
    assert inventory.find_item("/warehouse", "itemX") == ""

    # No items match prefix "/sectionY"
    assert inventory.find_item("/sectionY", "itemC") == ""


def test_inventory_system_level3():
    print("level 3")
    inventory = InventorySystem()

    # Level 3 operations
    assert inventory.add_user("user1", "1500") == True  # create user1
    assert inventory.add_user("user1", "1200") == False  # user1 already exists
    assert inventory.add_user("user2", "2500") == True  # create user2

    # Add itemBig by user1
    assert inventory.add_item_by("user1", "/sectionA/itemBig", "600") == "900"

    # Add itemMed by user1
    assert inventory.add_item_by("user1", "/itemMed", "400") == "500"

    # Copy itemMed to sectionA — still owned by user1
    assert inventory.copy_item("/itemMed", "/sectionA/itemMed") == ""

    # Now user1 has used 600 + 400 + 400 = 1400, capacity left = 100
    assert (
        inventory.add_item_by("user1", "/itemSmall", "200") == "300"
    )  # succeeds, capacity 100 left

    # This will fail — not enough capacity
    assert inventory.add_item_by("user1", "/sectionA/itemTiny", "100") == ""

    # user2 adds itemMed — this is distinct from previous itemMed
    assert inventory.add_item_by("user2", "/itemMed", "500") == "2000"

    # Fail — item already exists
    assert inventory.add_item_by("user1", "/sectionA/itemTiny", "100") == ""

    # Fail — user2 doesn’t have enough capacity for 2500
    assert inventory.add_item_by("user2", "/storage/itemHuge", "2500") == ""

    # Fail — user3 doesn’t exist
    assert inventory.add_item_by("user3", "/storage/itemHuge", "2500") == ""

    # Expand user1's capacity to 4000 — success
    assert inventory.update_capacity("user1", "4000") == "0"

    # Shrink user1’s capacity to 1000 — must delete 2 items
    assert inventory.update_capacity("user1", "1000") == "2"

    # Fail — user2 doesn’t exist (assumes deletion happened)
    assert inventory.update_capacity("user2", "5000") == ""


if __name__ == "__main__":
    print("Inventory Management")
    test_inventory_system_level1()

    test_inventory_system_level2()
    test_inventory_system_level3()
