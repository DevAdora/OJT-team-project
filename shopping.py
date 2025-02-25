import os
from rich.console import Console
from rich.table import Table
import datetime

class ShoppingCart:
    def __init__(self):
        self.cart = []
        self.console = Console()

    def add_to_cart(self, item, price, quantity):
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
        # Splice the receipt_filename to extract the username and date
        parts = receipt_filename.split('.')
        username = parts[0].split('/')[-1]  # Extract username
        date_str = parts[1]  # Extract date
        with open(receipt_filename, 'a') as f:
            f.write("Items purchased:\n")
            for item, price, quantity in self.cart:
                f.write(f"- {item}: {quantity} x {price}\n")
        self.cart.clear()
        return True