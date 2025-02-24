import os
from rich.console import Console
from rich.table import Table

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
                total = int(price) * int(quantity)
                total_price += int(total)
                table.add_row(item, str(price), str(quantity), str(total))
            table.add_row("Total", "", "", str(total_price))
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
                for item, price, quantity in self.cart:
                    f.write(f"- {item}: {quantity} x {price}\n")
            self.console.print("Checking out the following items:", style="bold green")
            table = Table(title="Items Purchased")
            table.add_column("Items", justify="left", style="magenta")
            table.add_column("Quantity", justify="left", style="magenta")
            table.add_column("Price", justify="left", style="magenta")
            table.add_column("Total", justify="left", style="magenta")
            for item, price, quantity in self.cart:
                table.add_row(item, str(price), str(quantity), str(int(price) * int(quantity)))
            self.console.print(table)
            self.cart.clear()
            self.console.print(f"Thank you for your purchase! Receipt saved as {receipt_filename}", style="bold green")
            return True