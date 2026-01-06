import json
import os
import sys

"""
This is an inventory management system. It's simple and text-based, with the data being stored in a JSON file.
Features:
- Add, view, update, and remove items
- Search items by name
- Generate low-stock reports
- Safe loading and saving with corruption handling
"""
# Notes from banditdev: Could do with some comments to assist with maintainability but I do think we could work with what we have so far.
# Notes from Alexandru: Roger that!

DATA_FILE = "inventory.json"
"""
As the name suggests, load_data will load inventory data from DATA_FILE. If the file does not exist it will return an empty list
If the file exists but is invalid/corrupt, it would be backed up and a new inventory would start.
"""

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass

    try:
        os.rename(DATA_FILE, DATA_FILE + ".bak")
        print(f"Warning: {DATA_FILE} was invalid and was backed up to {DATA_FILE + '.bak'}. Starting fresh.")
    except Exception:
        print(f"Warning: {DATA_FILE} unreadable. Starting with empty inventory.")
    return []

"""
Below the inventory list will be saved to DATA_FILE in JSON format.
"""
def save_data(inventory):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error saving data:", e)
"""
All the print commands used to display the main menu options.
"""
def print_menu(): 
    print("\nInventory Management")
    print("--------------------")
    print("1) Add Item")
    print("2) View Stock")
    print("3) Update Item")
    print("4) Remove Item")
    print("5) Search by Name")
    print("6) Low-stock Report")
    print("7) Save")
    print("8) Save & Exit")
    print("9) Exit without Saving")
