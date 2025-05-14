import sys
import random
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QMessageBox, QLineEdit, QHBoxLayout
)

API_URL = "http://127.0.0.1:8000"  # Django API URL
USERNAME = "Glione"
PASSWORD = "Pe2005dro!@#"


def is_server_online():
    try:
        response = requests.get("http://127.0.0.1:8000")
        return response.status_code == 200
    except:
        return False

if not is_server_online():
    print("⚠️ O servidor Django não está online. Execute `python manage.py runserver` e tente novamente.")
    exit()

class TradeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.token = self.get_token() 
        self.inventory = self.fetch_inventory()  # Fetch items first!
        self.init_ui()  
        self.load_inventory()  # Load inventory after fetching

    def init_ui(self):
        self.setWindowTitle("Trade Simulator - Inventário")
        self.setGeometry(100, 100, 600, 400)

        # Layouts principais
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # Campo de busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar item...")
        self.search_input.textChanged.connect(self.filter_inventory)

        # Botões
        self.generate_button = QPushButton("Gerar Item Aleatório")
        self.generate_button.clicked.connect(self.generate_item)

        self.remove_button = QPushButton("Remover Item Selecionado")
        self.remove_button.clicked.connect(self.remove_selected_item)

        # Lista de inventário
        self.inventory_list = QListWidget()

        # Montagem do layout
        top_layout.addWidget(QLabel("Buscar:"))
        top_layout.addWidget(self.search_input)

        bottom_layout.addWidget(self.generate_button)
        bottom_layout.addWidget(self.remove_button)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.inventory_list)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def get_token(self):
        url = f"{API_URL}/api-token-auth/"
        data = {
            "username": USERNAME,
            "password": PASSWORD
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("🔐 Token obtido com sucesso.")
                return response.json()['token']
            else:
                print("Erro ao obter token:", response.status_code, response.text)
                return None
        except requests.exceptions.RequestException as e:
            print("Erro de conexão ao obter token:", e)
            return None

    def fetch_inventory(self):
        try:
            headers = {"Authorization": f"Token {self.token}"} if self.token else {}
            response = requests.get(f"{API_URL}/api/items/", headers=headers)
            print("Status:", response.status_code)
            print("Dados:", response.json())

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
        print("🛠️ Gerando item aleatório...")
        # Monta o novo item
        self.item_pool = ["Sword", "Wand", "Bow", "Staff"] 
        item_name = random.choice(self.item_pool)
        rarities = ["Common", "Magic", "Rare", "Unique"]
        rarity = random.choice(rarities)
        quantity = random.randint(1, 10)

        data = {"name": item_name, "rarity": rarity, "quantity": quantity}
        headers = {"Authorization": f"Token {self.token}"} if self.token else {}

        try:
            response = requests.post(f"{API_URL}/api/items/", json=data, headers=headers)
            print("Status:", response.status_code, "Resposta:", response.text)

            if response.status_code == 201:
                print("✅ Item criado com sucesso!")

                # Verifica se já existe no inventário local
                for inv in self.inventory:
                    if inv["name"] == item_name and inv["rarity"] == rarity:
                        inv["quantity"] += quantity
                        break
                else:
                    # não achou, adiciona
                    self.inventory.append({
                        "name": item_name,
                        "rarity": rarity,
                        "quantity": quantity
                    })

                self.update_inventory_display()
                self.label.setText(f"Generated: {item_name}")
                self.show_popup(f"You found: {item_name} ({rarity}) x{quantity}!")
            else:
                print("❌ Erro ao criar item:", response.status_code)
        except Exception as e:
            print("Erro ao enviar item:", e)

    def load_inventory(self):
        self.inventory = self.fetch_inventory()
        self.update_inventory_display()

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
            headers = {"Authorization": f"Token {self.token}"} if self.token else {}
            response = requests.get(f"{API_URL}/api/items/", headers=headers)
            print("Fetching current inventory from API...")  # Debugging

            if response.status_code == 200:
                items = response.json()
                print(f"Current API Inventory: {items}")  # Debugging

                for api_item in items:
                    if api_item["name"] == item_name:
                        item_id = api_item["id"]

                        # If more than 1 quantity, update via POST request
                        if api_item["quantity"] > 1:
                            new_quantity = api_item["quantity"] - 1
                            update_response = requests.post(
                                f"{API_URL}/api/items/{item_id}/update_quantity/",
                                json={"quantity": new_quantity},
                                headers=headers
                            )

                            print(f"POST Response Code: {update_response.status_code}")  # Debugging
                            print(f"POST Response Data: {update_response.text}")  # Debugging

                            if update_response.status_code == 200:
                                self.inventory[selected_index]["quantity"] -= 1
                            else:
                                print("Error updating item in API")

                        else:
                            # Delete if quantity reaches 0
                            print(f"Deleting item {item_name}")  # Debugging
                            delete_response = requests.delete(
                                f"{API_URL}/api/items/{item_id}/",
                                headers=headers
                            )
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
        filtered_items = [
            item for item in self.inventory
            if search_text in item["name"].lower()
        ]
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
