from chatbot import GroceryStoreRecommender

class ShoppingCart:
    def __init__(self):
        self.cart = []

    def add_to_cart(self, item):
        self.cart.append(item)
        print(f"{item} has been added to your cart.")

    def view_cart(self):
        if not self.cart:
            print("Your cart is empty.")
        else:
            print("Your cart contains:")
            for item in self.cart:
                print(f"- {item}")

    def checkout(self):
        if not self.cart:
            print("Your cart is empty. Add items to your cart before checking out.")
        else:
            print("Checking out the following items:")
            for item in self.cart:
                print(f"- {item}")
            self.cart.clear()
            print("Thank you for your purchase!")

def recommendation_system():
    recommender = GroceryStoreRecommender()
    while True:
        user_query = input("Enter your query (type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break
        recommended_items = recommender.recommendItems(user_query)
        print(f"Recommended items: {recommended_items}")

def shop(cart):
    while True:
        item = input("Enter the item you want to add to your cart (type 'exit' to quit): ")
        if item.lower() == 'exit':
            break
        cart.add_to_cart(item)

def main():
    cart = ShoppingCart()
    while True:
        print("\nMain Menu:")
        print("1. Recommendation System")
        print("2. Shop")
        print("3. Cart")
        print("4. Checkout")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            recommendation_system()
        elif choice == '2':
            shop(cart)
        elif choice == '3':
            cart.view_cart()
        elif choice == '4':
            cart.checkout()
        elif choice == '5':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()