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