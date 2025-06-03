from dataclasses import dataclass
from typing import Optional, List
from .ingredient import Ingredient

@dataclass
class Meal:
    id: int
    name: str
    category: str
    instructions: str
    ingredients: List[Ingredient]
    rating: Optional[float] = None
    review_count: Optional[int] = None
    estimated_cost: Optional[float] = None
    prep_time: Optional[int] = None  # in minutes
    servings: Optional[int] = None
    keywords: Optional[List[str]] = None
    image_url: Optional[str] = None
    is_recommended: Optional[bool] = None
    recommendation_score: Optional[float] = None

