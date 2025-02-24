import re
import datetime
import os
from chatbot import GroceryStoreRecommender
from shopping import ShoppingCart
from shop import Shop
from rich.table import Table
from rich.console import Console


def recommendation_system(cart):
    recommender = GroceryStoreRecommender()
    console = Console()
    while True:
        user_query = input("Enter some products you want to buy (type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            return
        recommended_items = recommender.recommendItems(user_query)
        if len(recommended_items) < 1:
            console.print("No recommendations found. Please try again.", style="bold red")
            continue
        while recommended_items:
            # First display the options
            options_table = Table(title="Options")
            options_table.add_column("Key", justify="center", style="cyan", no_wrap=True)
            options_table.add_column("Action", justify="left", style="magenta")
            options_table.add_row("n", "New prompt")
            options_table.add_row("d", "Done selecting items")
            console.print(options_table)
            
            # Show recommended items with product and price columns.
            items_table = Table(title="Recommended items")
            items_table.add_column("Index", justify="center", style="cyan", no_wrap=True)
            items_table.add_column("Product", justify="left", style="magenta")
            items_table.add_column("Price", justify="left", style="magenta")
            for idx, item in enumerate(recommended_items, 1):
                # Expecting item as "product, price"
                product, price = item.split(", ")
                items_table.add_row(str(idx), product, price)
            console.print(items_table)
            
            choice = input("Enter the number of the item to add to cart, type 'n' for new prompt or 'd' if you're done: ")

            if choice.lower() == 'n':
                break
            elif choice.lower() == 'd':
                return  # Exit the recommendation system
            elif choice.isdigit() and 1 <= int(choice) <= len(recommended_items):
                selected_item = recommended_items.pop(int(choice) - 1)
                product, price = selected_item.split(", ")
                qty = input(f"Enter quantity for {product}: ")
                if qty.isdigit() and int(qty) > 0:
                    cart.add_to_cart(product, price, int(qty))
                else:
                    console.print("Invalid quantity. Please try again.", style="bold red")
            else:
                console.print("Invalid choice. Please try again.", style="bold red")

def user_menu(username):
    cart = ShoppingCart()
    receipt_filename = create_receipt_file(username)
    shop_instance = Shop(cart)
    console = Console()
    while True:
        table = Table(title="Main Menu")
        table.add_column("Key", justify="left", style="green", no_wrap=True)
        table.add_column("Action", justify="left", style="white", no_wrap=True)
        table.add_row("1", "Recommendation System")
        table.add_row("2", "Shop")
        table.add_row("3", "Cart")
        table.add_row("4", "Checkout")
        table.add_row("5", "Exit")
        console.print(table)
        choice = input("Enter your choice: ")

        if choice == '1':
            recommendation_system(cart)
        elif choice == '2':
            shop_instance.shop()
        elif choice == '3':
            cart.view_cart()
        elif choice == '4':
            hasItems = cart.checkout(receipt_filename)
            if hasItems:
                break
        elif choice == '5':
            console.print("Exiting the program. Goodbye!", style="bold yellow")
            with open(receipt_filename, 'r') as f:
                content = f.read()
            if "Items purchased:" not in content:
                os.remove(receipt_filename)
            break
        else:
            console.print("Invalid choice. Please try again.", style="bold red")

def admin_menu():
    console = Console()
    console.print("Admin menu is under construction.", style="bold yellow")

def create_receipt_file(username):
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    increment = 1
    if not os.path.exists('purchases'):
        os.makedirs('purchases')
    while True:
        receipt_filename = f"purchases/{username}.{date_str}.{increment}.receipt.txt"
        if not os.path.exists(receipt_filename):
            with open(receipt_filename, 'w') as f:
                f.write(f"Receipt for {username} on {date_str}\n")
            break
        increment += 1
    return receipt_filename

def login():
    console = Console()
    while True:
        table = Table(title="Login Menu")
        table.add_column("Key", justify="left", style="green", no_wrap=True)
        table.add_column("Action", justify="left", style="white", no_wrap=True)
        table.row_styles = ["none", "dim"]
        table.add_row("1", "User Login")
        table.add_row("2", "Admin Login")
        table.add_row("3", "Exit")
        console.print(table)
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter your username: ")
            if re.match("^[A-Za-z0-9]+$", username):
                console.print(f"Welcome, {username}!", style="bold green")
                user_menu(username)
            else:
                console.print("Invalid username. Only text and numbers are allowed.", style="bold red")
        elif choice == '2':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            if username == "admin" and password == "admin":
                console.print("Welcome, Admin!", style="bold green")
                admin_menu()
            else:
                console.print("Invalid admin credentials. Please try again.", style="bold red")
        elif choice == '3':
            console.print("Exiting the program. Goodbye!", style="bold yellow")
            break
        else:
            console.print("Invalid choice. Please try again.", style="bold red")

def main():
    login()

if __name__ == "__main__":
    main()