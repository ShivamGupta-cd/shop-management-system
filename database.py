import sqlite3
import os
import sys

# ------------------ BASE PATH ------------------
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()

# ------------------ DB PATH ------------------
DB_FOLDER = os.path.join(BASE_DIR, "db")
os.makedirs(DB_FOLDER, exist_ok=True)

DB_PATH = os.path.join(DB_FOLDER, "shop.db")


# ------------------ CONNECT ------------------
def connect():
    return sqlite3.connect(DB_PATH)


# ------------------ SETUP DATABASE ------------------
def setup_database():
    conn = connect()
    cursor = conn.cursor()

    # ---------------- ITEMS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        carton_price REAL,
        unit_price REAL,
        units_per_carton INTEGER,
        stock_units INTEGER
    )
    """)

    # ✅ SAFE COLUMN ADDS
    for col, query in [
        ("buy_price", "ALTER TABLE items ADD COLUMN buy_price REAL DEFAULT 0"),
        ("mrp", "ALTER TABLE items ADD COLUMN mrp REAL DEFAULT 0"),
    ]:
        try:
            cursor.execute(query)
        except:
            pass

    # ---------------- SALES TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        total REAL
    )
    """)

    # ✅ BUYER LINK
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN buyer_id INTEGER")
    except:
        pass

    # ---------------- SALE ITEMS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        type TEXT,
        price REAL
    )
    """)

    # ✅ IMPORTANT FOR PROFIT + DISCOUNT
    for col, query in [
        ("buy_price", "ALTER TABLE sale_items ADD COLUMN buy_price REAL"),
        ("discount", "ALTER TABLE sale_items ADD COLUMN discount REAL DEFAULT 0"),
    ]:
        try:
            cursor.execute(query)
        except:
            pass

    # ---------------- BUYERS TABLE ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buyers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT
    )
    """)


def fix_old_buy_price():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE sale_items
    SET buy_price = (
        SELECT buy_price FROM items WHERE items.id = sale_items.item_id
    )
    WHERE buy_price IS NULL OR buy_price = 0
    """)

    conn.commit()
    conn.close()
