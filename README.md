# 🏪 Shop Management System

A desktop-based shop management application built using Python and Tkinter.

---

## 🚀 Features

- Billing system (cart, GST, discounts)
- Inventory management (stock in cartons & units)
- Buyer management (save & reuse customers)
- Sales tracking and reports
- Invoice generation (PDF)
- Delete sales with stock restoration

---

## 🛠 Tech Stack

- Python
- Tkinter (GUI)
- SQLite (Database)
- ReportLab (PDF generation)

---

## ▶️ How to Run

1. Make sure all files are inside a folder named `shop`

Example structure:
shop/
├── gui.py ← (this is the file to run)
├── main.py
├── database.py
├── inventory.py
├── invoice.py
├── models.py
├── sales.py
├── update_db.py
├── db/
│ └── shop.db (auto-created)
└── invoices/ (auto-created)



2. Open terminal inside the `shop` folder

3. Run the app:
  py gui.py

👉 `gui.py` is the starting point of the application  
⚠️ Make sure you run the command from inside the `shop` folder  

---

## 📦 Requirements

Install required library:
pip install reportlab


---

## 🖨 Invoice & Printing

- Invoices are saved automatically in:
Documents/shop/invoices

👉 This is outside the project folder (inside the user's Documents)

### Printing behavior:

- If **SumatraPDF is installed**, invoices will print automatically  
- If not installed, the PDF will simply open  

### Optional (for auto printing):

Download SumatraPDF:  
https://www.sumatrapdfreader.org/download-free-pdf-viewer  

> The app works even without SumatraPDF



## 👨‍💻 Author

Shivam Gupta  

Thanks for visiting 😊
