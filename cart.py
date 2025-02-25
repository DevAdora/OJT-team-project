import os
from rich.console import Console
from rich.table import Table
import datetime

class ShoppingCart:
    def __init__(self):
        self.cart = []
        self.console = Console()

    def add_to_cart(self, item, price, quantity):
        for i, (cart_item, cart_price, cart_quantity) in enumerate(self.cart):
            if cart_item == item and cart_price == price:
                self.cart[i] = (cart_item, cart_price, cart_quantity + quantity)
                self.console.print(f"Updated {item} quantity to {cart_quantity + quantity}.", style="bold green")
                return
        self.cart.append((item, price, quantity))
        self.console.print(f"{quantity} {item} has been added to your cart.", style="bold green")

    def view_cart(self):
        if not self.cart:
            self.console.print("Your cart is empty.", style="bold red")
        else:
            table = Table(title="Your Cart")
            table.add_column("Items", justify="left", style="magenta")
            table.add_column("Price", justify="right", style="cyan")
            table.add_column("Quantity", justify="right", style="cyan")
            table.add_column("Total", justify="right", style="cyan")
            total_price = 0
            for item, price, quantity in self.cart:
                total = price * quantity
                total_price += total
                table.add_row(item, f"${price:.2f}", str(quantity), f"${total:.2f}")
            self.console.print(table)
            self.console.print(f"Total Price: ${total_price:.2f}", style="bold green")
    
    def checkout(self, receipt_filename):
        if not self.cart:
            return False

        purchases_folder = "purchases"
        if not os.path.exists(purchases_folder):
            os.makedirs(purchases_folder)

        # Extract username and date_str properly without "purchases/"
        filename_only = os.path.basename(receipt_filename)  # Removes the "purchases/" path
        parts = filename_only.split('.')

        if len(parts) < 2:
            return False  # Invalid filename format

        username = parts[0]  # Extract username directly
        date_str = parts[1]  # Extract date string
        counter = 1  # Start with 1

        while True:
            new_filename = os.path.join(purchases_folder, f"{username}.{date_str}.{counter}.receipt.txt")

            # If the file exists, check its content
            if os.path.exists(new_filename):
                with open(new_filename, 'r', encoding="utf-8") as f:
                    content = f.read()

                # If "Items purchased:" is missing, overwrite this file
                if "Items purchased:" not in content:
                    break
            else:
                # Use this file if it doesn’t exist
                break
            
            counter += 1  # Increment and try the next filename

        # ✅ Write receipt with UTF-8 encoding
        with open(new_filename, 'w', encoding="utf-8") as f:
            f.write(f"Receipt for {username} on {date_str}\n")
            f.write("Items purchased:\n")
            for item, price, quantity in self.cart:
                f.write(f"- {item}: {quantity} x ₱{price} = ₱{price * quantity}\n")
            total_price = sum(price * quantity for _, price, quantity in self.cart)
            f.write(f"\nTotal: ₱{total_price}\n")

        self.cart.clear()  # Clear the cart after writing receipt
        return True

