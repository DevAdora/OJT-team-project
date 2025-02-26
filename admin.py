import os

# Admin Interface
class Admin:
    def __init__(self):
        pass

    # To display all purchases
    def get_purchases(self):
        purchase_dir = 'purchases'
        purchases = []
        # Open each file in the purchases directory and read the contents
        if os.path.exists(purchase_dir):
            purchase_files = [f for f in os.listdir(purchase_dir) if f.endswith('.receipt.txt')]
            for file in purchase_files:
                with open(os.path.join(purchase_dir, file), 'r') as f:
                    items = f.read().splitlines()[1:]  # Skip the first line (header)
                    # Extract the item and quantity from each line
                    purchases.append({
                        'filename': file,
                        'items': items
                    })
        # Return the list of purchases
        return purchases

    # To display all categories and items
    def get_all_items(self):
        items_dir = 'items'
        all_items = {}
        if os.path.exists(items_dir):
            items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
            for file in items_files:
                category_name = file.replace('.txt', '')
                category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
                category_name = category_name.replace('And', 'and').title()
                with open(os.path.join(items_dir, file), 'r') as f:
                    items = f.read().splitlines()
                all_items[category_name] = items
        return all_items

    # To display all categories
    def get_all_categories(self):
        items_dir = 'items'
        all_categories = []
        if os.path.exists(items_dir):
            items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
            for file in items_files:
                category_name = file.replace('.txt', '')
                category_name = ''.join([' ' + char if char.isupper() else char for char in category_name]).strip()
                category_name = category_name.replace('And', 'and').title()
                all_categories.append(category_name)
        return all_categories

    # To display items in a specific category
    def get_items_by_category(self, category):
        items_dir = 'items'
        category = ''.join([word.capitalize() for word in category.split()])
        category_file = os.path.join(items_dir, f"{category}.txt")
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                items = f.read().splitlines()
            return items
        return []

    # To add item in a category
    def add_update_item(self, category, item, price):
        items_dir = 'items'
        category = ''.join([word.capitalize() for word in category.split()])
        category_file = os.path.join(items_dir, f"{category}.txt")
        if not os.path.exists(items_dir):
            os.makedirs(items_dir)
        items = []
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                items = f.read().splitlines()
        item_entry = f"{item}, {price}"
        if item_entry not in items:
            items.append(item_entry)
        with open(category_file, 'w') as f:
            f.write('\n'.join(items))
        
        # Update productsDataset.txt
        self.update_products_dataset(item_entry)
        
        return f"Item '{item}' added/updated in category '{category}'."

    # To delete item from a category
    def delete_item(self, category, item):
        items_dir = 'items'
        category = ''.join([word.capitalize() for word in category.split()])
        category_file = os.path.join(items_dir, f"{category}.txt")
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                items = f.read().splitlines()
            items = [i for i in items if not i.startswith(item)]
            with open(category_file, 'w') as f:
                f.write('\n'.join(items))
            
            # Update productsDataset.txt
            self.update_products_dataset()
            
            return f"Item '{item}' deleted from category '{category}'."
        return f"Category '{category}' or item '{item}' not found."

    # To edit item in a category
    def edit_item(self, category, old_item, new_item, price):
        items_dir = 'items'
        category = ''.join([word.capitalize() for word in category.split()])
        category_file = os.path.join(items_dir, f"{category}.txt")
        if os.path.exists(category_file):
            with open(category_file, 'r') as f:
                items = f.read().splitlines()
            updated_items = []
            for item in items:
                if item.startswith(old_item):
                    updated_items.append(f"{new_item}, {price}")
                else:
                    updated_items.append(item)
            with open(category_file, 'w') as f:
                f.write('\n'.join(updated_items))
            
            # Update productsDataset.txt
            self.update_products_dataset()
            
            return f"Item '{old_item}' updated to '{new_item}' with price '{price}' in category '{category}'."
        return f"Category '{category}' or item '{old_item}' not found."
    
    # To update productsDataset.txt when action is performed on items
    def update_products_dataset(self, new_item=None):
        items_dir = 'items'
        dataset_file = 'productsDataset.txt'
        all_items = []
        
        if os.path.exists(items_dir):
            items_files = [f for f in os.listdir(items_dir) if f.endswith('.txt')]
            for file in items_files:
                with open(os.path.join(items_dir, file), 'r') as f:
                    items = f.read().splitlines()
                    all_items.extend(items)
        
        if new_item and new_item not in all_items:
            all_items.append(new_item)
        
        with open(dataset_file, 'w') as f:
            f.write('\n'.join(all_items))