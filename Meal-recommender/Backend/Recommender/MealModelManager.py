from Backend.Recommender.Multiple_linear_regression import MultipleLinearRegressionModel
from Backend.Data.MealFeatureManager import MealFeatureManager
from Backend.Data.MealDataManager import MealDataManager
import pandas as pd
import pickle
import os

class MealModelManager:
    """Manages training and persistence of ML models."""

    def __init__(self):
        self.feature_manager = MealFeatureManager()
        self.data_manager = MealDataManager()
        self.prep_time_model = MultipleLinearRegressionModel()
        self.models_dir = "models"  # Directory to save trained models
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)

    def train_prep_time_model(self, limit: int = 1000) -> bool:
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