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
        self.synonyms = {}
        self.domain_to_products = {}
        with open(synonymsFile, 'r') as f:
            for line in f:
                parts = line.strip().split(': ')
                if len(parts) == 2:
                    main_product, syns = parts[0].lower(), parts[1].split(', ')
                    domain = syns[-1].lower()
                    for synonym in syns:
                        self.synonyms[synonym.lower()] = main_product
                    if domain not in self.domain_to_products:
                        self.domain_to_products[domain] = []
                    if main_product not in self.domain_to_products[domain]:
                        self.domain_to_products[domain].append(main_product)

    def expand_query(self, query):
        """Expands query with synonyms by appending all main product names found."""
        query_lower = query.lower()
        found = []
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
        """Extracts product names from query, including synonyms."""
        query_lower = query.lower()
        found = []
        for product in self.items.keys():
            matches = re.findall(r'\b' + re.escape(product) + r'\b', query_lower)
            if matches:
                found.extend([product] * len(matches))
        for synonym, main_product in self.synonyms.items():
            matches = re.findall(r'\b' + re.escape(synonym) + r'\b', query_lower)
            if matches:
                found.extend([main_product] * len(matches))
        print(f"Extracted Products: {found}")
        return found

    def recommendItems(self, userQuery, threshold=0.5, topK=5):
        """Returns recommendations based on query, including semantic search for unmatched words."""
        cleaned_query = userQuery.strip().lower()
        print(f"Cleaned Query: {cleaned_query}")
        
        domains_found = [domain for domain in self.domain_to_products if re.search(r'\b' + re.escape(domain) + r'\b', cleaned_query)]
        domain_recommendations = []
        if domains_found:
            domain_products = []
            for domain in domains_found:
                domain_products.extend(self.domain_to_products[domain])
            domain_products = list(dict.fromkeys(domain_products))
            domain_recommendations = [f"{p}, {self.items[p]}" for p in domain_products]
            print(f"Domain(s) found: {domains_found}\nDomain Products: {domain_recommendations}\n")

        query_without_domains = cleaned_query
        for domain in domains_found:
            query_without_domains = re.sub(r'\b' + re.escape(domain) + r'\b', '', query_without_domains)
        query_without_domains = query_without_domains.strip()
        print(f"Query without domains: {query_without_domains}")

        product_recommendations = []
        unmatched_terms = []
        
        if query_without_domains:
            expanded_query = self.expand_query(query_without_domains)
            extracted_products = self.extract_products(expanded_query)
            words = set(expanded_query.split())
            unmatched_terms = words - set(extracted_products)
            print(f"Extracted Products: {extracted_products}")
            print(f"Unmatched Terms (for semantic search): {unmatched_terms}")
            
            for prod in extracted_products:
                fuzzy_prod = self.fuzzy_match(prod, self.item_names)
                queryEmbedding = self.model.encode(fuzzy_prod, convert_to_tensor=True)
                cosineScores = util.cos_sim(queryEmbedding, self.itemEmbeddings)[0]
                topResults = np.argpartition(-cosineScores.cpu().numpy(), range(topK))[:topK]
                rec_for_prod = [f"{self.item_names[idx]}, {self.items[self.item_names[idx]]}" 
                                for idx in topResults if cosineScores[idx] >= threshold]
                product_recommendations.extend(rec_for_prod)
            
            for term in unmatched_terms:
                queryEmbedding = self.model.encode(term, convert_to_tensor=True)
                cosineScores = util.cos_sim(queryEmbedding, self.itemEmbeddings)[0]
                topResults = np.argpartition(-cosineScores.cpu().numpy(), range(topK))[:topK]
                rec_for_term = [f"{self.item_names[idx]}, {self.items[self.item_names[idx]]}" 
                                for idx in topResults if cosineScores[idx] >= threshold]
                product_recommendations.extend(rec_for_term)

            product_recommendations = list(dict.fromkeys(product_recommendations))
            print(f"Final Product Recommendations: {product_recommendations}\n")

        final_recommendations = domain_recommendations + product_recommendations
        final_recommendations = list(dict.fromkeys(final_recommendations))
        print(f"Final Recommendations: {final_recommendations}\n")
        
        return final_recommendations
