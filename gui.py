import tkinter as tk
from tkinter import messagebox
from database import connect
from invoice import generate_invoice
from datetime import datetime
from database import setup_database
setup_database()
# ------------------ STYLING ------------------
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_NORMAL = ("Segoe UI", 10)

PRIMARY = "#2E86C1"
SUCCESS = "#27AE60"
DANGER = "#E74C3C"
LIGHT_BG = "#F4F6F7"

# ------------------ ADD ITEM ------------------
def add_item_gui():
    win = tk.Toplevel(root)
    win.title("Add Item")
    win.geometry("520x400")

    # ---------------- FORM ----------------
    form_frame = tk.LabelFrame(win, text="Item Details", padx=10, pady=10)
    form_frame.pack(fill="x", padx=10, pady=10)

    # Row 0
    tk.Label(form_frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Row 1
    tk.Label(form_frame, text="Carton Price").grid(row=1, column=0, padx=5, pady=5)
    cp_entry = tk.Entry(form_frame)
    cp_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Unit Price").grid(row=1, column=2, padx=5, pady=5)
    up_entry = tk.Entry(form_frame)
    up_entry.grid(row=1, column=3, padx=5, pady=5)

    # Row 2
    tk.Label(form_frame, text="MRP").grid(row=2, column=0, padx=5, pady=5)
    mrp_entry = tk.Entry(form_frame)
    mrp_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Units/Carton").grid(row=2, column=2, padx=5, pady=5)
    upc_entry = tk.Entry(form_frame)
    upc_entry.grid(row=2, column=3, padx=5, pady=5)

    # Row 3
    tk.Label(form_frame, text="Cartons").grid(row=3, column=0, padx=5, pady=5)
    carton_entry = tk.Entry(form_frame, width=8)
    carton_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Extra Units").grid(row=3, column=2, padx=5, pady=5)
    unit_entry = tk.Entry(form_frame, width=8)
    unit_entry.grid(row=3, column=3, padx=5, pady=5)

    # ---------------- LIVE STOCK PREVIEW ----------------
    preview_label = tk.Label(win, text="Total Units: 0", font=("Arial", 11, "bold"))
    preview_label.pack(pady=5)

    def update_preview(event=None):
        try:
            cartons = int(carton_entry.get() or 0)
            units = int(unit_entry.get() or 0)
            upc = int(upc_entry.get() or 0)
            total = cartons * upc + units
        except:
            total = 0

        preview_label.config(text=f"Total Units: {total}")

    carton_entry.bind("<KeyRelease>", update_preview)
    unit_entry.bind("<KeyRelease>", update_preview)
    upc_entry.bind("<KeyRelease>", update_preview)

    # ---------------- SAVE FUNCTION ----------------
    def save(event=None):
        name = name_entry.get().strip().lower()

        if not name:
            messagebox.showerror("Error", "Name required")
            return

        try:
            cp = float(cp_entry.get())
            up = float(up_entry.get())
            mrp = float(mrp_entry.get())
            upc = int(upc_entry.get())

            cartons = int(carton_entry.get() or 0)
            extra_units = int(unit_entry.get() or 0)

        except:
            messagebox.showerror("Error", "Invalid input!")
            return

        stock = (cartons * upc) + extra_units

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM items WHERE LOWER(name)=?", (name,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE items
                SET carton_price=?, unit_price=?, mrp=?, units_per_carton=?, stock_units=stock_units+?
                WHERE id=?
            """, (cp, up, mrp, upc, stock, existing[0]))

            messagebox.showinfo("Updated", "Item updated!")

        else:
            cursor.execute("""
                INSERT INTO items (name, carton_price, unit_price, mrp, units_per_carton, stock_units)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, cp, up, mrp, upc, stock))

            messagebox.showinfo("Success", "New item added!")

        conn.commit()
        conn.close()

        # clear fields
        for e in [name_entry, cp_entry, up_entry, mrp_entry, upc_entry, carton_entry, unit_entry]:
            e.delete(0, tk.END)

        preview_label.config(text="Total Units: 0")
        name_entry.focus_set()

    # ---------------- BUTTON ----------------
    tk.Button(
        win,
        text="✔ Save Item",
        bg=SUCCESS,
        fg="white",
        font=FONT_HEADER,
        command=save
    ).pack(pady=10)

    # ---------------- KEYBOARD FLOW ----------------
    entries = [name_entry, cp_entry, up_entry, mrp_entry, upc_entry, carton_entry, unit_entry]

    for i in range(len(entries) - 1):
        entries[i].bind("<Return>", lambda e, idx=i: entries[idx + 1].focus_set())

    entries[-1].bind("<Return>", save)

    name_entry.focus_set()

