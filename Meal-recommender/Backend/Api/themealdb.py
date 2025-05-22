import requests
from typing import List, Dict, Optional

class MealDBAPI:
    def __init__(self):
        self.base_url = "https://www.themealdb.com/api/json/v1/1/"

    def search_by_ingredient(self, ingredient: str) -> List[Dict]:
        url = f"{self.base_url}filter.php?i={ingredient}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("meals", [])
        else:
            print(f"Error: {response.status_code}")
            return []
        
    def get_meal_details(self, meal_id: str) -> Optional[Dict]:
        url = f"{self.base_url}lookup.php?i={meal_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("meals", [])[0] if data.get("meals") else None
        else:
            print(f"Error: {response.status_code}")
            return None
        
    def search_by_category(self, category: str) -> List[Dict]:
        url = f"{self.base_url}filter.php?c={category}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("meals", [])
        else:
            print(f"Error: {response.status_code}")
            return []
        
    