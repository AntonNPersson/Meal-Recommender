from typing import List, Dict, Optional
import time
import requests

class SpoonacularAPI:
    def __init__(self, api_key = Optional[str]):
        self.base_url = "https://api.spoonacular.com/recipes"
        self.api_key = api_key

        self.last_request = 0
        self.request_interval = 1

    def _rate_limit(self):
        current_time = time.time()
        if current_time - self.last_request < self.request_interval:
            time.sleep(self.request_interval - (current_time - self.last_request))
        self.last_request = time.time()

    def _make_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict:
        if params is None:
            params = {}

        if 'apiKey' in params and not params['apiKey']:
            raise ValueError("API key is required for Spoonacular API requests.")

        params['apiKey'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        self._rate_limit()

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429 or response.status_code == 402:
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"An error occurred while making the request: {e}")
        
    def search_by_ingredients(self, ingredients: List[str], number: int = 1000) -> List[Dict]:
        """Find recipes using specific ingredients (Spoonacular)."""
        params = {
            'ingredients': ','.join(ingredients),
            'number': min(number, 100),
            'ranking': 1,  # Maximize used ingredients
            'ignorePantry': True
        }
        
        data = self._make_request('findByIngredients', params)
        if data:
            # Add source info
            for recipe in data:
                recipe['source'] = 'spoonacular'
            return data
        return []
    
    def search_by_category(self, category: str, number: int = 1000) -> List[Dict]:
        """Find recipes by category (Spoonacular)."""
        params = {
            'type': category,
            'number': min(number, 100)
        }
        
        data = self._make_request('random', params)
        if data and 'recipes' in data:
            # Add source info
            for recipe in data['recipes']:
                recipe['source'] = 'spoonacular'
            return data['recipes']
        return []