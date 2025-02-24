import re
import datetime
import os
from chatbot import GroceryStoreRecommender
from shopping import ShoppingCart

def recommendation_system(cart):
    recommender = GroceryStoreRecommender()
    selected_items = []
    while True:
        user_query = input("Enter some products you want to buy (type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            for item in selected_items:
                cart.add_to_cart(item)
            return
        recommended_items = recommender.recommendItems(user_query)
        if len(recommended_items) < 1:
            print("No recommendations found. Please try again.")
            continue
        while recommended_items:
            print("Recommended items:")
            for idx, item in enumerate(recommended_items, 1):
                print(f"[{idx}] - {item}")
            choice = input("Enter the number of the item to add to cart, type 'new' for a new recommendation, or 'done' to finish: ")
            if choice.lower() == 'new':
                break
            elif choice.lower() == 'done':
                for item in selected_items:
                    cart.add_to_cart(item)
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(recommended_items):
                selected_item = recommended_items.pop(int(choice) - 1)
                selected_items.append(selected_item)
                print(f"{selected_item} has been added to your list.")
            else:
                print("Invalid choice. Please try again.")

def shop(cart):
    while True:
        recommendation_system(cart)

def user_menu(username):
    cart = ShoppingCart()
    receipt_filename = create_receipt_file(username)
    while True:
        print("\nMain Menu:")
        print("1. Recommendation System")
        print("2. Shop")
        print("3. Cart")
        print("4. Checkout")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            recommendation_system(cart)
        elif choice == '2':
            shop(cart)
        elif choice == '3':
            cart.view_cart()
        elif choice == '4':
            cart.checkout(receipt_filename)
        elif choice == '5':
            print("Exiting the program. Goodbye!")
            if not cart.cart:
                with open(receipt_filename, 'r') as f:
                    content = f.read()
                    if "Items purchased:" not in content:
                        os.remove(receipt_filename)
                        print(f"Receipt file {receipt_filename} did not contain 'Items purchased:' and was deleted.")
            break
        else:
            print("Invalid choice. Please try again.")









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
    while True:
        print("\nLogin Menu:")
        print("1. User Login")
        print("2. Admin Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter your username: ")
            if re.match("^[A-Za-z0-9]+$", username):
                print(f"Welcome, {username}!")
                user_menu(username)
            else:
                print("Invalid username. Only text and numbers are allowed.")
        elif choice == '2':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            if username == "admin" and password == "admin":
                print("Welcome, Admin!")
                admin_menu()
            else:
                print("Invalid admin credentials. Please try again.")
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    login()

if __name__ == "__main__":
    main()