import re
import pandas as pd

def parse_r_vector(r_string):
    """
    Convert R c() syntax to Python list
    
    Input: 'c("blueberries", "granulated sugar", "vanilla yogurt", "lemon juice")'
    Output: ['blueberries', 'granulated sugar', 'vanilla yogurt', 'lemon juice']
    """
    if not r_string or pd.isna(r_string):
        return []
    
    r_string = str(r_string).strip()
    
    # Check if it's R vector syntax
    if not (r_string.startswith('c(') and r_string.endswith(')')):
        return []
    
    # Remove 'c(' and ')'
    content = r_string[2:-1]
    
    # Handle empty vectors
    if not content.strip():
        return []
    
    # Split by comma, but be careful with commas inside quotes
    ingredients = []
    current_item = ""
    in_quotes = False
    quote_char = None
    
    i = 0
    while i < len(content):
        char = content[i]
        
        if not in_quotes:
            if char in ['"', "'"]:
                in_quotes = True
                quote_char = char
            elif char == ',' and not in_quotes:
                # End of current item
                item = current_item.strip()
                if item:
                    ingredients.append(item)
                current_item = ""
            else:
                current_item += char
        else:
            if char == quote_char:
                # Check if it's escaped quote
                if i + 1 < len(content) and content[i + 1] == quote_char:
                    # Escaped quote, add one quote and skip next
                    current_item += char
                    i += 1
                else:
                    # End of quoted string
                    in_quotes = False
                    quote_char = None
            else:
                current_item += char
        
        i += 1
    
    # Add the last item
    item = current_item.strip()
    if item:
        ingredients.append(item)
    
    # Clean up each ingredient (remove quotes and extra spaces)
    cleaned_ingredients = []
    for ing in ingredients:
        ing = ing.strip()
        # Remove surrounding quotes
        if (ing.startswith('"') and ing.endswith('"')) or (ing.startswith("'") and ing.endswith("'")):
            ing = ing[1:-1]
        cleaned_ingredients.append(ing.strip())
    
    return cleaned_ingredients

def parse_r_vector_to_string(r_string):
    """
    Convert R c() syntax to a single string of ingredients
    
    Input: 'c("blueberries", "granulated sugar", "vanilla yogurt", "lemon juice")'
    Output: 'blueberries. granulated sugar. vanilla yogurt. lemon juice'
    """
    ingredients = parse_r_vector(r_string)
    return ' '.join(ingredients) if ingredients else ''

def parse_r_vector_simple(r_string):
    """
    Simpler version using regex - works for most cases
    """
    if not r_string or pd.isna(r_string):
        return []
    
    r_string = str(r_string).strip()
    
    # Check if it's R vector syntax
    if not (r_string.startswith('c(') and r_string.endswith(')')):
        return []
    
    # Extract content between c( and )
    content = r_string[2:-1]
    
    # Find all quoted strings
    pattern = r'"([^"]*)"'
    matches = re.findall(pattern, content)
    
    # If no double quotes, try single quotes
    if not matches:
        pattern = r"'([^']*)'"
        matches = re.findall(pattern, content)
    
    return matches

def parse_ISO_8601_duration(duration: str) -> int:
    """
    Parse ISO 8601 duration format (e.g., 'PT30M' for 30 minutes) into total minutes.
    
    :param duration: ISO 8601 duration string
    :return: Total duration in minutes
    """
    if not duration or pd.isna(duration):
        return 0
    
    # Remove 'PT' prefix
    content = duration[2:]
    
    total_minutes = 0
    
    # Extract hours
    hour_match = re.search(r'(\d+)H', content)
    if hour_match:
        total_minutes += int(hour_match.group(1)) * 60
    
    # Extract minutes
    minute_match = re.search(r'(\d+)M', content)
    if minute_match:
        total_minutes += int(minute_match.group(1))
    
    return total_minutes