"""
Thus should ensure the input cannot be empty 
"""
def input_nonempty(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Input cannot be empty.")

"""
Finding the item based on ID, returns "none" if non-existent
"""
def find_by_id(inventory, item_id):
    for item in inventory:
        if item.get("id") == item_id:
            return item
    return None
"""
This section will generate a new numeric ID (as a string) based on existing IDs.
"""
def generate_unique_id(inventory):
    ids = []
    for it in inventory:
        try:
            ids.append(int(it.get("id")))
        except Exception:
            pass
    next_id = max(ids) + 1 if ids else 1
    return str(next_id)
"""
Adding a new item to the inventory and validating both the price and quantity.
"""
def add_item(inventory):
    print("\nAdd Item")
    print("Leave ID blank to auto-generate.")
    raw_id = input("ID: ").strip()
    if not raw_id:
        item_id = generate_unique_id(inventory)
    else:
        if find_by_id(inventory, raw_id):
            print("Error: An item with that ID already exists.")
            return
        item_id = raw_id

    name = input_nonempty("Name: ")
    """
    price
    """
    while True:
        p = input("Price: ").strip()
        try:
            price = float(p)
            if price < 0:
                print("Price must be non-negative.")
                continue
            break
        except Exception:
            print("Invalid price. Enter a number (e.g., 9.99).")
    """        
    quantity
    """
    while True:
        q = input("Quantity: ").strip()
        try:
            quantity = int(q)
            if quantity < 0:
                print("Quantity must be non-negative.")
                continue
            break
        except Exception:
            print("Invalid quantity. Enter an integer (e.g., 5).")

    inventory.append({"id": item_id, "name": name, "price": price, "quantity": quantity})
    print(f"Added item {item_id} - {name}.")

"""
This formats rows and headers into an aligned text table
"""
def format_table(rows, headers):
    cols = list(zip(*([headers] + rows))) if rows else [[h] for h in headers]
    widths = [max(len(str(x)) for x in col) for col in cols]

    sep = " | "
    line = "-+-".join("-" * w for w in widths)
    header_line = sep.join(str(h).ljust(w) for h, w in zip(headers, widths))

    out = header_line + "\n" + line + "\n"
    for r in rows:
        out += sep.join(str(c).ljust(w) for c, w in zip(r, widths)) + "\n"

    return out
"""
This displays all inventory items in a table
"""
def view_stock(inventory):
    if not inventory:
        print("\nInventory is empty.")
        return

    rows = []
    for it in inventory:
        rows.append([
            it.get("id"),
            it.get("name"),
            f"{it.get('price'):.2f}",
            it.get("quantity")
        ])

    print("\nCurrent Stock")
    print(format_table(rows, ["ID", "Name", "Price", "Quantity"]))

"""
This updates an existing inventory item by ID
"""
def update_item(inventory):
    if not inventory:
        print("\nInventory is empty.")
        return

    item_id = input_nonempty("Enter ID of item to update: ")
    item = find_by_id(inventory, item_id)

    if not item:
        print("Item not found.")
        return

    print(f"Updating {item_id} - {item['name']}. Leave blank to keep current value.")

    new_name = input(f"Name [{item['name']}]: ").strip()
    if new_name:
        item["name"] = new_name

    while True:
        new_price = input(f"Price [{item['price']:.2f}]: ").strip()
        if not new_price:
            break
        try:
            p = float(new_price)
            if p < 0:
                print("Price must be non-negative.")
                continue
            item["price"] = p
            break
        except Exception:
            print("Invalid price.")

    while True:
        new_q = input(f"Quantity [{item['quantity']}]: ").strip()
        if not new_q:
            break
        try:
            q = int(new_q)
            if q < 0:
                print("Quantity must be non-negative.")
                continue
            item["quantity"] = q
            break
        except Exception:
            print("Invalid quantity.")

    print("Item updated.")

"""
This removes an item from the inventory after confirmation
"""
def remove_item(inventory):
    if not inventory:
        print("\nInventory is empty.")
        return

    item_id = input_nonempty("Enter ID of item to remove: ")
    item = find_by_id(inventory, item_id)

    if not item:
        print("Item not found.")
        return

    confirm = input(
        f"Confirm delete {item_id} - {item['name']}? (y/N): "
    ).strip().lower()

    if confirm == "y":
        inventory.remove(item)
        print("Item removed.")
    else:
        print("Deletion cancelled.")

"""
This searches inventory items by name using a case-insensitive match
"""
def search_item(inventory):
    if not inventory:
        print("\nInventory is empty.")
        return

    term = input_nonempty("Search term: ").lower()
    results = []

    for it in inventory:
        if term in it.get("name", "").lower():
            results.append([
                it.get("id"),
                it.get("name"),
                f"{it.get('price'):.2f}",
                it.get("quantity")
            ])

    if not results:
        print("No matching items found.")
        return

    print(f"\nSearch results for '{term}':")
    print(format_table(results, ["ID", "Name", "Price", "Quantity"]))

"""
This generates a report of items below a specified quantity threshold
"""
def low_stock_report(inventory):
    if not inventory:
        print("\nInventory is empty.")
        return

    while True:
        t = input(
            "Report threshold (quantity < threshold, default 5): "
        ).strip()
        if not t:
            threshold = 5
            break
        try:
            threshold = int(t)
            break
        except Exception:
            print("Invalid number.")

    low = []
    for it in inventory:
        if int(it.get("quantity", 0)) < threshold:
            low.append([it.get("id"), it.get("name"), it.get("quantity")])

    if not low:
        print(f"No items below {threshold}.")
        return

    print(f"\nLow-stock items (quantity < {threshold}):")
    print(format_table(low, ["ID", "Name", "Quantity"]))

"""
This runs the main program loop and handles user input
"""
def main():
    inventory = load_data()
    print("Loaded", len(inventory), "items.")

    while True:
        try:
            print_menu()
            choice = input("Choose an option (1-9): ").strip()

            if choice == "1":
                add_item(inventory)
            elif choice == "2":
                view_stock(inventory)
            elif choice == "3":
                update_item(inventory)
            elif choice == "4":
                remove_item(inventory)
            elif choice == "5":
                search_item(inventory)
            elif choice == "6":
                low_stock_report(inventory)
            elif choice == "7":
                save_data(inventory)
                print("Saved.")
            elif choice == "8":
                save_data(inventory)
                print("Saved. Exiting.")
                break
            elif choice == "9":
                confirm = input("Exit without saving? (y/N): ").strip().lower()
                if confirm == "y":
                    print("Exiting without saving.")
                    break
                else:
                    print("Cancelled.")
            else:
                print("Invalid choice.")

        except KeyboardInterrupt:
            print("\nInterrupted. Use the menu to save and exit properly.")
        except Exception as e:
            print("An error occurred:", e)


# This ensures the program only runs when executed directly
if __name__ == "__main__":
    main()
