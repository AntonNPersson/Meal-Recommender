from Backend.Recommender.MealModelManager import MealModelManager

class MealTrainingService:
    """Service for training meal-related models."""

    def __init__(self):
        self.model_manager = MealModelManager()

    def train_prep_time_model(self, limit: int = 1000) -> bool:
        """Train the preparation time model with a specified limit."""
        return self.model_manager.train_prep_time_model(limit=limit)
    
    def train_all_models(self, limit: int = 1000) -> bool:
        """Train all models that require training."""
        try:
            if not self.train_prep_time_model(limit=limit):
                print("Failed to train preparation time model.")
                return False
            
            # Add more model training calls here as needed
            # e.g., self.train_other_model()
            
            return True
        except Exception as e:
            print(f"Error during model training: {e}")
            return False