from database import setup_database
from inventory import add_item, view_items
from sales import make_sale
from invoice import generate_invoice
from inventory import add_item, view_items, remove_stock
from sales import make_sale, view_sales, view_sale_details
from inventory import add_item, view_items, remove_stock, reset_data
def menu():
    while True:
        print("\n--- SHOP MENU ---")
        print("1. Add Item")
        print("2. View Stock")
        print("3. Make Sale")
        print("4. Remove Stock")
        print("5. View sales")
        print("6. View sale details")
        print("7. Reset data")
        print("8. Exit")


        choice = input("Enter choice: ")

        if choice == "1":
            add_item()

        elif choice == "2":
            view_items()

        elif choice == "3":
            sale_id = make_sale()
            if sale_id:
                generate_invoice(sale_id)

        elif choice == "4":
            remove_stock()
        elif choice =="5":
            view_sales()
        elif choice == "6":
            view_sale_details()
        elif choice == "7":
            reset_data()
        elif choice == "8":
            break

if __name__ == "__main__":
    setup_database()
    menu()

