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
        for filename in os.listdir('items'):
            if filename.endswith('.txt'):
                category_name = filename.replace('.txt', '')
                category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
                category_name = category_name.replace('And', 'and').title()
                categories.append((filename, category_name))
        return categories

    def display_categories(self):
        table = Table(title="Categories")
        table.add_column("Index", justify="center", style="cyan", no_wrap=True)
        table.add_column("Category", justify="left", style="magenta")
        table.add_row("[0]", "Exit")
        for idx, (_, category_name) in enumerate(self.categories, 1):
            table.add_row(str(idx), category_name)
        self.console.print(table)

    def display_products(self, category_filename):
        with open(f'items/{category_filename}', 'r') as f:
            products = f.readlines()
        table = Table(title="Products")
        table.add_column("Index", justify="center", style="cyan", no_wrap=True)
        table.add_column("Product", justify="left", style="magenta")
        table.add_row("0", "Exit")
        for idx, product in enumerate(products, 1):
            table.add_row(str(idx), product.strip())
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
                        self.cart.add_to_cart(selected_product)
                    else:
                        self.console.print("Invalid choice. Please try again.", style="bold red")
            else:
                self.console.print("Invalid choice. Please try again.", style="bold red")