from dataclasses import dataclass
from typing import Optional, List

@dataclass
class User:
    id: int
    prefered_flavors: Optional[List[str]] = None
    prefered_types: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
