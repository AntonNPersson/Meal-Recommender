from deep_translator import GoogleTranslator
import re

class IngredientTranslator:
    """
    A class to translate ingredient names between different languages.
    """

    def __init__(self):
        # Manual mapping for common Spanish ingredients
        self.spanish_to_english = {
            # Vegetables
            'patata': 'potato',
            'patatas': 'potato',
            'tomate': 'tomato',
            'tomates': 'tomato',
            'cebolla': 'onion',
            'cebollas': 'onion',
            'ajo': 'garlic',
            'ajos': 'garlic',
            'zanahoria': 'carrot',
            'zanahorias': 'carrot',
            'pimiento': 'pepper',
            'pimientos': 'pepper',
            'pepino': 'cucumber',
            'pepinos': 'cucumber',
            'lechuga': 'lettuce',
            'espinaca': 'spinach',
            'espinacas': 'spinach',
            'calabacín': 'zucchini',
            'calabaza': 'pumpkin',
            'berenjena': 'eggplant',
            'brócoli': 'broccoli',
            'coliflor': 'cauliflower',
            'apio': 'celery',
            
            # Proteins
            'pollo': 'chicken',
            'pechuga': 'chicken breast',
            'muslo': 'chicken thigh',
            'jamón': 'ham',
            'cerdo': 'pork',
            'ternera': 'veal',
            'vacuno': 'beef',
            'cordero': 'lamb',
            'pescado': 'fish',
            'salmón': 'salmon',
            'atún': 'tuna',
            'bacalao': 'cod',
            'merluza': 'hake',
            'gambas': 'shrimp',
            'langostinos': 'prawns',
            'mejillones': 'mussels',
            'almejas': 'clams',
            'pulpo': 'octopus',
            'solomillo': 'tenderloin',
            'pavo': 'turkey',
            'chorizo': 'chorizo',
            'salchichón': 'salami',
            'salchicha': 'sausage',
            
            # Grains and legumes
            'arroz': 'rice',
            'pasta': 'pasta',
            'fideos': 'noodles',
            'macarrones': 'macaroni',
            'espaguetis': 'spaghetti',
            'lentejas': 'lentils',
            'garbanzos': 'chickpeas',
            'alubias': 'beans',
            'judías': 'beans',
            'pan': 'bread',
            'harina': 'flour',
            'avena': 'oats',
            
            # Dairy
            'leche': 'milk',
            'queso': 'cheese',
            'mantequilla': 'butter',
            'yogur': 'yogurt',
            'nata': 'cream',
            'huevo': 'egg',
            'huevos': 'eggs',
            
            # Fruits
            'manzana': 'apple',
            'manzanas': 'apple',
            'naranja': 'orange',
            'naranjas': 'orange',
            'plátano': 'banana',
            'plátanos': 'banana',
            'limón': 'lemon',
            'limones': 'lemon',
            'fresa': 'strawberry',
            'fresas': 'strawberry',
            'uva': 'grape',
            'uvas': 'grape',
            'pera': 'pear',
            'peras': 'pear',
            'melocotón': 'peach',
            'kiwi': 'kiwi',
            'piña': 'pineapple',
            'mango': 'mango',
            
            # Oils and condiments
            'aceite': 'oil',
            'aceite de oliva': 'olive oil',
            'vinagre': 'vinegar',
            'sal': 'salt',
            'pimienta': 'pepper',
            'azúcar': 'sugar',
            'miel': 'honey',
            'mostaza': 'mustard',
            'mayonesa': 'mayonnaise',
            'ketchup': 'ketchup',
            
            # Herbs and spices
            'perejil': 'parsley',
            'cilantro': 'cilantro',
            'albahaca': 'basil',
            'orégano': 'oregano',
            'tomillo': 'thyme',
            'romero': 'rosemary',
            'laurel': 'bay leaf',
            'canela': 'cinnamon',
            'comino': 'cumin',
            'pimentón': 'paprika',
            'ñora': 'ñora pepper',
            
            # Nuts
            'almendra': 'almond',
            'almendras': 'almond',
            'nuez': 'walnut',
            'nueces': 'walnut',
            'pistacho': 'pistachio',
            'pistachos': 'pistachio',
            'cacahuete': 'peanut',
            'cacahuetes': 'peanut',
            'avellana': 'hazelnut',
            'avellanas': 'hazelnut',
            
            # Common processed foods
            'conserva': 'canned',
            'congelado': 'frozen',
            'fresco': 'fresh',
            'seco': 'dried',
            'molido': 'ground',
            'troceado': 'chopped',
            'entero': 'whole',
            'filetes': 'fillets',
            'rodajas': 'slices',

            # Extras
            'salsa': 'sauce',
            'sopas': 'soups',
            'crema': 'cream',
            'caldo': 'broth',
            'pasta de curry': 'curry paste',
            'sazonador': 'seasoning',
            'aderezo': 'dressing',
            'snack': 'snack',
            'aperitivo': 'appetizer',
            'galleta': 'cookie',
            'galletas': 'cookies',
            'chocolate': 'chocolate',
            'caramelo': 'candy',
            'chicle': 'gum',
            'pizza': 'pizza',
            'hamburguesa': 'burger',
            'perrito caliente': 'hot dog',
            'tortilla': 'omelette',
            'tortilla de patatas': 'Spanish omelette',
            'tortilla española': 'Spanish omelette',
            'tortilla de maíz': 'corn tortilla',
            'tortilla de trigo': 'wheat tortilla',
            'cava': 'sparkling wine',
            'vino': 'wine',
            'cerveza': 'beer',
            'sidra': 'cider',
            'tinto de verano': 'red wine spritzer',
            'sangría': 'sangria',
            'Café': 'coffee',
            'té': 'tea',
            'infusión': 'herbal tea',
            'filetes de pescado': 'fish fillets',
            'filetes de pollo': 'chicken fillets',
            'filetes de ternera': 'beef fillets',
            'filetes de cerdo': 'pork fillets',
            'filetes de pavo': 'turkey fillets',
            'filetes de cordero': 'lamb fillets',
            'filetes de pechuga': 'chicken breast fillets',
            'filetes de solomillo': 'tenderloin fillets',
            'filetes pechuga de pollo': 'chicken breast fillets',
            'filetes de pechuga de pavo': 'turkey breast fillets',
        }

    def translate_ingredient(self, ingredient: str, src_lang: str = 'spanish') -> str:
        """
        Translate an ingredient from source language to English.
        Uses manual mapping first, then falls back to Google Translate.
        """
        if src_lang.lower() in ['spanish', 'es', 'spa']:
            return self._translate_from_spanish(ingredient)
        else:
            # For other languages, use Google Translate directly
            return None

    def _translate_from_spanish(self, ingredient: str) -> str:
        """
        Translate Spanish ingredient to English using manual mapping first.
        """
        clean_ingredient = ingredient.lower().strip()
        
        # First, try exact match
        if clean_ingredient in self.spanish_to_english:
            return self.spanish_to_english[clean_ingredient]
        
        # Try partial matches for compound ingredients like "patata de bravas"
        for spanish_term, english_term in self.spanish_to_english.items():
            if spanish_term in clean_ingredient:
                return english_term
        
        # Remove common descriptors and try again
        clean_ingredient = self._remove_descriptors(clean_ingredient)
        if clean_ingredient in self.spanish_to_english:
            return self.spanish_to_english[clean_ingredient]
        
        # Try partial match again after cleaning
        for spanish_term, english_term in self.spanish_to_english.items():
            if spanish_term in clean_ingredient:
                return english_term
        
        # Fall back to Spanish
        return None

    def _remove_descriptors(self, ingredient: str) -> str:
        """
        Remove common descriptors to get the base ingredient.
        """
        # Common descriptors to remove
        descriptors = [
            'de', 'con', 'sin', 'a', 'la', 'del', 'para', 'en',
            'fresco', 'seco', 'congelado', 'troceado', 'entero',
            'grande', 'pequeño', 'mediano', 'fino', 'grueso',
            'dulce', 'salado', 'picante', 'suave', 'extra',
            'natural', 'ecológico', 'bio', 'light'
        ]
        
        words = ingredient.split()
        # Keep the first word (main ingredient) and remove descriptors
        filtered_words = [word for word in words if word not in descriptors]
        if filtered_words:
            return filtered_words[0]  # Return the main ingredient
        else:
            return ingredient

    def _translate_with_google(self, ingredient: str, src_lang: str) -> str:
        """
        Translate using Google Translate as fallback.
        """
        try:
            translated_text = GoogleTranslator(source=src_lang, target='en').translate(ingredient.lower())
            return translated_text.lower()
        except Exception as e:
            print(f"Error translating ingredient '{ingredient}': {e}")
            return ingredient.lower()

    def add_custom_mapping(self, spanish_term: str, english_term: str):
        """
        Add a custom mapping to the dictionary.
        """
        self.spanish_to_english[spanish_term.lower()] = english_term.lower()

    def get_mapping_stats(self):
        """
        Get statistics about the current mapping.
        """
        return {
            'total_mappings': len(self.spanish_to_english),
            'categories': {
                'vegetables': len([k for k in self.spanish_to_english.keys() 
                                if k in ['patata', 'tomate', 'cebolla', 'ajo', 'zanahoria']]),
                'proteins': len([k for k in self.spanish_to_english.keys() 
                               if k in ['pollo', 'cerdo', 'pescado', 'jamón']]),
                'fruits': len([k for k in self.spanish_to_english.keys() 
                             if k in ['manzana', 'naranja', 'plátano', 'limón']])
            }
        }

            


