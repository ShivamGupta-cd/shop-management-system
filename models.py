from database import connect

def add_item(name, price, stock):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO items (name, price, stock) VALUES (?, ?, ?)",
        (name, price, stock)
    )

    conn.commit()
    conn.close()


def view_items():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    conn.close()
    return items