import sys
import random
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QMessageBox, QLineEdit
)

API_URL = "http://127.0.0.1:8000/api/items/"  # Django API URL

class TradeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PoE Trade Simulator")
        self.setGeometry(100, 100, 400, 500)

        self.item_pool = [
            "Chaos Orb", "Exalted Orb", "Divine Orb", "Mirror of Kalandra",
            "Tabula Rasa", "Kaom's Heart", "Headhunter", "Berek's Grip"
        ]

        self.inventory = self.fetch_inventory()  # Fetch items first!

        layout = QVBoxLayout()

        self.label = QLabel("Click to generate a new item!", self)
        layout.addWidget(self.label)

        self.button = QPushButton("Generate Random Item", self)
        self.button.clicked.connect(self.generate_item)
        layout.addWidget(self.button)

        self.inventory_label = QLabel("Inventory:", self)
        layout.addWidget(self.inventory_label)

        self.inventory_list = QListWidget(self)
        layout.addWidget(self.inventory_list)

        self.delete_button = QPushButton("Remove Selected Item", self)
        self.delete_button.clicked.connect(self.remove_selected_item)
        layout.addWidget(self.delete_button)

        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Filter items...")
        self.filter_input.textChanged.connect(self.filter_inventory)
        layout.addWidget(self.filter_input)

        self.setLayout(layout)

        # Call update after setting inventory
        self.update_inventory_display()

    def fetch_inventory(self):
        """Fetch items from Django API and store their details."""
        try:
            response = requests.get(API_URL)
            print("API Response Status:", response.status_code)  # Debug
            print("API Response Data:", response.text)  # Debug
            
            if response.status_code == 200:
                items = response.json()
                return [
                    {
                        "name": item["name"],
                        "rarity": item["rarity"],
                        "quantity": item["quantity"]
                    }
                    for item in items
                ]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching inventory: {e}")
        return []

    def generate_item(self):
        """Generate a random item with rarity and quantity, then send it to the API."""
        item_name = random.choice(self.item_pool)
        rarities = ["Common", "Magic", "Rare", "Unique"]
        rarity = random.choice(rarities)
        quantity = random.randint(1, 10)  # Stackable items

        data = {"name": item_name, "rarity": rarity, "quantity": quantity}

        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 201:
                self.inventory.append(data)
                self.update_inventory_display()
                self.label.setText(f"Generated: {item_name}")
                self.show_popup(f"You found: {item_name} ({rarity}) x{quantity}!")
        except requests.exceptions.RequestException as e:
            print(f"Error adding item: {e}")

    def update_inventory_display(self, filtered_items=None):
        """Updates the inventory UI list with item details."""
        self.inventory_list.clear()
        
        items_to_show = filtered_items if filtered_items is not None else self.inventory

        if not items_to_show:
            self.inventory_list.addItem("No items available")  # Show placeholder text
            return

        for item in items_to_show:
            display_text = f"{item['name']} - {item['rarity']} (x{item['quantity']})"
            self.inventory_list.addItem(display_text)

    def remove_selected_item(self):
        """Reduce item quantity or remove from inventory via API."""
        selected_index = self.inventory_list.currentRow()
        if selected_index == -1:
            self.show_popup("No item selected!")
            return

        item = self.inventory[selected_index]  # Get selected item
        item_name = item["name"]

        print(f"Selected item to remove: {item_name}")  # Debugging

        try:
            response = requests.get(API_URL)
            print("Fetching current inventory from API...")  # Debugging
            if response.status_code == 200:
                items = response.json()
                print(f"Current API Inventory: {items}")  # Debugging
                for api_item in items:
                    if api_item["name"] == item_name:
                        item_id = api_item["id"]

                        # If more than 1 quantity, update instead of deleting
                        if api_item["quantity"] > 1:
                            updated_data = {
                                "name": api_item["name"],
                                "rarity": api_item["rarity"],
                                "quantity": api_item["quantity"] - 1
                            }
                            print(f"Updating quantity of {item_name} to {api_item['quantity'] - 1}")  # Debugging
                            update_response = requests.put(f"{API_URL}{item_id}/", json=updated_data)
                            print(f"PUT Response Code: {update_response.status_code}")  # Debugging
                            print(f"PUT Response Data: {update_response.text}")  # Debugging
                            if update_response.status_code == 200:
                                self.inventory[selected_index]["quantity"] -= 1
                        else:
                            print(f"Deleting item {item_name}")  # Debugging
                            delete_response = requests.delete(f"{API_URL}{item_id}/")
                            print(f"DELETE Response Code: {delete_response.status_code}")  # Debugging
                            if delete_response.status_code == 204:
                                self.inventory.pop(selected_index)

                        self.update_inventory_display()
                        self.show_popup(f"Updated Inventory: {item_name}")
                        break

        except requests.exceptions.RequestException as e:
            print(f"Error updating/removing item: {e}")


    def filter_inventory(self):
        """Filters inventory based on search input."""
        search_text = self.filter_input.text().lower()
        filtered_items = [item for item in self.inventory if search_text in item.lower()]
        self.update_inventory_display(filtered_items)

    def show_popup(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Notification")
        msg.setText(message)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradeApp()
    window.show()
    sys.exit(app.exec_())
