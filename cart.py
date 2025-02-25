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

        def write_receipt(filename):
            with open(filename, 'w') as f:
                parts = filename.split('/')[-1].split('.')
                username = parts[0]
                date_str = parts[1]
                f.write(f"Receipt for {username.replace("purchases/", "")} on {date_str}\n")
                f.write("Items purchased:\n")
                for item, price, quantity in self.cart:
                    f.write(f"- {item}: {quantity} x {price}\n")
                self.cart.clear()

        parts = receipt_filename.split('.')
        username = parts[0].split('/')[-1]  # Extract username
        date_str = parts[1]  # Extract date

        if os.path.exists(receipt_filename):
            with open(receipt_filename, 'r') as f:
                content = f.read()
                if "Items purchased:" not in content:
                    write_receipt(receipt_filename)
                    return True

        parts = receipt_filename.split('.')
        username = parts[0].split('/')[-1]  # Extract username
        date_str = parts[1]  # Extract date
        counter = int(parts[2])  # Extract counter

        purchases_folder = "purchases"
        if not os.path.exists(purchases_folder):
            os.makedirs(purchases_folder)

        while True:
            new_filename = os.path.join(purchases_folder, f"{username}.{date_str}.{counter}.receipt.txt")
            if not os.path.exists(new_filename):
                write_receipt(new_filename)
                return True
            counter += 1