# ------------------ VIEW STOCK ------------------
def view_stock_gui():
    win = tk.Toplevel(root)
    win.title("View Stock")
    win.geometry("1500x700")

    # ---------------- SEARCH ----------------
    tk.Label(win, text="Search Item").pack()
    search_entry = tk.Entry(win)
    search_entry.pack(fill="x")

    # ---------------- TABLE ----------------
    from tkinter import ttk

    columns = (
        "ID",
        "Name",
        "Units/Carton",
        "Cartons",
        "Units",
        "MRP",
        "Carton Price",
        "Unit Price"
    )

    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.pack(fill="both", expand=True)

    # ---------------- LOAD DATA ----------------
    def load_data(search_text=""):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, stock_units, units_per_carton, mrp, carton_price, unit_price
            FROM items
            WHERE name LIKE ?
        """, ('%' + search_text + '%',))

        tree.delete(*tree.get_children())

        for row in cursor.fetchall():
            item_id, name, stock, upc, mrp, cp, up = row

            cartons = stock // upc if upc else 0
            units = stock % upc if upc else stock

            item = tree.insert("", "end", values=(
                item_id,
                name.capitalize(),
                upc,
                cartons,
                units,
                f"{mrp:.2f}",
                f"{cp:.2f}",
                f"{up:.2f}"
            ))

            # 🔥 LOW STOCK LOGIC
            if cartons == 0 and units < 5:
                tree.item(item, tags=("low",))

        conn.close()

    # ---------------- SEARCH EVENT ----------------
    def search(event=None):
        load_data(search_entry.get())

    search_entry.bind("<KeyRelease>", search)

    # ---------------- KEYBOARD NAV ----------------
    search_entry.bind("<Down>", lambda e: tree.focus_set())

    def focus_first(event=None):
        items = tree.get_children()
        if items:
            tree.focus(items[0])
            tree.selection_set(items[0])

    tree.bind("<Return>", focus_first)

    # ---------------- INITIAL LOAD ----------------
    load_data()
    search_entry.focus_set()


# ------------------ ADD STOCK ------------------
def add_stock_gui():
    win = tk.Toplevel(root)
    win.title("Add Stock")
    win.geometry("500x400")

    # ---------------- SEARCH ----------------
    tk.Label(win, text="Search Item").pack(pady=5)

    search_entry = tk.Entry(win)
    search_entry.pack(fill="x", padx=10)

    result_list = tk.Listbox(win, height=6)
    result_list.pack(fill="x", padx=10, pady=5)

    # ---------------- INPUT ----------------
    input_frame = tk.LabelFrame(win, text="Stock Details", padx=10, pady=10)
    input_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(input_frame, text="Quantity").grid(row=0, column=0, padx=5, pady=5)
    qty_entry = tk.Entry(input_frame, width=10)
    qty_entry.grid(row=0, column=1, padx=5, pady=5)
    qty_entry.insert(0, "1")

    type_var = tk.StringVar(value="unit")

    tk.Radiobutton(input_frame, text="Unit", variable=type_var, value="unit")\
        .grid(row=0, column=2, padx=5)

    tk.Radiobutton(input_frame, text="Carton", variable=type_var, value="carton")\
        .grid(row=0, column=3, padx=5)

    # ---------------- SEARCH FUNCTION ----------------
    def search(event=None):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name FROM items WHERE name LIKE ?",
            ('%' + search_entry.get() + '%',)
        )

        result_list.delete(0, tk.END)

        for r in cursor.fetchall():
            result_list.insert(tk.END, f"{r[0]} - {r[1]}")

        conn.close()

        if result_list.size() > 0:
            result_list.selection_set(0)
            result_list.activate(0)

    # ---------------- ADD STOCK ----------------
    def add_stock():
        selected = result_list.get(tk.ACTIVE)
        if not selected:
            messagebox.showerror("Error", "Select item")
            return

        try:
            item_id = int(selected.split(" - ")[0])
            qty = int(qty_entry.get())
        except:
            messagebox.showerror("Error", "Invalid input")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT units_per_carton FROM items WHERE id=?", (item_id,))
        upc = cursor.fetchone()[0]

        added = qty * upc if type_var.get() == "carton" else qty

        cursor.execute(
            "UPDATE items SET stock_units=stock_units+? WHERE id=?",
            (added, item_id)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Done", "Stock added!")

        # reset
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, "1")
        search_entry.delete(0, tk.END)
        result_list.delete(0, tk.END)

        search_entry.focus_set()

    # ---------------- BUTTON ----------------
    tk.Button(
        win,
        text="Add Stock",
        bg=SUCCESS,
        fg="white",
        font=FONT_HEADER,
        command=add_stock
    ).pack(pady=10)

    # ---------------- KEYBOARD ----------------
    search_entry.bind("<KeyRelease>", search)
    result_list.bind("<Return>", lambda e: qty_entry.focus_set())
    qty_entry.bind("<Return>", lambda e: add_stock())

    search_entry.focus_set()


# ------------------ SALES ------------------
def make_sale_gui():
    win = tk.Toplevel(root)
    win.title("Billing")
    win.geometry("850x850")

    cart = {}

    # ---------------- BUYER ----------------
    buyer_frame = tk.LabelFrame(win, text="Buyer Details", padx=10, pady=10)
    tk.Label(buyer_frame, text="Search Buyer").grid(row=2, column=0)

    buyer_search = tk.Entry(buyer_frame)
    buyer_search.grid(row=2, column=1)

    buyer_list = tk.Listbox(buyer_frame, height=4)
    buyer_list.grid(row=3, column=0, columnspan=4, sticky="ew")
    buyer_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(buyer_frame, text="Name").grid(row=0, column=0)
    buyer_name_entry = tk.Entry(buyer_frame)
    buyer_name_entry.grid(row=0, column=1)

    tk.Label(buyer_frame, text="Phone").grid(row=0, column=2)
    buyer_phone_entry = tk.Entry(buyer_frame)
    buyer_phone_entry.grid(row=0, column=3)

    tk.Label(buyer_frame, text="GST %").grid(row=1, column=0)
    gst_entry = tk.Entry(buyer_frame)
    gst_entry.grid(row=1, column=1)

    # ---------------- SEARCH ----------------
    search_frame = tk.LabelFrame(win, text="Add Item", padx=10, pady=10)
    search_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(search_frame, text="Search").grid(row=0, column=0)
    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    tk.Label(search_frame, text="Qty").grid(row=0, column=2)
    qty_entry = tk.Entry(search_frame, width=5)
    qty_entry.grid(row=0, column=3)
    qty_entry.insert(0, "1")

    type_var = tk.StringVar(value="carton")
    tk.Radiobutton(search_frame, text="Carton", variable=type_var, value="carton").grid(row=0, column=4)
    tk.Radiobutton(search_frame, text="Unit", variable=type_var, value="unit").grid(row=0, column=5)

    tk.Label(search_frame, text="Disc ₹").grid(row=0, column=6)
    discount_entry = tk.Entry(search_frame, width=6)
    discount_entry.grid(row=0, column=7)
    discount_entry.insert(0, "0")

    result_list = tk.Listbox(search_frame, height=6)
    result_list.grid(row=1, column=0, columnspan=8, sticky="ew")

    # ---------------- CART ----------------
    from tkinter import ttk

    cart_frame = tk.Frame(win)
    cart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_frame = tk.LabelFrame(cart_frame, text="Cart")
    left_frame.pack(side="left", fill="both", expand=True)

    columns = ("Item", "Type", "Qty", "Price", "Total")
    cart_table = ttk.Treeview(left_frame, columns=columns, show="headings")

    for col in columns:
        cart_table.heading(col, text=col)
        cart_table.column(col, anchor="center")

    cart_table.pack(fill="both", expand=True)

    # ---------------- SUMMARY ----------------
    right_frame = tk.LabelFrame(cart_frame, text="Summary")
    right_frame.pack(side="right", fill="y")

    total_label = tk.Label(right_frame, text="Subtotal: 0")
    total_label.pack(anchor="w")

    gst_label = tk.Label(right_frame, text="GST: 0")
    gst_label.pack(anchor="w")

    final_label = tk.Label(right_frame, text="Final: 0", font=("Arial", 12, "bold"), fg="green")
    final_label.pack(anchor="w")


    def search_buyer(event=None):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name, phone FROM buyers WHERE name LIKE ?",
            ('%' + buyer_search.get() + '%',)
        )

        buyer_list.delete(0, tk.END)

        for b in cursor.fetchall():
            buyer_list.insert(tk.END, f"{b[0]} - {b[1]} ({b[2]})")

        conn.close()

        if buyer_list.size() > 0:
            buyer_list.selection_clear(0, tk.END)
            buyer_list.selection_set(0)
            buyer_list.activate(0)

    def fill_buyer(event=None):
        selected = buyer_list.get(tk.ACTIVE)
        if not selected:
            return

        parts = selected.split(" - ")[1]
        name = parts.split(" (")[0]
        phone = parts.split("(")[1].replace(")", "")

        buyer_name_entry.delete(0, tk.END)
        buyer_name_entry.insert(0, name)

        buyer_phone_entry.delete(0, tk.END)
        buyer_phone_entry.insert(0, phone)


    # ---------------- SEARCH FUNCTION ----------------
    def search(event=None):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, stock_units, units_per_carton
            FROM items WHERE name LIKE ?
        """, ('%' + search_entry.get() + '%',))

        result_list.delete(0, tk.END)

        for r in cursor.fetchall():
            cartons = r[2] // r[3] if r[3] else 0
            units = r[2] % r[3] if r[3] else r[2]
            result_list.insert(tk.END, f"{r[0]} - {r[1]} ({cartons}C {units}U)")

        conn.close()

        if result_list.size() > 0:
            result_list.selection_set(0)

    # ---------------- REFRESH CART ----------------
    def refresh_cart():
        cart_table.delete(*cart_table.get_children())

        subtotal = 0

        for item in cart.values():
            total = (item["qty"] * item["price"]) - item["discount"]
            subtotal += total

            cart_table.insert("", "end", values=(
                item["name"],
                "C" if item["type"] == "carton" else "U",
                item["qty"],
                f"{item['price']:.2f}",
                f"{total:.2f}"
            ))

        try:
            gst_percent = float(gst_entry.get())
        except:
            gst_percent = 0

        gst_amt = subtotal * gst_percent / 100
        final = subtotal + gst_amt

        total_label.config(text=f"Subtotal: {subtotal:.2f}")
        gst_label.config(text=f"GST: {gst_amt:.2f}")
        final_label.config(text=f"Final: {final:.2f}")

    # ---------------- ADD TO CART ----------------
    def add_to_cart(event=None):
        selected = result_list.get(tk.ACTIVE)
        if not selected:
            return

        try:
            qty = int(qty_entry.get())
            discount = float(discount_entry.get() or 0)
        except:
            messagebox.showerror("Error", "Invalid input")
            return

        item_id = int(selected.split(" - ")[0])

        conn = connect()
        cursor = conn.cursor()

        # ✅ ADD MRP HERE
        cursor.execute("""
            SELECT name, carton_price, unit_price, mrp, units_per_carton, stock_units
            FROM items WHERE id=?
        """, (item_id,))

        data = cursor.fetchone()
        conn.close()

        if not data:
            return

        # ✅ unpack with MRP
        name, cp, up, mrp, upc, stock = data

        sale_type = type_var.get()
        price = cp if sale_type == "carton" else up

        needed = qty * upc if sale_type == "carton" else qty

        if stock < needed:
            messagebox.showerror("Stock Error", "Not enough stock!")
            return

        # ✅ STORE MRP IN CART
        if item_id in cart and cart[item_id]["type"] == sale_type:
            cart[item_id]["qty"] += qty
            cart[item_id]["discount"] += discount
        else:
            cart[item_id] = {
                "name": name,
                "qty": qty,
                "type": sale_type,
                "price": price,
                "mrp": mrp,          # 👈 THIS WAS MISSING
                "upc": upc,
                "discount": discount
            }

        # RESET
        qty_entry.delete(0, tk.END)
        qty_entry.insert(0, "1")

        discount_entry.delete(0, tk.END)
        discount_entry.insert(0, "0")

        search_entry.delete(0, tk.END)

        refresh_cart()
        search_entry.focus_set()

    # ---------------- REMOVE ----------------
    def remove_item():
        selected = cart_table.selection()
        if not selected:
            return

        index = cart_table.index(selected[0])
        key = list(cart.keys())[index]

        del cart[key]
        refresh_cart()

    def clear_cart():
        cart.clear()
        refresh_cart()

    # ---------------- CHECKOUT ----------------
    def checkout(do_print):
        try:
            if not cart:
                messagebox.showerror("Error", "Cart empty")
                return

            # ---------------- CALCULATE TOTAL ----------------
            subtotal = sum((i["qty"] * i["price"]) - i["discount"] for i in cart.values())

            try:
                gst_percent = float(gst_entry.get())
            except:
                gst_percent = 0

            final_total = subtotal + (subtotal * gst_percent / 100)

            # ---------------- DB CONNECTION ----------------
            conn = connect()
            cursor = conn.cursor()

            date = datetime.now().strftime("%Y-%m-%d")

            buyer_name = buyer_name_entry.get().strip()
            buyer_phone = buyer_phone_entry.get().strip()

            # ---------------- BUYER HANDLING ----------------
            buyer_id = None

            if buyer_name or buyer_phone:
                cursor.execute(
                    "SELECT id FROM buyers WHERE name=? AND phone=?",
                    (buyer_name, buyer_phone)
                )

                row = cursor.fetchone()

                if row:
                    buyer_id = row[0]
                else:
                    cursor.execute(
                        "INSERT INTO buyers (name, phone) VALUES (?, ?)",
                        (buyer_name, buyer_phone)
                    )
                    buyer_id = cursor.lastrowid

            # ---------------- INSERT SALE ----------------
            cursor.execute(
                "INSERT INTO sales (date, total, buyer_id) VALUES (?, ?, ?)",
                (date, final_total, buyer_id)
            )
            sale_id = cursor.lastrowid

            # ---------------- INSERT ITEMS ----------------
            for item_id, item in cart.items():
                used = item["qty"] * item["upc"] if item["type"] == "carton" else item["qty"]

                cursor.execute("""
                    INSERT INTO sale_items (sale_id, item_id, quantity, type, price)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item_id, item["qty"], item["type"], item["price"]))

                cursor.execute(
                    "UPDATE items SET stock_units = stock_units - ? WHERE id=?",
                    (used, item_id)
                )

            conn.commit()
            conn.close()

            # ---------------- INVOICE ----------------
            generate_invoice(
                sale_id,
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                gst_percent=gst_percent,
                do_print=do_print,
                cart=cart
            )

            messagebox.showinfo("Done", "Sale complete")
            win.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- BUTTONS ----------------
    button_frame = tk.Frame(win)
    button_frame.pack(fill="x", padx=10, pady=10)

    tk.Button(button_frame, text="➕ Add", width=10, command=add_to_cart).grid(row=0, column=0)
    tk.Button(button_frame, text="❌ Remove", width=10, command=remove_item).grid(row=0, column=1)
    tk.Button(button_frame, text="🗑 Clear", width=10, command=clear_cart).grid(row=0, column=2)

    tk.Button(button_frame, text="✔ Checkout", bg="#27AE60", fg="white",
              font=("Arial", 11, "bold"), width=20,
              command=lambda: checkout(False)).grid(row=1, column=0, columnspan=2)

    tk.Button(button_frame, text="🖨 Print Bill", bg="#2E86C1", fg="white",
              font=("Arial", 11, "bold"), width=20,
              command=lambda: checkout(True)).grid(row=1, column=2)

    # ---------------- KEYBOARD FLOW (FIXED) ----------------
    search_entry.bind("<KeyRelease>", search)
    search_entry.bind("<Down>", lambda e: result_list.focus_set())

    buyer_search.bind("<KeyRelease>", search_buyer)
    buyer_list.bind("<Return>", fill_buyer)    

    result_list.bind("<Return>", lambda e: qty_entry.focus_set())
    qty_entry.bind("<Return>", lambda e: discount_entry.focus_set())
    discount_entry.bind("<Return>", add_to_cart)

    cart_table.bind("<Delete>", lambda e: remove_item())

    win.bind("<F5>", lambda e: checkout(False))
    win.bind("<F6>", lambda e: checkout(True))

    search_entry.focus_set()
    search_entry.focus_set()
# ------------------ VIEW SALES ------------------
def view_sales_gui():
    win = tk.Toplevel(root)
    win.title("Sales")
    win.geometry("900x600")

    from tkinter import ttk

    # ---------------- SEARCH ----------------
    tk.Label(win, text="Search by Date (YYYY-MM-DD)").pack()
    search_entry = tk.Entry(win)
    search_entry.pack(fill="x")

    # ---------------- TABLE ----------------
    columns = ("Sale ID", "Date", "Total")

    tree = ttk.Treeview(win, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.pack(fill="both", expand=True)

    # ---------------- LOAD DATA ----------------
    def load_data(search_text=""):
        conn = connect()
        cursor = conn.cursor()

        if search_text:
            cursor.execute("""
                SELECT id, date, total
                FROM sales
                WHERE date LIKE ?
                ORDER BY id DESC
            """, ('%' + search_text + '%',))
        else:
            cursor.execute("""
                SELECT id, date, total
                FROM sales
                ORDER BY id DESC
            """)

        tree.delete(*tree.get_children())

        tree.tag_configure("low", background="#f8d7da")  # light red

        for row in cursor.fetchall():
            sale_id, date, total = row

            tree.insert("", "end", values=(
                sale_id,
                date,
                f"{total:.2f}"
            ))

        conn.close()

    # ---------------- OPEN DETAILS ----------------
    def open_details(event=None):
        selected = tree.focus()
        if not selected:
            return

        values = tree.item(selected, "values")
        sale_id = int(values[0])

        show_sale_details(sale_id)

    # ---------------- SEARCH EVENT ----------------
    def search(event=None):
        load_data(search_entry.get())

    search_entry.bind("<KeyRelease>", search)

    # ---------------- DOUBLE CLICK ----------------
    tree.bind("<Double-1>", open_details)

    # ---------------- INITIAL LOAD ----------------
    load_data()
    search_entry.focus_set()


# ------------------ RESET ------------------
def reset_gui():
    win = tk.Toplevel(root)
    win.title("Reset")

    def do_reset(mode):
        if not messagebox.askyesno("Confirm", "Are you sure?"):
            return

        conn = connect()
        cursor = conn.cursor()

        if mode == 1:
            cursor.execute("UPDATE items SET stock_units=0")
        elif mode == 2:
            cursor.execute("DELETE FROM sales")
            cursor.execute("DELETE FROM sale_items")
        elif mode == 3:
            cursor.execute("DELETE FROM items")
            cursor.execute("DELETE FROM sales")
            cursor.execute("DELETE FROM sale_items")

        conn.commit()
        conn.close()

        messagebox.showinfo("Done", "Reset complete")
        win.destroy()

    tk.Button(win, text="Reset Stock", command=lambda: do_reset(1)).pack()
    tk.Button(win, text="Delete Sales", command=lambda: do_reset(2)).pack()
    tk.Button(win, text="Full Reset", command=lambda: do_reset(3)).pack()

#-----------------Show Sale Details------------
def show_sale_details(sale_id):
    win = tk.Toplevel(root)
    win.title(f"Sale Details - #{sale_id}")
    win.geometry("700x500")

    from tkinter import ttk

    conn = connect()
    cursor = conn.cursor()

    # ---------------- BUYER INFO ----------------
    cursor.execute("""
        SELECT buyers.name, buyers.phone
        FROM sales
        LEFT JOIN buyers ON sales.buyer_id = buyers.id
        WHERE sales.id=?
    """, (sale_id,))

    buyer = cursor.fetchone()

    if buyer:
        tk.Label(win, text=f"Buyer: {buyer[0] or '-'}", font=("Arial", 11, "bold")).pack()
        tk.Label(win, text=f"Phone: {buyer[1] or '-'}").pack()

    # ---------------- TABLE ----------------
    columns = ("Item", "Type", "Qty", "Price", "Total")

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    scroll_y = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scroll_y.pack(side="right", fill="y")

    tree.configure(yscrollcommand=scroll_y.set)
    tree.pack(fill="both", expand=True)

    # ---------------- FETCH ITEMS ----------------
    cursor.execute("""
        SELECT items.name, sale_items.type, sale_items.quantity, sale_items.price
        FROM sale_items
        JOIN items ON items.id = sale_items.item_id
        WHERE sale_items.sale_id=?
    """, (sale_id,))

    total_sum = 0

    for name, typ, qty, price in cursor.fetchall():
        total = qty * price
        total_sum += total

        tree.insert("", "end", values=(
            name.capitalize(),
            typ,
            qty,
            f"{price:.2f}",
            f"{total:.2f}"
        ))

    conn.close()

    # ---------------- TOTAL ----------------
    tk.Label(
        win,
        text=f"Total: ₹{total_sum:.2f}",
        font=("Arial", 12, "bold")
    ).pack(pady=5)

    # ---------------- DELETE BUTTON ----------------
    def confirm_delete():
        if not messagebox.askyesno("Confirm", "Delete this sale?"):
            return

        delete_sale(sale_id)

        messagebox.showinfo("Deleted", "Sale deleted successfully")
        win.destroy()

    tk.Button(
        win,
        text="❌ Delete Sale",
        bg="red",
        fg="white",
        font=("Arial", 11, "bold"),
        command=confirm_delete
    ).pack(pady=10)


def edit_item_gui():
    win = tk.Toplevel(root)
    win.title("Edit Item")
    win.geometry("650x500")

    selected_id = None

    # ---------------- MAIN FRAME ----------------
    main_frame = tk.Frame(win)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------------- LEFT (SEARCH) ----------------
    left_frame = tk.LabelFrame(main_frame, text="Search Item", padx=10, pady=10)
    left_frame.pack(side="left", fill="both", expand=True, padx=5)

    search_entry = tk.Entry(left_frame)
    search_entry.pack(fill="x", pady=5)

    item_list = tk.Listbox(left_frame)
    item_list.pack(fill="both", expand=True)

    # ---------------- RIGHT (FORM) ----------------
    right_frame = tk.LabelFrame(main_frame, text="Item Details", padx=10, pady=10)
    right_frame.pack(side="right", fill="both", expand=True, padx=5)

    # Row 0
    tk.Label(right_frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(right_frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    # Row 1
    tk.Label(right_frame, text="Carton Price").grid(row=1, column=0, padx=5, pady=5)
    cp_entry = tk.Entry(right_frame)
    cp_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(right_frame, text="Unit Price").grid(row=1, column=2, padx=5, pady=5)
    up_entry = tk.Entry(right_frame)
    up_entry.grid(row=1, column=3, padx=5, pady=5)

    # Row 2
    tk.Label(right_frame, text="MRP").grid(row=2, column=0, padx=5, pady=5)
    mrp_entry = tk.Entry(right_frame)
    mrp_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(right_frame, text="Units/Carton").grid(row=2, column=2, padx=5, pady=5)
    upc_entry = tk.Entry(right_frame)
    upc_entry.grid(row=2, column=3, padx=5, pady=5)

    # Row 3 (🔥 FIXED STOCK UI)
    tk.Label(right_frame, text="Cartons").grid(row=3, column=0, padx=5, pady=5)
    carton_entry = tk.Entry(right_frame, width=10)
    carton_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(right_frame, text="Units").grid(row=3, column=2, padx=5, pady=5)
    unit_entry = tk.Entry(right_frame, width=10)
    unit_entry.grid(row=3, column=3, padx=5, pady=5)

    # ---------------- SEARCH ----------------
    def search(event=None):
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name FROM items WHERE name LIKE ?",
            ('%' + search_entry.get() + '%',)
        )

        item_list.delete(0, tk.END)

        for r in cursor.fetchall():
            item_list.insert(tk.END, f"{r[0]} - {r[1]}")

        conn.close()

        if item_list.size() > 0:
            item_list.selection_set(0)
            item_list.activate(0)

    # ---------------- LOAD ITEM ----------------
    def load_item(event=None):
        nonlocal selected_id

        selected = item_list.get(tk.ACTIVE)
        if not selected:
            return

        item_id = int(selected.split(" - ")[0])
        selected_id = item_id

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, carton_price, unit_price, mrp, units_per_carton, stock_units
            FROM items WHERE id=?
        """, (item_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        name, cp, up, mrp, upc, stock = row

        # clear all
        for e in [name_entry, cp_entry, up_entry, mrp_entry, upc_entry, carton_entry, unit_entry]:
            e.delete(0, tk.END)

        # fill values
        name_entry.insert(0, name)
        cp_entry.insert(0, cp)
        up_entry.insert(0, up)
        mrp_entry.insert(0, mrp)
        upc_entry.insert(0, upc)

        cartons = stock // upc if upc else 0
        units = stock % upc if upc else stock

        carton_entry.insert(0, cartons)
        unit_entry.insert(0, units)

        name_entry.focus_set()

    # ---------------- SAVE ----------------
    def save(event=None):
        if not selected_id:
            messagebox.showerror("Error", "Select item first")
            return

        name = name_entry.get().strip().lower()

        try:
            cp = float(cp_entry.get())
            up = float(up_entry.get())
            mrp = float(mrp_entry.get())
            upc = int(upc_entry.get())

            cartons = int(carton_entry.get() or 0)
            units = int(unit_entry.get() or 0)

            stock = cartons * upc + units

        except:
            messagebox.showerror("Error", "Invalid input")
            return

        conn = connect()
        cursor = conn.cursor()

        # prevent duplicate name
        cursor.execute(
            "SELECT id FROM items WHERE LOWER(name)=? AND id!=?",
            (name, selected_id)
        )

        if cursor.fetchone():
            messagebox.showerror("Error", "Item name already exists")
            conn.close()
            return

        cursor.execute("""
            UPDATE items
            SET name=?, carton_price=?, unit_price=?, mrp=?, units_per_carton=?, stock_units=?
            WHERE id=?
        """, (name, cp, up, mrp, upc, stock, selected_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("Saved", "Item updated")
        search_entry.focus_set()

    # ---------------- DELETE ----------------
    def delete(event=None):
        if not selected_id:
            return

        if not messagebox.askyesno("Confirm", "Delete this item?"):
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM items WHERE id=?", (selected_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", "Item removed")

        search()
        search_entry.focus_set()

    # ---------------- BUTTONS ----------------
    btn_frame = tk.Frame(right_frame)
    btn_frame.grid(row=4, column=0, columnspan=4, pady=10)

    tk.Button(btn_frame, text="✔ Save", bg="green", fg="white", width=12, command=save).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="❌ Delete", bg="red", fg="white", width=12, command=delete).grid(row=0, column=1, padx=5)

    # ---------------- KEYBOARD ----------------
    search_entry.bind("<KeyRelease>", search)
    search_entry.bind("<Down>", lambda e: item_list.focus_set())

    item_list.bind("<Return>", load_item)

    entries = [name_entry, cp_entry, up_entry, mrp_entry, upc_entry, carton_entry, unit_entry]

    for i in range(len(entries) - 1):
        entries[i].bind("<Return>", lambda e, idx=i: entries[idx + 1].focus_set())

    entries[-1].bind("<Return>", save)

    item_list.bind("<Delete>", delete)

    win.bind("<F5>", lambda e: save())
    win.bind("<F6>", lambda e: delete())

    search_entry.focus_set()

def sales_report_gui():
    from database import connect

    win = tk.Toplevel(root)
    win.title("Sales Report")
    win.geometry("420x520")

    tk.Label(win, text="Sales Report", font=("Arial", 14, "bold")).pack(pady=10)

    # ---------------- INPUT ----------------
    tk.Label(win, text="Enter Date (YYYY-MM-DD)").pack()
    date_entry = tk.Entry(win)
    date_entry.pack()

    tk.Label(win, text="Enter Month (YYYY-MM)").pack()
    month_entry = tk.Entry(win)
    month_entry.pack()

    # ---------------- RESULT LIST ----------------
    result_box = tk.Listbox(win, width=55)
    result_box.pack(pady=10)

    total_label = tk.Label(win, text="Total: ₹0.00", font=("Arial", 11, "bold"))
    total_label.pack()

    # ---------------- OPEN DETAILS ----------------
    def open_details(event=None):
        selected = result_box.curselection()
        if not selected:
            return

        text = result_box.get(selected[0])

        # ignore non-sale lines
        if "Sale #" not in text:
            return

        try:
            sale_id = int(text.split("Sale #")[1].split()[0])
        except:
            return

        show_sale_details(sale_id)

    # bind AFTER function is defined
    result_box.bind("<Double-1>", open_details)

    # ---------------- DAILY ----------------
    def show_daily():
        date = date_entry.get().strip()

        if not date:
            messagebox.showerror("Error", "Enter date")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, date, total 
            FROM sales 
            WHERE DATE(date) = DATE(?)
            ORDER BY id DESC
        """, (date,))

        data = cursor.fetchall()
        conn.close()

        result_box.delete(0, tk.END)

        if not data:
            result_box.insert(tk.END, "No sales found")
            total_label.config(text="Daily Total: ₹0.00")
            return

        total = 0

        for sale_id, full_date, amount in data:
            result_box.insert(
                tk.END,
                f"{full_date} | Sale #{sale_id} → ₹{amount:.2f}"
            )
            total += amount

        total_label.config(text=f"Daily Total: ₹{total:.2f}")

    # ---------------- MONTHLY ----------------
    def show_monthly():
        month = month_entry.get().strip()

        if not month:
            messagebox.showerror("Error", "Enter month")
            return

        conn = connect()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, date, total 
            FROM sales 
            WHERE date LIKE ?
            ORDER BY id DESC
        """, (month + "%",))

        data = cursor.fetchall()
        conn.close()

        result_box.delete(0, tk.END)

        if not data:
            result_box.insert(tk.END, "No sales found")
            total_label.config(text="Monthly Total: ₹0.00")
            return

        total = 0

        for sale_id, date, amount in data:
            result_box.insert(
                tk.END,
                f"{date} | Sale #{sale_id} → ₹{amount:.2f}"
            )
            total += amount

        total_label.config(text=f"Monthly Total: ₹{total:.2f}")

    # ---------------- BUTTONS ----------------
    tk.Button(win, text="Show Daily Report", command=show_daily).pack(pady=5)
    tk.Button(win, text="Show Monthly Report", command=show_monthly).pack(pady=5)

    date_entry.focus_set()
    

def delete_sale(sale_id):
    conn = connect()
    cursor = conn.cursor()

    # 1. get items of this sale
    cursor.execute("""
        SELECT item_id, quantity, type
        FROM sale_items
        WHERE sale_id=?
    """, (sale_id,))
    
    items = cursor.fetchall()

    # 2. restore stock
    for item_id, qty, typ in items:
        cursor.execute("SELECT units_per_carton FROM items WHERE id=?", (item_id,))
        upc = cursor.fetchone()[0]

        added_back = qty * upc if typ == "carton" else qty

        cursor.execute("""
            UPDATE items
            SET stock_units = stock_units + ?
            WHERE id=?
        """, (added_back, item_id))

    # 3. delete sale items
    cursor.execute("DELETE FROM sale_items WHERE sale_id=?", (sale_id,))

    # 4. delete sale
    cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))

    conn.commit()
    conn.close()


