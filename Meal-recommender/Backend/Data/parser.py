import re
from typing import Tuple, Optional

class ProductNameParser:
    def __init__(self):
        self.volume_patterns = [
            r"(\d+(\.\d+)?)\s*(ml|l|milliliters|liters)",
            r"(\d+(\.\d+)?)\s*(oz|ounces)",
            r"(\d+(\.\d+)?)\s*(cup|cups)",
            r"(\d+(\.\d+)?)\s*(tbsp|tablespoon|tablespoons)",
            r"(\d+(\.\d+)?)\s*(tsp|teaspoon|teaspoons)",
            r'(\d+(?:,\d+)?)\s*º', # Oil acidity
            r'pack\s*(\d+)', # Pack size
            r'(\d+)\s*ml\s*pack', # Pack size
            r'(\d+)\s*uds?', # Units
        ]

        self.brands = ["hacendado", "mercadona", "carrefour", "dia", "alcampo", "lidl", "aldi", "spar", "el corte ingles"]

    def parse_product_name(self, product_name: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Parse product name into: (clean_name, volume, brand)
        
        Example: "Aceite de oliva 0,4º Hacendado" 
        Returns: ("aceite de oliva", "0,4º", "hacendado")
        """
        original = product_name.lower()
        
        # Extract volume/size
        volume = self._extract_volume(original)
        
        # Extract brand
        brand = self._extract_brand(original)
        
        # Clean the product name
        clean_name = self._clean_name(original, volume, brand)
        
        return clean_name, volume, brand

    def _extract_volume(self, name: str) -> Optional[str]:
        """Extract volume/weight from product name"""
        for pattern in self.volume_patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_brand(self, name: str) -> Optional[str]:
        """Extract brand name from product"""
        for brand in self.brands:
            if brand in name.lower():
                return brand
        return None

    def _clean_name(self, name: str, volume: str = None, brand: str = None) -> str:
        """Remove volume and brand info to get clean product name"""
        clean = name.lower()

        if volume:
            clean = clean.replace(volume, '').strip()

        if brand:
            clean = clean.replace(brand, '').strip()

        # Remove any remaining special characters
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', clean)
        # Remove extra spaces  
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean