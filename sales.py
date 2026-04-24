from database import connect
from datetime import datetime
from inventory import search_item


def make_sale():
    cart = []

    while True:
        # 🔍 SEARCH ITEM
        keyword = input("\nSearch item name: ")
        results = search_item(keyword)

        if not results:
            print("No items found!")
            continue

        # SHOW MATCHES
        print("\nMatches:")
        for i, item in enumerate(results):
            print(f"{i+1}. {item[1]} (ID: {item[0]})")

        # SELECT ITEM
        try:
            choice = int(input("Select item number: ")) - 1
            item_id = results[choice][0]
        except:
            print("Invalid selection!")
            continue

        # QUANTITY + TYPE
        try:
            qty = int(input("Quantity: "))
        except:
            print("Invalid quantity!")
            continue

        sale_type = input("Type (carton/unit): ").lower()

        if sale_type not in ["carton", "unit"]:
            print("Invalid type! Use 'carton' or 'unit'")
            continue

        cart.append((item_id, qty, sale_type))

        more = input("Add more items? (y/n): ")
        if more != 'y':
            break

    # 🧮 PROCESS SALE
    conn = connect()
    cursor = conn.cursor()

    total = 0

    # CHECK STOCK + CALCULATE TOTAL
    for item_id, qty, sale_type in cart:
        cursor.execute("""
            SELECT name, carton_price, unit_price, units_per_carton, stock_units
            FROM items WHERE id=?
        """, (item_id,))

        item = cursor.fetchone()

        if not item:
            print("Item not found!")
            return None

        name, cp, up, upc, stock = item

        if sale_type == "carton":
            needed_units = qty * upc
            price = cp * qty
        else:
            needed_units = qty
            price = up * qty

        if stock < needed_units:
            print(f"Not enough stock for {name}!")
            return None

        total += price

    # 💾 SAVE SALE
    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO sales (date, total) VALUES (?, ?)", (date, total))
    sale_id = cursor.lastrowid

    # 📉 UPDATE STOCK + SAVE ITEMS
    for item_id, qty, sale_type in cart:
        cursor.execute("""
            SELECT carton_price, unit_price, units_per_carton
            FROM items WHERE id=?
        """, (item_id,))

        cp, up, upc = cursor.fetchone()

        if sale_type == "carton":
            used_units = qty * upc
            price = cp
        else:
            used_units = qty
            price = up

        cursor.execute("""
            INSERT INTO sale_items (sale_id, item_id, quantity, type, price)
            VALUES (?, ?, ?, ?, ?)
        """, (sale_id, item_id, qty, sale_type, price))

        cursor.execute("""
            UPDATE items
            SET stock_units = stock_units - ?
            WHERE id=?
        """, (used_units, item_id))

    conn.commit()
    conn.close()

    print("\n✅ Sale completed!")
    print("Total amount:", total)

    return sale_id


def view_sales():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, date, total FROM sales ORDER BY id DESC")
    sales = cursor.fetchall()

    conn.close()

    print("\n--- SALES HISTORY ---")

    if not sales:
        print("No sales yet!")
        return

    for sale in sales:
        print(f"""
Sale ID: {sale[0]}
Date: {sale[1]}
Total: {sale[2]}
-----------------------
""")
        
def view_sale_details():
    sale_id = input("Enter Sale ID: ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT date, total FROM sales WHERE id=?", (sale_id,))
    sale = cursor.fetchone()

    if not sale:
        print("Sale not found!")
        return

    print(f"\nDate: {sale[0]}")
    print(f"Total: {sale[1]}")

    cursor.execute("""
        SELECT items.name, sale_items.quantity, sale_items.type, sale_items.price
        FROM sale_items
        JOIN items ON items.id = sale_items.item_id
        WHERE sale_items.sale_id=?
    """, (sale_id,))

    print("\nItems:")
    for item in cursor.fetchall():
        print(f"{item[0]} ({item[2]}) x{item[1]} = {item[1]*item[3]}")

    conn.close()