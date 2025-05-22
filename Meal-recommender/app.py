from Backend.Data.data_merger import DataMerger

def main():
    csv_file = r"C:\Users\Anton\Documents\Meal Recommender\Meal-recommender\data\raw\mercadona_products_latest.csv"
    processor = DataMerger(csv_file)

    processed_products = processor.get_enriched_meals("cucumber")
    for product in processed_products:
        print(f"Product: {product.name}")
        print(f"Category: {product.category}")
        print(f"Instructions: {product.instructions}")
        print(f"Estimated Cost: {product.estimated_cost}")
        print("Ingredients:")
        for ingredient in product.ingredients:
            print(f"- {ingredient.name}: {ingredient.amount} (Price per unit: {ingredient.price_per_unit})")
        print("\n")

if __name__ == "__main__":
    main()
