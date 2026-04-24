import sqlite3
import os
import sys

# ------------------ BASE PATH ------------------
def get_base_path():
    # If app is compiled (PyInstaller)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # If running normally
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

    # ITEMS TABLE
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

    # SALES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        total REAL
    )
    """)

    # SALE ITEMS TABLE
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buyers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT
    )
    """)


    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN buyer_id INTEGER")
    except:
        pass  # already exists

    conn.commit()
    conn.close()