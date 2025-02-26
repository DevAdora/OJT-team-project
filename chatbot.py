from sentence_transformers import SentenceTransformer, util
import numpy as np
from fuzzywuzzy import process
import re

class GroceryStoreRecommender:
    def __init__(self, modelName='all-MiniLM-L6-v2', dataFile='productsDataset.txt', synonymsFile='synonymsMapping.txt'):
        # Load a pre-trained model
        self.model = SentenceTransformer(modelName)

        # Read and preprocess dataset (store items as a dictionary: product -> price)
        self.items = {}
        with open(dataFile, 'r') as f:
            for line in f:
                parts = line.strip().split(', ')
                if len(parts) == 2:
                    self.items[parts[0].lower()] = int(parts[1])
        
        # Precompute embeddings for all item names
        self.item_names = list(self.items.keys())
        self.itemEmbeddings = self.model.encode(self.item_names, convert_to_tensor=True)

        # Load synonyms mapping from file and build domain mapping.
        # Expected format for each line:
        #   main_product: synonym1, synonym2, ..., domain_keyword
        # Store synonyms as a dictionary: synonym -> main product
        self.synonyms = {}
        # Store domain mapping as a dictionary: domain -> list of products
        self.domain_to_products = {}

        # Read synonyms file
        with open(synonymsFile, 'r') as f:
            for line in f:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    main_product, syns = parts[0].lower(), parts[1].split(', ')
                    # The last element is assumed to be the domain keyword (e.g. bakery, beverages, ...).
                    domain = syns[-1].lower()
                    # Map each synonym to the main product.
                    for synonym in syns:
                        # Set the main product as the value for the synonym key.
                        # Example: { 'cola': 'coca cola', 'pop': 'coca cola', ... }
                        self.synonyms[synonym.lower()] = main_product

                    # Add the main product to the domain mapping.
                    # Domain = Root keyword for the product category.
                    # Example: { 'beverages': ['coca cola', 'pepsi', ...], ... }
                    if domain not in self.domain_to_products:
                        self.domain_to_products[domain] = []
                    # Ensure no duplicates are added.
                    if main_product not in self.domain_to_products[domain]:
                        self.domain_to_products[domain].append(main_product)

    # Add a method to expand the query with synonyms (synonymMapping.txt contents)
    def expand_query(self, query):
        """Expands query with synonyms by appending all main product names found.
           This ensures that if multiple synonyms occur, all are added to the query."""
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        # Will store all main product names found in the query
        found = []
        # Find all synonyms in the query and append their main product names
        # Example: query = "cola and pop", found = ["coca cola", "coca cola"]
        for synonym, main_product in sorted(self.synonyms.items(), key=lambda x: -len(x[0])):
            # Find all occurrences of the synonym in the query
            # Example: query = "cola and pop" -> matches = ["cola", "pop"]
            matches = re.findall(r'\b' + re.escape(synonym) + r'\b', query_lower)
            # If found, append the main product name to the list
            # Example: found = ["coca cola", "coca cola"]
            if matches:
                found.extend([main_product] * len(matches))
        # Combine the original query with the found main product names
        if found:
            # Join the original query with the found main product names
            # Example: expanded_query = "cola and pop coca cola coca cola"
            expanded_query = query_lower + " " + " ".join(found)
        else:
            # If no synonyms were found, return the original query
            expanded_query = query_lower
        print(f"Expanded Query: {expanded_query}")
        # Return the expanded query
        return expanded_query

    # Add a method to perform fuzzy matching
    # How to use: match = fuzzy_match("coca cola", ["coca cola", "pepsi", "sprite"])
    # Output: "coca cola" (Score: 100), since "coca cola" is an exact match
    # Purpose: To find the best fuzzy match for a query.
    def fuzzy_match(self, query, choices, threshold=75):
        """Finds best fuzzy match for a query."""
        # Use process.extractOne to find the best match (Only one result is needed)
        # The result is a tuple containing the best match and its score
        match, score = process.extractOne(query, choices)
        print(f"Fuzzy Match: {match} (Score: {score})")
        # Return the match if the score is above the threshold, else return the original query
        return match if score >= threshold else query

    # Add a method to extract products from the query
    def extract_products(self, query):
        """
        Attempts to extract product names directly from the query.
        Looks for both the main product names and any synonyms.
        Returns a list including all occurrences (duplicates) of matches.
        """
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        # Will store all product names found in the query
        found = []
        # Check for direct matches with main product names using regex
        for product in self.items.keys():
            # Find all occurrences of the product name in the query
            # Example: query = "cola and pop", matches = ["cola"]
            matches = re.findall(r'\b' + re.escape(product) + r'\b', query_lower)
            if matches:
                found.extend([product] * len(matches))
        
        # Check for synonyms and map them to the main product
        for synonym, main_product in self.synonyms.items():
            # Find all occurrences of the synonym in the query
            # Example: query = "cola and pop", matches = ["cola", "pop"]
            matches = re.findall(r'\b' + re.escape(synonym) + r'\b', query_lower)
            if matches:
                found.extend([main_product] * len(matches))
        
        print(f"Extracted Products: {found}")
        # Return all product names found in the query
        return found

    # Method to recommend items based on the query
    # How to use: recommendItems("I want to buy some cola and pop", threshold=0.5, topK=5)
    def recommendItems(self, userQuery, threshold=0.5, topK=5):
        """
        Returns recommendations based on the query.
        Process:
          1. Clean the query.
          2. Identify domain keywords in the query and get their recommendations.
          3. Remove domain keywords from the query.
          4. Process the remainder (via synonym expansion, extraction, and semantic search).
          5. Combine both sets of recommendations.
        """
        # Step 1: Clean query
        # Remove leading/trailing whitespaces and convert to lowercase
        # Example: userQuery = "  I want to buy some Cola and Pop  "
        # Output: cleaned_query = "i want to buy some cola and pop"
        cleaned_query = userQuery.strip().lower()
        print(f"Cleaned Query: {cleaned_query}")
        
        # Step 2: Identify domain keywords anywhere in the query.
        # Example: userQuery = "i want to buy some cola and pop"
        # Output: domains_found = ['beverages']
        domains_found = []
        for domain in self.domain_to_products:
            if re.search(r'\b' + re.escape(domain) + r'\b', cleaned_query):
                domains_found.append(domain)
        
        # Get recommendations for each domain found
        # Input: ['beverages']
        # Output: ['coca cola, 2', 'pepsi, 2', ...]
        domain_recommendations = []
        if domains_found:
            domain_products = []
            # Get all products for each domain found
            for domain in domains_found:
                # Extend the list of products with the products for the current domain
                # Input: ['beverages']
                # Output: ['coca cola', 'pepsi', ...]
                domain_products.extend(self.domain_to_products[domain])
            # Remove duplicates while preserving order
            # Input: ['coca cola', 'pepsi', 'coca cola', ...]
            # Output: ['coca cola', 'pepsi', ...]
            domain_products = list(dict.fromkeys(domain_products))
            domain_recommendations = [f"{p}, {self.items[p]}" for p in domain_products]
            print(f"Domain(s) found: {domains_found}\nDomain Products: {domain_recommendations}\n")
        
        # Step 3: Remove domain keywords from the cleaned query.
        # Example: cleaned_query = "i want to buy some beverages and flour"
        # Output: query_without_domains = "i want to buy some and flour"
        query_without_domains = cleaned_query
        for domain in domains_found:
            # Remove domain keyword from the query
            query_without_domains = re.sub(r'\b' + re.escape(domain) + r'\b', '', query_without_domains)
        query_without_domains = query_without_domains.strip()
        print(f"Query without domains: {query_without_domains}")
        
        # Step 4: Process remaining query for product extraction and semantic search.
        # Logic:
        # 1. If query_without_domains is not empty, expand the query with synonyms.
        # 2. Extract products from the expanded query.
        product_recommendations = []
        # If the query without domains is not empty
        if query_without_domains:
            # Expand the query with synonyms
            expanded_query = self.expand_query(query_without_domains)
            # Extract products from the expanded query
            # Example: expanded_query = "i want to buy some and flour"
            # Output: extracted = ['flour']
            extracted = self.extract_products(expanded_query)
            # If products are extracted, recommend them using semantic search
            if extracted:
                # For each extracted product, recommend similar products
                for prod in extracted:
                    # Perform fuzzy matching to find the best match
                    fuzzy_prod = self.fuzzy_match(prod, self.item_names)
                    # Perform semantic search to find similar products using embeddings and cosine similarity (model)
                    queryEmbedding = self.model.encode(fuzzy_prod, convert_to_tensor=True)
                    cosineScores = util.cos_sim(queryEmbedding, self.itemEmbeddings)[0]
                    topResults = np.argpartition(-cosineScores.cpu().numpy(), range(topK))[:topK]
                    # Get product recommendations based on the cosine similarity threshold
                    # Example:
                    # self.item_names = ["apple", "banana", "milk", "bread", "coffee"]
                    # self.items = {"apple": 15, "banana": 10, "milk": 20, "bread": 25, "coffee": 30}
                    # cosineScores = [0.4, 0.45, 0.5, 0.35, 0.48]  # Similarity scores for each product
                    # threshold = 0.5  # Minimum required similarity score
                    # 
                    # Step 1: Find the top-K highest similarity scores
                    # topResults = [2]  # Only "milk" was selected as it has the highest score (>= threshold)
                    #
                    # Step 2: Filter products based on the threshold
                    rec_for_prod = [
                        f"{self.item_names[idx]}, {self.items[self.item_names[idx]]}" 
                        for idx in topResults if cosineScores[idx] >= threshold
                    ]
                    # Extend the list of product recommendations with the recommendations for the current product
                    # Example: product_recommendations = ['flour, 3', 'bread, 2', ...]
                    product_recommendations.extend(rec_for_prod)
                # Remove duplicates while preserving order
                product_recommendations = list(dict.fromkeys(product_recommendations))
                print(f"Expanded Query: {expanded_query}\nExtracted: {extracted}\nProduct Recommendations: {product_recommendations}\n")
            # If no products are extracted, provide fallback recommendations
            else:
                # Perform fuzzy matching on the expanded query
                fuzzy_query = self.fuzzy_match(expanded_query, self.item_names)
                # Perform semantic search to find similar products using embeddings and cosine similarity (model)
                queryEmbedding = self.model.encode(fuzzy_query, convert_to_tensor=True)
                # Calculate cosine similarity scores between the query embedding and all item embeddings
                cosineScores = util.cos_sim(queryEmbedding, self.itemEmbeddings)[0]
                topResults = np.argpartition(-cosineScores.cpu().numpy(), range(topK))[:topK]
                product_recommendations = [
                    f"{self.item_names[idx]}, {self.items[self.item_names[idx]]}" 
                    for idx in topResults if cosineScores[idx] >= threshold
                ]
                print(f"Expanded Query: {expanded_query}\nExtracted: {extracted}\nFallback Product Recommendations: {product_recommendations}\n")
        
        # Step 5: Combine domain and product recommendations.
        final_recommendations = domain_recommendations + product_recommendations
        final_recommendations = list(dict.fromkeys(final_recommendations))
        print(f"Final Recommendations: {final_recommendations}\n")
        return final_recommendations
