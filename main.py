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
            cart.checkout()
        elif choice == '5':
            print("Exiting the program. Goodbye!")
            if not cart.cart:
                os.remove(receipt_filename)
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