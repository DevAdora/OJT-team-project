from sentence_transformers import SentenceTransformer, util
import numpy as np

# Load a pre-trained model (adjust the model name if needed)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Read and preprocess your dataset (each line is an item)
with open('unique_items.txt', 'r') as f:
    items = [line.strip() for line in f if line.strip()]

# Precompute embeddings for all items (cache these for performance)
item_embeddings = model.encode(items, convert_to_tensor=True)

def recommend_items(user_query, threshold=0.5, top_k=5):
    """
    Computes the semantic similarity between the user query and the dataset items.
    Returns the top matching items whose similarity score is above the threshold.
    """
    # Compute embedding for the user query
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    
    # Compute cosine similarities between query and each item embedding
    cosine_scores = util.cos_sim(query_embedding, item_embeddings)[0]
    
    # Get indices of the top-k highest scoring items
    top_results = np.argpartition(-cosine_scores, range(top_k))[:top_k]
    recommended = []
    for idx in top_results:
        if cosine_scores[idx] >= threshold:
            recommended.append(items[idx])
    return recommended

# Example usage
while True:
    user_query = input("Enter your query (type 'exit' to quit): ")
    recommended = recommend_items(user_query)
    print("Recommended items:", recommended)
    if user_query.lower() == 'exit':
        break