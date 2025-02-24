from sentence_transformers import SentenceTransformer, util
import numpy as np

class GroceryStoreRecommender:
    def __init__(self, modelName='all-MiniLM-L6-v2', dataFile='productsDataset.txt'):
        # Load a pre-trained model
        self.model = SentenceTransformer(modelName)

        # Read and preprocess your dataset (each line is an item)
        with open(dataFile, 'r') as f:
            self.items = [line.strip() for line in f if line.strip()]

        # Precompute embeddings for all items (cache these for performance)
        self.itemEmbeddings = self.model.encode(self.items, convert_to_tensor=True)

    def recommendItems(self, userQuery, threshold=0.5, topK=5):
        """
        Computes the semantic similarity between the user query and the dataset items.
        Returns the top matching items whose similarity score is above the threshold.
        """
        # Compute embedding for the user query
        queryEmbedding = self.model.encode(userQuery, convert_to_tensor=True)

        # Compute cosine similarities between query and each item embedding
        cosineScores = util.cos_sim(queryEmbedding, self.itemEmbeddings)[0]

        # Get indices of the top-k highest scoring items
        topResults = np.argpartition(-cosineScores, range(topK))[:topK]
        recommended = []
        for idx in topResults:
            if cosineScores[idx] >= threshold:
                recommended.append(self.items[idx])
        return recommended