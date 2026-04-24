# 🏪 Shop Management System

A desktop-based shop management application built using Python and Tkinter.

## 🚀 Features

- Billing system (cart, GST, discounts)
- Inventory management (stock in cartons & units)
- Buyer management (save & reuse customers)
- Sales tracking and reports
- Invoice generation
- Delete sales with stock restoration

## 🛠 Tech Stack

- Python
- Tkinter (GUI)
- SQLite (Database)

## ▶️ How to Run

1. Make sure all files are inside a folder named `shop`

Example structure:

shop/
├── main.py  ← (this is the file to run)
├── gui.py
├── database.py
├── inventory.py
├── invoice.py
├── models.py
├── sales.py
├── update_db.py
├── db/
│   └── shop.db (auto-created)
└── invoices/ (auto-created)

2. Open terminal inside the `shop` folder

3. Run this command:
   on macos it is python3 gui.py
   on windows it is py gui.py

👉 `gui.py` is the starting point of the application.
⚠️ Make sure you run the command from inside the `shop` folder.




## 📌 Notes

- Database (`shop.db`) is created automatically
- Invoices are saved locally
- Designed for small shop / wholesale use

---

## 👨‍💻 Author

Shivam Gupta
Thanks For Visiting 😊
