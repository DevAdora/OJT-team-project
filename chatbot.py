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
        self.synonyms = {}
        self.domain_to_products = {}
        with open(synonymsFile, 'r') as f:
            for line in f:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    main_product, syns = parts[0].lower(), parts[1].split(', ')
                    # The last element is assumed to be the domain keyword.
                    domain = syns[-1].lower()
                    # Map each synonym to the main product.
                    for synonym in syns:
                        self.synonyms[synonym.lower()] = main_product
                    # Build domain mapping: add main_product to the domain keyword's list.
                    if domain not in self.domain_to_products:
                        self.domain_to_products[domain] = []
                    if main_product not in self.domain_to_products[domain]:
                        self.domain_to_products[domain].append(main_product)

    def expand_query(self, query):
        """Expands query with synonyms by appending all main product names found.
           This ensures that if multiple synonyms occur, all are added to the query."""
        query_lower = query.lower()
        found = []
        # Sort synonyms by length (descending) to match multi-word phrases first
        for synonym, main_product in sorted(self.synonyms.items(), key=lambda x: -len(x[0])):
            matches = re.findall(r'\b' + re.escape(synonym) + r'\b', query_lower)
            if matches:
                found.extend([main_product] * len(matches))
        if found:
            expanded_query = query_lower + " " + " ".join(found)
        else:
            expanded_query = query_lower
        print(f"Expanded Query: {expanded_query}")
        return expanded_query

    def fuzzy_match(self, query, choices, threshold=75):
        """Finds best fuzzy match for a query."""
        match, score = process.extractOne(query, choices)
        print(f"Fuzzy Match: {match} (Score: {score})")
        return match if score >= threshold else query

    def extract_products(self, query):
        """
        Attempts to extract product names directly from the query.
        Looks for both the main product names and any synonyms.
        Returns a list including all occurrences (duplicates) of matches.
        """
        query_lower = query.lower()
        found = []
        # Check for direct matches with main product names using regex
        for product in self.items.keys():
            matches = re.findall(r'\b' + re.escape(product) + r'\b', query_lower)
            if matches:
                found.extend([product] * len(matches))
        
        # Check for synonyms and map them to the main product
        for synonym, main_product in self.synonyms.items():
            matches = re.findall(r'\b' + re.escape(synonym) + r'\b', query_lower)
            if matches:
                found.extend([main_product] * len(matches))
        
        print(f"Extracted Products: {found}")
        return found

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
        cleaned_query = userQuery.strip().lower()
        print(f"Cleaned Query: {cleaned_query}")
        
        # Step 2: Identify domain keywords anywhere in the query.
        domains_found = []
        for domain in self.domain_to_products:
            if re.search(r'\b' + re.escape(domain) + r'\b', cleaned_query):
                domains_found.append(domain)
        
        domain_recommendations = []
        if domains_found:
            domain_products = []
            for domain in domains_found:
                domain_products.extend(self.domain_to_products[domain])
            # Remove duplicates while preserving order
            domain_products = list(dict.fromkeys(domain_products))
            domain_recommendations = [f"{p}, {self.items[p]}" for p in domain_products]
            print(f"Domain(s) found: {domains_found}\nDomain Products: {domain_recommendations}\n")
        
        # Step 3: Remove domain keywords from the cleaned query.
        query_without_domains = cleaned_query
        for domain in domains_found:
            query_without_domains = re.sub(r'\b' + re.escape(domain) + r'\b', '', query_without_domains)
        query_without_domains = query_without_domains.strip()
        print(f"Query without domains: {query_without_domains}")
        
        # Step 4: Process remaining query for product extraction and semantic search.
        product_recommendations = []
        if query_without_domains:
            expanded_query = self.expand_query(query_without_domains)
            extracted = self.extract_products(expanded_query)
            if extracted:
                for prod in extracted:
                    fuzzy_prod = self.fuzzy_match(prod, self.item_names)
                    queryEmbedding = self.model.encode(fuzzy_prod, convert_to_tensor=True)
                    cosineScores = util.cos_sim(queryEmbedding, self.itemEmbeddings)[0]
                    topResults = np.argpartition(-cosineScores.cpu().numpy(), range(topK))[:topK]
                    rec_for_prod = [
                        f"{self.item_names[idx]}, {self.items[self.item_names[idx]]}" 
                        for idx in topResults if cosineScores[idx] >= threshold
                    ]
                    product_recommendations.extend(rec_for_prod)
                product_recommendations = list(dict.fromkeys(product_recommendations))
                print(f"Expanded Query: {expanded_query}\nExtracted: {extracted}\nProduct Recommendations: {product_recommendations}\n")
            else:
                fuzzy_query = self.fuzzy_match(expanded_query, self.item_names)
                queryEmbedding = self.model.encode(fuzzy_query, convert_to_tensor=True)
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
