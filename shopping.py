import datetime
import os

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

    def checkout(self, receipt_filename):
        if not self.cart:
            print("Your cart is empty. Add items to your cart before checking out.")
        else:
            if not os.path.exists('purchases'):
                os.makedirs('purchases')
            with open(receipt_filename, 'w') as f:
                username, date = receipt_filename.split('.')[0], receipt_filename.split('.')[1]
                f.write(f"Receipt for {username} on {date}\n")
                f.write("Items purchased:\n")
                for item in self.cart:
                    f.write(f"- {item}\n")
            print("Checking out the following items:")
            for item in self.cart:
                print(f"- {item}")
            self.cart.clear()
            print(f"Thank you for your purchase! Receipt saved as {receipt_filename}")