from database import connect

def add_item():
    name = input("Item name: ").lower()

    conn = connect()
    cursor = conn.cursor()

    # check if item exists
    cursor.execute("SELECT id FROM items WHERE LOWER(name)=?", (name,))
    existing = cursor.fetchone()

    carton_price = float(input("Carton price: "))
    unit_price = float(input("Single item price: "))
    units_per_carton = int(input("Units per carton: "))
    stock_units = int(input("Add stock (in units): "))

    if existing:
        # update stock
        cursor.execute("""
            UPDATE items
            SET stock_units = stock_units + ?
            WHERE id = ?
        """, (stock_units, existing[0]))

        print("Stock updated for existing item!")

    else:
        cursor.execute("""
            INSERT INTO items (name, carton_price, unit_price, units_per_carton, stock_units)
            VALUES (?, ?, ?, ?, ?)
        """, (name, carton_price, unit_price, units_per_carton, stock_units))

        print("New item added!")

    conn.commit()
    conn.close()


def view_items():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, carton_price, unit_price, units_per_carton, stock_units
        FROM items
    """)

    items = cursor.fetchall()
    conn.close()

    print("\n--- STOCK ---")

    for item in items:
        item_id, name, cp, up, upc, stock = item

        cartons = stock // upc
        units = stock % upc

        print(f"""
ID: {item_id}
Name: {name}
Carton Price: {cp}
Unit Price: {up}
Stock: {cartons} carton(s) + {units} unit(s)
-------------------------
""")
        
def search_item(keyword):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name FROM items
        WHERE name LIKE ?
    """, ('%' + keyword + '%',))

    results = cursor.fetchall()
    conn.close()

    return results

def remove_stock():
    from database import connect

    conn = connect()
    cursor = conn.cursor()

    keyword = input("\nSearch item to remove stock: ")

    cursor.execute("""
        SELECT id, name, units_per_carton, stock_units
        FROM items
        WHERE name LIKE ?
    """, ('%' + keyword + '%',))

    results = cursor.fetchall()

    if not results:
        print("No items found!")
        return

    print("\nMatches:")
    for i, item in enumerate(results):
        print(f"{i+1}. {item[1]} (Stock: {item[3]} units)")

    try:
        choice = int(input("Select item number: ")) - 1
        item_id, name, upc, stock = results[choice]
    except:
        print("Invalid choice!")
        return

    qty = int(input("Quantity to remove: "))
    remove_type = input("Type (carton/unit): ").lower()

    if remove_type == "carton":
        remove_units = qty * upc
    elif remove_type == "unit":
        remove_units = qty
    else:
        print("Invalid type!")
        return

    if remove_units > stock:
        print("❌ Cannot remove more than available stock!")
        return

    cursor.execute("""
        UPDATE items
        SET stock_units = stock_units - ?
        WHERE id=?
    """, (remove_units, item_id))

    conn.commit()
    conn.close()

    print(f"✅ Stock updated! Removed from {name}")

def reset_data():
    from database import connect

    print("\n⚠️ RESET OPTIONS")
    print("1. Reset Stock (set to 0)")
    print("2. Delete Sales History")
    print("3. FULL RESET (Everything)")
    print("4. Cancel")

    choice = input("Choose option: ")

    confirm = input("Type 'YES' to confirm: ")
    if confirm != "YES":
        print("Cancelled!")
        return

    conn = connect()
    cursor = conn.cursor()

    if choice == "1":
        cursor.execute("UPDATE items SET stock_units = 0")
        print("✅ All stock reset to 0")

    elif choice == "2":
        cursor.execute("DELETE FROM sale_items")
        cursor.execute("DELETE FROM sales")
        print("✅ Sales history deleted")

    elif choice == "3":
        cursor.execute("DELETE FROM sale_items")
        cursor.execute("DELETE FROM sales")
        cursor.execute("DELETE FROM items")
        print("🔥 FULL RESET DONE")

    else:
        print("Cancelled")
        return

    conn.commit()
    conn.close()