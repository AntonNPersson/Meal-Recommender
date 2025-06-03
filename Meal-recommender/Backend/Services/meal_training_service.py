from Backend.Recommender.meal_model_manager import MealModelManager

class MealTrainingService:
    """Service for training meal-related models."""

    def __init__(self):
        self.model_manager = MealModelManager()

    def train_prep_time_model(self, limit: int = 1000) -> bool:
        """Train the preparation time model with a specified limit."""
        return self.model_manager.train_prep_time_model(limit=limit)
    
    def train_recommendation_model(self, limit: int = 1000) -> bool:
        """Train the recommendation model with a specified limit."""
        return self.model_manager.train_recommendation_model(limit=limit)
    
    def train_all_models(self, limit: int = 1000) -> bool:
        """Train all models with a specified limit."""
        try:
            if not self.train_prep_time_model(limit=limit):
                print("Failed to train preparation time model.")
                return False
            
            if not self.train_recommendation_model(limit=limit):
                print("Failed to train recommendation model.")
                return False
            
            return True
        except Exception as e:
            print(f"Error during model training: {e}")
            return False