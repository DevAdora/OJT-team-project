import datetime
import os
from rich.console import Console
from rich.table import Table

class ShoppingCart:
    def __init__(self):
        self.cart = []
        self.console = Console()

    def add_to_cart(self, item):
        self.cart.append(item)
        self.console.print(f"{item} has been added to your cart.", style="bold green")

    def view_cart(self):
        if not self.cart:
            self.console.print("Your cart is empty.", style="bold red")
        else:
            table = Table(title="Your Cart")
            table.add_column("Items", justify="left", style="magenta")
            for item in self.cart:
                table.add_row(item)
            self.console.print(table)

    def checkout(self, receipt_filename):
        if not self.cart:
            self.console.print("Your cart is empty. Add items to your cart before checking out.", style="bold red")
            return False
        else:
            if not os.path.exists('purchases'):
                os.makedirs('purchases')
            with open(receipt_filename, 'w') as f:
                username, date = receipt_filename.split('.')[0], receipt_filename.split('.')[1]
                f.write(f"Receipt for {username.replace("purchases/", "")} on {date}\n")
                f.write("Items purchased:\n")
                for item in self.cart:
                    f.write(f"- {item}\n")
            self.console.print("Checking out the following items:", style="bold green")
            table = Table(title="Items Purchased")
            table.add_column("Items", justify="left", style="magenta")
            for item in self.cart:
                table.add_row(item)
            self.console.print(table)
            self.cart.clear()
            self.console.print(f"Thank you for your purchase! Receipt saved as {receipt_filename}", style="bold green")
            return True