from Backend.Recommender.Multiple_linear_regression import MultipleLinearRegressionModel
from Backend.Data.data_merger import DataMerger
from Backend.Data.meal_feature_extractions import MealFeatureExtractor
import pandas as pd

class MealPredictionService:
    def __init__(self, limit: int = 1000):
        self.mercadona_csv_file_path = r"C:\Users\Anton\Documents\Meal Recommender\Meal-recommender\data\raw\mercadona_products_latest.csv"
        self.food_csv_file_path = r"C:\Users\Anton\Documents\Meal Recommender\Meal-recommender\data\raw\recipes.csv"
        self.feature_extractor = MealFeatureExtractor(
            mercadona_csv_path=self.mercadona_csv_file_path,
            food_csv_path=self.food_csv_file_path,
            training_limit=limit
        )
        self.mlr_model = MultipleLinearRegressionModel()
        self.data_merger = DataMerger(
            mercadona_csv_file_path=self.mercadona_csv_file_path,
            food_csv_file_path=self.food_csv_file_path,
            training_limit=limit
        )

    def prepare_model(self, limit: int = 1000) -> list:
        """
        Predict meal preparation times using the trained model.
        """
        # Extract features from training data
        training_features = self.feature_extractor.extract_training_features(limit=limit)
        if not training_features:
            return []

        # Prepare DataFrame for model training
        df = self.feature_extractor.prepare_training_data(limit=limit)
        if df.empty:
            return []

        # Train the model and get predictions
        X_test, y_test, y_pred = self.mlr_model.train_model_with_sgd(df)

    def get_enriched_meals(self, search_term: str) -> list:
        """
        Get enriched meals based on a search term.
        """
        enriched_meals = self.data_merger.get_enriched_meals(search_term)
        
        if not enriched_meals or len(enriched_meals) == 0:
            return None
        
        # Extract features for enriched meals
        enriched_features = self.feature_extractor.extract_features_from_meals(enriched_meals)

        if not enriched_features or len(enriched_features) == 0:
            return None
        
        # Calculate preparation times for enriched meals
        df = pd.DataFrame(enriched_features)
        df.fillna(0, inplace=True)
        enriched_prep_times = self.mlr_model.predict(df)

        if enriched_prep_times is None or len(enriched_prep_times) == 0:
            return None
        
        # Combine enriched meals with their predicted preparation times
        for meal, prep_time in zip(enriched_meals, enriched_prep_times):
            meal.prep_time = round(prep_time, 2) if prep_time is not None else None

        return enriched_meals