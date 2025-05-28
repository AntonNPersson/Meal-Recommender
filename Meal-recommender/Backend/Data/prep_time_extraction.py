import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from ..models.meal import Meal

class PrepTimeFeatureExtractor:
    def __init__(self):
        self.prep_keywords = [
            "chop", "slice", "dice", "mince", "grate", "peel", "wash",
            "soak", "marinate", "mix", "stir", "blend", "whisk", "beat",
            "fold", "knead", "roll", "shape", "oven", "bake", "fry", "boil",
            "steam", "roast", "grill", "sear", "sauté", "cook", "prepare",
            "european", "asian", "american", "mexican", "indian", "mediterranean",
            "stove top", "slow cooker", "pressure cooker", "air fryer", "microwave"
        ]
        self.fresh_ingredients = [
            'onion', 'garlic', 'tomato', 'pepper', 'herb', 'lemon', 'lime',
            'cucumber', 'carrot', 'celery', 'spinach', 'broccoli', 'cauliflower',
            'zucchini', 'eggplant', 'mushroom', 'green bean', 'peas', 'corn',
            'potato', 'sweet potato', 'pumpkin', 'squash', 'radish', 'beet'
        ]

    def extract_features_from_meals(self, meals: List[Meal]) -> List[Dict]:
        """Extract features from any list of Meal objects."""
        if not meals:
            return []

        features = []
        
        for meal in meals:
            instruction_text = meal.instructions.lower() if meal.instructions else ""
            fresh_count = sum(
                ingredient.name.lower() in self.fresh_ingredients 
                for ingredient in meal.ingredients
            )
            fresh_ratio = fresh_count / len(meal.ingredients) if meal.ingredients else 0

            # Check if meal has keywords attribute (training data might have this)
            keyword_count = sum(
                instruction_text.count(keyword) for keyword in self.prep_keywords
            )
            
            if hasattr(meal, 'keywords') and meal.keywords:
                keyword_count += sum(
                    meal.keywords.count(keyword) for keyword in self.prep_keywords
                )

            feature = {
                "ingredient_count": len(meal.ingredients),
                "instruction_length": len(instruction_text.split()),
                "prep_keyworks_count": keyword_count,
                "fresh_ratio": fresh_ratio
            }

            # Add target variable if this is training data
            if hasattr(meal, 'prep_time') and meal.prep_time is not None:
                feature["prep_time_target"] = meal.prep_time

            features.append(feature)
        
        return features

    def prepare_features_dataframe(self, meals: List[Meal], include_target: bool = False) -> pd.DataFrame:
        """Convert meals to feature DataFrame."""
        features = self.extract_features_from_meals(meals)
        if not features:
            return pd.DataFrame()

        df = pd.DataFrame(features)
        
        # Separate features and target
        feature_columns = ["ingredient_count", "instruction_length", "prep_keyworks_count", "fresh_ratio"]
        
        if include_target and "prep_time_target" in df.columns:
            # For training - include target
            return df[feature_columns + ["prep_time_target"]].fillna(0)
        else:
            # For prediction - only features
            return df[feature_columns].fillna(0)

    def estimate_prep_time_heuristic(self, features: Dict) -> Optional[int]:
        """Heuristic-based prep time estimation (fallback method)."""
        if not features:
            return None
        
        base_time = features['ingredient_count'] * 2
        instruction_time = min(features['instruction_length'] / 50, 20)
        
        if features['prep_keyworks_count'] > 0:
            instruction_time += features['prep_keyworks_count'] * 2

        fresh_time = features['fresh_ratio'] * 3
        estimated_time = int(base_time + instruction_time + fresh_time)
        
        # Add some randomness and bounds
        noise = np.random.randint(0, 5)
        total_time = max(5, min(120, estimated_time + noise))
        
        return total_time