# ------------------ MAIN ------------------
root = tk.Tk()
root.title("Shop System")
root.geometry("500x550")
root.configure(bg=LIGHT_BG)

# ---------------- HEADER ----------------
header = tk.Frame(root, bg=PRIMARY, height=80)
header.pack(fill="x")

tk.Label(
    header,
    text="SHOP SYSTEM",
    bg=PRIMARY,
    fg="white",
    font=FONT_TITLE
).pack(pady=20)

# ---------------- MAIN AREA ----------------
main_frame = tk.Frame(root, bg=LIGHT_BG)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ---------------- PRIMARY ACTIONS ----------------
primary_frame = tk.Frame(main_frame, bg=LIGHT_BG)
primary_frame.pack(fill="x", pady=10)

# 💰 Make Sale (big)
tk.Button(
    primary_frame,
    text="💰 Make Sale",
    height=2,
    bg=SUCCESS,
    fg="white",
    font=FONT_HEADER,
    relief="flat",
    command=make_sale_gui
).pack(fill="x", pady=5)

# ➕ Add Item (big)
tk.Button(
    primary_frame,
    text="➕ Add Item",
    height=2,
    bg=PRIMARY,
    fg="white",
    font=FONT_HEADER,
    relief="flat",
    command=add_item_gui
).pack(fill="x", pady=5)

# ✏️ Edit Item (big)
tk.Button(
    primary_frame,
    text="✏️ Edit Item",
    height=2,
    bg="#5DADE2",
    fg="white",
    font=FONT_HEADER,
    relief="flat",
    command=edit_item_gui
).pack(fill="x", pady=5)


# ---------------- SECONDARY ACTIONS ----------------
secondary_frame = tk.Frame(main_frame, bg=LIGHT_BG)
secondary_frame.pack(fill="x", pady=15)

buttons = [
    ("📦 Add Stock", add_stock_gui),   # moved here (small)
    ("View Stock", view_stock_gui),
    ("View Sales", view_sales_gui),
    ("Sales Report", sales_report_gui),
    ("Reset Data", reset_gui),
]

for text, cmd in buttons:
    tk.Button(
        secondary_frame,
        text=text,
        height=1,
        font=FONT_NORMAL,
        relief="ridge",
        command=cmd
    ).pack(fill="x", pady=3)


# ---------------- EXIT ----------------
tk.Button(
    root,
    text="Exit",
    bg=DANGER,
    fg="white",
    font=FONT_HEADER,
    command=root.quit
).pack(fill="x", padx=20, pady=10)

root.mainloop()