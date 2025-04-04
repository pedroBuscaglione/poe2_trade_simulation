# inventory_db.py
import sqlite3

DB_NAME = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_item(item_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO inventory (item_name) VALUES (?)", (item_name,))
    conn.commit()
    conn.close()

def get_all_items():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT item_name FROM inventory")
    items = [row[0] for row in c.fetchall()]
    conn.close()
    return items

def remove_item_by_index(index):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Get the rowid of the item at that index
    c.execute("SELECT rowid FROM inventory LIMIT 1 OFFSET ?", (index,))
    result = c.fetchone()

    if result:
        rowid = result[0]
        c.execute("DELETE FROM inventory WHERE rowid = ?", (rowid,))
        conn.commit()

    conn.close()

