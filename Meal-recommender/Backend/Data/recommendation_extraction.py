import pandas as pd
from typing import Dict, List
from ..models.meal import Meal

class RecommendationFeatureExtraction:
    def __init__(self):
        # Cuisine-specific ingredients
        self.italian_ingredients = [
            "pasta", "tomato", "basil", "olive oil", "garlic", "cheese",
            "mozzarella", "parmesan", "spinach", "mushroom", "eggplant",
            "zucchini", "bell pepper", "onion", "carrot"
        ]
        self.mexican_ingredients = [
            "tortilla", "beans", "avocado", "cilantro", "lime", "chili",
            "corn", "tomato", "onion", "bell pepper", "cheese", "salsa"
        ]
        self.indian_ingredients = [
            "curry", "chicken", "lentils", "rice", "yogurt", "spices",
            "garlic", "ginger", "onion", "tomato", "cilantro", "peas"
        ]
        self.asian_ingredients = [
            "soy sauce", "ginger", "garlic", "rice", "noodles", "tofu",
            "bok choy", "carrot", "bell pepper", "scallion", "sesame oil"
        ]
        self.american_ingredients = [
            "burger", "beef", "chicken", "bacon", "cheese", "potato",
            "lettuce", "tomato", "onion", "bread", "ketchup", "mustard"
        ]
        self.mexican_ingredients = [
            "taco", "burrito", "enchilada", "quesadilla", "salsa", "guacamole",
            "jalapeño", "cilantro", "lime", "corn", "beans", "avocado"
        ]

        # flavor profiles
        self.sweet_ingredients = [
            "sugar", "honey", "maple syrup", "chocolate", "vanilla",
            "fruit", "cinnamon", "caramel", "brown sugar", "agave"
        ]
        self.savory_ingredients = [
            "salt", "pepper", "garlic", "onion", "soy sauce", "cheese",
            "bacon", "herbs", "spices", "olive oil", "butter", "mushroom"
        ]
        self.sour_ingredients = [
            "lemon", "lime", "vinegar", "yogurt", "sour cream", "pickles",
            "tomato", "cranberry", "tamarind", "pomegranate", "grapefruit"
        ]
        self.spicy_ingredients = [
            "chili", "jalapeño", "cayenne", "sriracha", "hot sauce",
            "ginger", "wasabi", "pepper flakes", "curry powder", "black pepper"
        ]
        self.comfort_ingredients = [
            "mac and cheese", "pizza", "burger", "fried chicken", "pasta",
            "butter", "cream", "cheese", "bacon", "chocolate", "ice cream"
        ]

        # Common dietary sources
        self.protein_sources = [
            "chicken", "beef", "pork", "tofu", "fish", "shrimp", "lentils",
            "beans", "eggs", "cheese"
        ]
        self.diary_sources = [
            "milk", "yogurt", "cheese", "cream", "butter", "sour cream"
        ]
        self.gluten_sources = [
            "bread", "pasta", "flour", "cereal", "barley", "rye", "oats"
        ]

        # Tequniques for meal preparation
        self.advanced_techniques = [
            "sous vide", "smoking", "fermentation", "pickling", "canning",
            "curing", "confiting", "dehydrating", "pressure cooking"
        ]

    def extract_features_from_meals(self, meals: List[Meal]) -> List[Dict]:
        """Extract features from any list of Meal objects."""

        if not meals:
            return []
        
        features = []

        for meal in meals:
            try:
                instruction_text = meal.instructions.lower() if meal.instructions else ""
                ingredient_names = [ingredient.name.lower() for ingredient in meal.ingredients]

                type_of_meal = self._extract_cuisine_type(ingredient_names)
                flavor_profile = self._extract_flavor_profile(ingredient_names)
                prep_time = meal.prep_time if hasattr(meal, 'prep_time') and meal.prep_time is not None else None
                complexity_score = self._calculate_complexity(instruction_text, meal.ingredients)

                is_vegetarian = all(
                    ingredient not in self.protein_sources for ingredient in ingredient_names
                )

                has_dairy = any(
                    ingredient in self.diary_sources for ingredient in ingredient_names
                )

                has_gluten = any(
                    ingredient in self.gluten_sources for ingredient in ingredient_names
                )

                ingredient_count = len(meal.ingredients)
                instruction_length = len(instruction_text.split())
                rating = meal.rating if hasattr(meal, 'rating') and meal.rating is not None else None

                feature = {
                    "ingredient_count": ingredient_count,
                    "instruction_length": instruction_length,
                    "type_of_meal": type_of_meal,
                    "is_vegetarian": is_vegetarian,
                    "has_dairy": has_dairy,
                    "has_gluten": has_gluten,
                    "prep_time": prep_time,
                    "flavor_profile": flavor_profile,
                    "complexity_score": complexity_score
                }

                # Add target variable if this is training data
                feature["is_recommended"] = self._create_target(
                    rating, 
                    review_count=meal.review_count if hasattr(meal, 'review_count') else 0
                )
                features.append(feature)
            except Exception as e:
                print(f"Error processing meal {meal.name if hasattr(meal, 'name') else 'Unknown'}: {e}")
                print("Skipping this meal due to error.")
                print("Meal data:", meal)
                import traceback
                traceback.print_exc()
                break
        return features
    
    def _extract_cuisine_type(self, ingredient_names: List[str]) -> str:
        """Determine the type of meal based on ingredient names."""
        cuisine_counts = {
            'italian': self._get_ingredient_counts(ingredient_names, self.italian_ingredients),
            'mexican': self._get_ingredient_counts(ingredient_names, self.mexican_ingredients),
            'indian': self._get_ingredient_counts(ingredient_names, self.indian_ingredients),
            'asian': self._get_ingredient_counts(ingredient_names, self.asian_ingredients),
            'american': self._get_ingredient_counts(ingredient_names, self.american_ingredients)
        }
        return max(cuisine_counts, key=cuisine_counts.get)
    
    def _extract_flavor_profile(self, ingredient_names: List[str]) -> str:
        """Determine the flavor profile based on ingredient names."""
        flavor_counts = {
            'sweet': self._get_ingredient_counts(ingredient_names, self.sweet_ingredients),
            'savory': self._get_ingredient_counts(ingredient_names, self.savory_ingredients),
            'sour': self._get_ingredient_counts(ingredient_names, self.sour_ingredients),
            'spicy': self._get_ingredient_counts(ingredient_names, self.spicy_ingredients),
            'comfort': self._get_ingredient_counts(ingredient_names, self.comfort_ingredients)
        }
        return max(flavor_counts, key=flavor_counts.get)
    
    def _calculate_complexity(self, instruction_text: str, ingredients) -> int:
        """Calculate complexity based on instruction text."""
        score = 0

        score += sum(2 for word in instruction_text.split() if word in self.advanced_techniques)
        score += len(instruction_text.split()) / 10  # Length of instructions
        score += len(ingredients) / 5  # Number of ingredients

        if "overnight" in instruction_text or "slow cooker" in instruction_text:
            score += 3


        return min(int(score), 10)  # Cap complexity score at 10

    def _get_ingredient_counts(self, ingredient_names: List, source_names: List) -> int:
        """Count the number of ingredients in a meal."""
        return sum(
            ingredient in ingredient_names for ingredient in source_names
        )
    
    def _create_target(self, rating, review_count=None):
        if rating is None:
            return None
        
        # Could add confidence based on review count
        if review_count and review_count < 1:
            return None  # Not enough data
        
        # Or use different thresholds
        if rating >= 3.0:
            return True
        else:
            return False
        
    def prepare_features_dataframe(self, meals: List[Meal], include_target: bool = False) -> pd.DataFrame:
        """Convert meals to feature DataFrame."""
        features = self.extract_features_from_meals(meals)
        if not features:
            return pd.DataFrame()
        
        df = pd.DataFrame(features)
        
        if include_target and "is_recommended" in df.columns:
            # Remove rows where target is None (insufficient data)
            original_count = len(df)
            df = df[df["is_recommended"].notna()]
            print(f"Filtered out {original_count - len(df)} meals with insufficient rating data")
            
            # Convert to int for sklearn
            df["is_recommended"] = df["is_recommended"].astype(int)
            print(f"Target distribution: {df['is_recommended'].value_counts()}")
            
            feature_columns = [
                "ingredient_count", "instruction_length", "type_of_meal",
                "is_vegetarian", "has_dairy", "has_gluten", "prep_time",
                "flavor_profile", "complexity_score"
            ]
            return df[feature_columns + ["is_recommended"]].fillna(0)
        else:
            # For prediction - only features
            feature_columns = [
                "ingredient_count", "instruction_length", "type_of_meal",
                "is_vegetarian", "has_dairy", "has_gluten", "prep_time",
                "flavor_profile", "complexity_score"
            ]
            return df[feature_columns].fillna(0)
        