from dataclasses import dataclass
from typing import Optional, List
from .ingredient import Ingredient

@dataclass
class Meal:
    id: int
    name: str
    category: str
    ingredients: List[Ingredient]
    instructions: str
    estimated_cost: Optional[float] = None
    prep_time: Optional[int] = None  # in minutes
    servings: Optional[int] = None
    keywords: Optional[List[str]] = None
    image_url: Optional[str] = None

