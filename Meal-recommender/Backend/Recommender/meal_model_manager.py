from Backend.Recommender.multiple_linear_regression import MultipleLinearRegressionModel
from Backend.Recommender.logistic_regression import LogisticRegressionModel
from Backend.Data.meal_feature_manager import MealFeatureManager
from Backend.Data.meal_data_manager import MealDataManager
import pandas as pd
import pickle
import os
import traceback

class MealModelManager:
    """Manages training and persistence of ML models."""

    def __init__(self):
        self.feature_manager = MealFeatureManager()
        self.data_manager = MealDataManager()
        self.prep_time_model = MultipleLinearRegressionModel()
        self.recommendation_model = LogisticRegressionModel()
        self.models_dir = "models"  # Directory to save trained models
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)

    def train_prep_time_model(self, limit: int = 10000) -> bool:
        """Train the preparation time prediction model."""
        try:
            if not self.data_manager.can_train():
                print("No training data available.")
                return False
            
            training_data = self.feature_manager.get_prep_time_features(self.data_manager.get_all_training_meals(), include_target=True)

            if training_data.empty:
                return False
            
            X_test, y_test, y_pred = self.prep_time_model.train_model_with_sgd(training_data, limit=limit)
            
            # Save the trained model
            self.save_model(self.prep_time_model, "prep_time_model.pkl")
            return True
            
        except Exception as e:
            print(f"Error training prep time model: {e}")
            return False
        
    def train_recommendation_model(self, limit: int = 10000) -> bool:
        """Train the recommendation model."""
        try:
            if not self.data_manager.can_train():
                print("No training data available.")
                return False
            
            training_data = self.feature_manager.get_recommendation_features(self.data_manager.get_all_training_meals(), include_target=True)

            if training_data.empty:
                return False
            
            self.recommendation_model.train_and_evaluate(training_data, 
                                                feature_names=[
                                                "ingredient_count", 
                                                "instruction_length", 
                                                "type_of_meal",
                                                "is_vegetarian", 
                                                "has_dairy", 
                                                "has_gluten",
                                                "prep_time",
                                                "flavor_profile",
                                                "complexity_score"
                                                ], 
                                                target_name="is_recommended",
                                                max_iter=limit)
            
            # Save the trained model
            self.save_model(self.recommendation_model, "recommendation_model.pkl")
            return True
            
        except Exception as e:
            print(f"Error training recommendation model: {e}")
            traceback.print_exc()
            return False
        
    def save_model(self, model, filename: str):
        """Save a trained model to disk."""
        filepath = os.path.join(self.models_dir, filename)
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)

    def load_model(self, filename: str):
        """Load a trained model from disk."""
        filepath = os.path.join(self.models_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return None
    
    def model_exists(self, filename: str) -> bool:
        """Check if a model file exists."""
        filepath = os.path.join(self.models_dir, filename)
        return os.path.exists(filepath)
    
    def get_prep_time_model(self):
        """Get the prep time model (load if exists, train if not)."""
        # Try to load existing model first
        model = self.load_model("prep_time_model.pkl")
        if model:
            self.prep_time_model = model
            return self.prep_time_model
        
        # If no saved model, train a new one
        print("No existing prep time model found. Training a new one...")
        if self.train_prep_time_model():
            return self.prep_time_model
        
        return None
    
    def get_recommendation_model(self):
        """Get the recommendation model (load if exists, train if not)."""
        # Try to load existing model first
        model = self.load_model("recommendation_model.pkl")
        if model:
            self.recommendation_model = model
            return self.recommendation_model
        
        # If no saved model, train a new one
        print("No existing recommendation model found. Training a new one...")
        if self.train_recommendation_model():
            return self.recommendation_model
        
        return None