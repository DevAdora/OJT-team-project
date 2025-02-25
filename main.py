import re
import datetime
import os
from chatbot import GroceryStoreRecommender
from cart import ShoppingCart
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
    print("Admin menu is under construction.")
    print("\nOptions Menu:")
    print("1. Purchase List")
    print("2. Available items on sale")
    
    choice = input("Enter your choice: ")
    
    if choice == '1':
        print("\nPurchase List:")
        purchase_dir = 'purchases'
        if os.path.exists(purchase_dir):
            purchase_files = os.listdir(purchase_dir)
            if purchase_files:
                print("\nPurchase history:")
                for file in purchase_files:
                    if file.endswith('.receipt.txt'):
                        with open(os.path.join(purchase_dir, file), 'r') as f:
                            print(f"\n--- {file} ---")
                            print(f.read())
            else:
                print("No purchase history found.")
        else:
            print("No purchase history found.")

def admin_menu():
    print("\nOptions Menu:")
    print("1. Purchase List")
    print("2. Available items on sale")
    
    choice = input("Enter your choice: ")
    if choice == '1':
        print("\nPurchase List:")
        purchase_dir = 'purchases'
        if os.path.exists(purchase_dir):
            purchase_files = [f for f in os.listdir(purchase_dir) if f.endswith('.receipt.txt')]
            if purchase_files:
                print("\nPurchase history:")
                for idx, file in enumerate(purchase_files, 1):
                    print(f"[{idx}] {file}")
                
                while True:
                    file_choice = input("\nEnter the number of the receipt to view details (or exit to return): ")
                    if file_choice == 'exit':
                        break
                    elif file_choice.isdigit() and 1 <= int(file_choice) <= len(purchase_files):
                        selected_file = purchase_files[int(file_choice) - 1]
                        print(f"\n--- {selected_file} ---")
                        with open(os.path.join(purchase_dir, selected_file), 'r') as f:
                            print(f.read())
                            print("\nOptions:")
                            print("1. View another receipt")
                            print("2. Return to Admin Menu")
                            print("3. Exit")
                            option = input("\nEnter your choice: ")
                            if option == '2':
                                admin_menu()
                                return  
                            elif option == '3':
                                print("Exiting the program. Goodbye!")
                                break
                            elif option != '1':
                                print("Invalid choice. Returning to receipt list.")
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("No purchase history found.")
        else:
            print("No purchase history found.")



    if choice == '2':
        while True:
            print("\nAvailable items on sale:")
            print("1. View items by category")
            print("2. Add new or update existing items")
            print("3. Delete items")
            print("4. Return to Admin Menu")
            
            items_choice = input("\nEnter your choice: ")
            
            if items_choice == '4':
                break
                
            elif items_choice == '1':
                print("\nSelect Category to view:")
                items_dir = 'items'
                if os.path.exists(items_dir):
                    items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
                    if items_files:
                        for idx, file in enumerate(items_files, 1):
                            # Remove .txt extension and display as menu option
                            category_name = file.replace('.txt', '')
                            category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
                            category_name = category_name.replace('And', 'and').title()
                            print(f"{idx}. {category_name}")
                        print(f"{len(items_files) + 1}. All Categories") 
                        print(f"{len(items_files) + 2}. Return to Previous Menu")
                    else:
                        print("No category files found.")
                else:
                    print("Items directory not found.")
                
                category_choice = input("\nEnter category number: ")
                
                if category_choice == '6':
                    continue
                    
                items_dir = 'items'
                if os.path.exists(items_dir):
                    items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
                    if items_files:
                        # Display files based on category choice
                        for idx, file in enumerate(items_files, 1):
                            if (category_choice == '5' or
                                (category_choice == '1' and 'bakeryAndBread' in file) or
                                (category_choice == '2' and 'beverages' in file) or
                                (category_choice == '3' and 'dairyandEggs' in file) or
                                (category_choice == '4' and 'Clothing' in file)):
                                print(f"[{idx}] {file}")
                        
                        # Let user select specific file to view
                        file_choice = input("\nEnter the number of the file to view details: ")
                        if file_choice.isdigit() and 1 <= int(file_choice) <= len(items_files):
                            selected_file = items_files[int(file_choice) - 1]
                            print(f"\n--- {selected_file} ---")
                            with open(os.path.join(items_dir, selected_file), 'r') as f:
                                content = f.read()
                                print(content)
                                # Store items for potential updates
                                items = content.splitlines()
                            input("\nPress Enter to continue...")
                        else:
                            print("Invalid file selection.")
                            input("\nPress Enter to continue...")
                    else:
                        print("No items found.")
                        input("\nPress Enter to continue...")
                else:
                    print("Items directory not found.")
                    input("\nPress Enter to continue...")
                    
            elif items_choice == '2':
                print("\n=== Update Item ===")
                items_dir = 'items'
                if os.path.exists(items_dir):
                    items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
                    if items_files:
                        print("\nAvailable Categories:")
                        for idx, file in enumerate(items_files, 1):
                            category_name = file.replace('.txt', '')
                            category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
                            category_name = category_name.replace('And', 'and').title()
                            print(f"{idx}. {category_name}")
                        
                        category_choice = input("\nEnter category number to update items: ")
                        if category_choice.isdigit() and 1 <= int(category_choice) <= len(items_files):
                            selected_file = items_files[int(category_choice) - 1]
                            
                            # Read existing items
                            with open(os.path.join(items_dir, selected_file), 'r') as f:
                                items = f.read().splitlines()
                            
                            print("\nCurrent items in category:")
                            for idx, item in enumerate(items, 1):
                                print(f"{idx}. {item}")
                            
                            item_choice = input("\nEnter item number to update (or 0 to add new item): ")
                            
                            if item_choice == '0':
                                new_item = input("Enter new item name: ")
                                # Add to category file
                                with open(os.path.join(items_dir, selected_file), 'a') as f:
                                    f.write(f'\n{new_item}')
                                
                                # Add to products dataset
                                with open('productsDataset.txt', 'a') as f:
                                    # Add to products dataset
                                    with open('productsDataset.txt', 'r') as f:
                                        products = f.read().splitlines()
                                    products.append(new_item)
                                    with open('productsDataset.txt', 'w') as f:
                                        f.write('\n'.join(products))
                                    
                                print(f"\nAdded: {new_item}")
                                
                            elif item_choice.isdigit() and 1 <= int(item_choice) <= len(items):
                                old_item = items[int(item_choice) - 1]
                                new_item = input(f"Enter new name for '{old_item}': ")
                                items[int(item_choice) - 1] = new_item
                                
                                # Update category file
                                with open(os.path.join(items_dir, selected_file), 'w') as f:
                                    f.write('\n'.join(items))
                                    
                                    # Update products dataset
                                    with open('productsDataset.txt', 'r') as pf:
                                        products = pf.read().splitlines()
                                    products = [p for p in products if p != old_item]
                                    products.append(new_item)
                                    with open('productsDataset.txt', 'w') as pf:
                                        pf.write('\n'.join(products))
                                    
                                print(f"\nUpdated: '{old_item}' to '{new_item}'")
                            else:
                                print("Invalid item selection.")
                    else:
                        print("No category files found.")
                else:
                    print("Items directory not found.")
                
                input("\nPress Enter to continue...")

            elif items_choice == '3':
                print("\n=== Delete Item ===")
                items_dir = 'items'
                if os.path.exists(items_dir):
                    items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
                    if items_files:
                        print("\nAvailable Categories:")
                        for idx, file in enumerate(items_files, 1):
                            category_name = file.replace('.txt', '')
                            category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
                            category_name = category_name.replace('And', 'and').title()
                            print(f"{idx}. {category_name}")
                        
                        category_choice = input("\nEnter category number to delete items from: ")
                        if category_choice.isdigit() and 1 <= int(category_choice) <= len(items_files):
                            selected_file = items_files[int(category_choice) - 1]
                            
                            # Read existing items
                            with open(os.path.join(items_dir, selected_file), 'r') as f:
                                items = f.read().splitlines()
                            
                            print("\nCurrent items in category:")
                            for idx, item in enumerate(items, 1):
                                print(f"{idx}. {item}")
                            
                            item_choice = input("\nEnter item number to delete: ")
                            
                            if item_choice.isdigit() and 1 <= int(item_choice) <= len(items):
                                deleted_item = items.pop(int(item_choice) - 1)
                                
                                # Update category file
                                with open(os.path.join(items_dir, selected_file), 'w') as f:
                                    f.write('\n'.join(items))
                                
                                # Remove from products dataset
                                with open('productsDataset.txt', 'r') as f:
                                    products = f.read().splitlines()
                                
                                if deleted_item in products:
                                    products.remove(deleted_item)
                                    with open('productsDataset.txt', 'w') as f:
                                        f.write('\n'.join(products))
                                    
                                    with open('productsDataset.txt', 'w') as f:
                                        f.write('\n'.join(products))
                                
                                print(f"\nDeleted: {deleted_item}")
                            else:
                                print("Invalid item selection.")
                        else:
                            print("Invalid category selection.")
                    else:
                        print("No category files found.")
                else:
                    print("Items directory not found.")
                
                input("\nPress Enter to continue...")

            elif items_choice == '4':
                return
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