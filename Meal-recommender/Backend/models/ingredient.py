from dataclasses import dataclass
from typing import Optional

@dataclass
class Ingredient:
    name: str
    amount: str
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None