import os
from rich.table import Table
from rich.console import Console

class Shop:
    def __init__(self, cart):
        self.cart = cart
        self.categories = self.load_categories()
        self.console = Console()

    def load_categories(self):
        categories = []
        if not os.path.exists('items'):
            self.console.print("The 'items' directory does not exist.", style="bold red")
            return categories

        txt_files = [f for f in os.listdir('items') if f.endswith('.txt')]
        if not txt_files:
            self.console.print("No '.txt' files found in the 'items' directory.", style="bold red")
            return categories

        for filename in txt_files:
            category_name = filename.replace('.txt', '')
            category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
            category_name = category_name.replace('And', 'and').title()
            categories.append((filename, category_name))
        return categories

    def display_categories(self):
        table = Table(title="Categories")
        table.add_column("Index", justify="center", style="cyan", no_wrap=True)
        table.add_column("Category", justify="left", style="magenta")
        table.add_row("0", "Exit")
        for idx, (_, category_name) in enumerate(self.categories, 1):
            table.add_row(str(idx), category_name)
        self.console.print(table)

    def display_products(self, category_filename):
        print(category_filename)
        with open(f'items/{category_filename}', 'r') as f:
            products = f.readlines()
        table = Table(title="Products")
        table.add_column("Index", justify="center", style="cyan", no_wrap=True)
        table.add_column("Product", justify="left", style="magenta")
        table.add_column("Price", justify="right", style="green")
        table.add_row("0", "Exit", "")
        for idx, product in enumerate(products, 1):
            try:
                item, price = product.strip().split(", ")
                table.add_row(str(idx), item, price)
            except ValueError:
                self.console.print(f"Skipping invalid product line: {product.strip()}", style="bold red")
        self.console.print(table)
        return products

    def shop(self):
        while True:
            self.display_categories()
            choice = input("Select a category by number, or '0' to exit: ")
            if choice == '0':
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(self.categories):
                category_filename = self.categories[int(choice) - 1][0]
                products = self.display_products(category_filename)
                while True:
                    product_choice = input("Select a product by number to add to cart, or '0' to exit: ")
                    if product_choice == '0':
                        break
                    elif product_choice.isdigit() and 1 <= int(product_choice) <= len(products):
                        selected_product = products[int(product_choice) - 1].strip()
                        item, price = selected_product.split(", ")
                        quantity = input(f"Enter the quantity for {item}: ")
                        if quantity.isdigit() and int(quantity) > 0:
                            self.cart.add_to_cart(item, price, int(quantity))
                        else:
                            self.console.print("Invalid quantity. Please try again.", style="bold red")
                    else:
                        self.console.print("Invalid choice. Please try again.", style="bold red")
            else:
                self.console.print("Invalid choice. Please try again.", style="bold red")