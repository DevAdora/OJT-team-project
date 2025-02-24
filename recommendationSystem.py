from chatbot import GroceryStoreRecommender

def main():
    # Initialize the recommender system
    recommender = GroceryStoreRecommender()

    print("Welcome to the Grocery Store Recommender System!")
    print("Enter your queries to get recommendations. Type 'exit' to quit.")

    while True:
        userQuery = input("Enter your query: ")
        if userQuery.lower() == 'exit':
            print("Thank you for using the recommendation system. Goodbye!")
            break

        recommendedItems = recommender.recommendItems(userQuery)
        print(f"Recommended items: {recommendedItems}")
        print("-" * 40)

if __name__ == "__main__":
    main()