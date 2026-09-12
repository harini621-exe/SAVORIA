"""
Ingredient Analyzer Agent
Processes and normalises user-provided ingredient lists.
"""

import re
from typing import List, Dict, Any, Tuple


class IngredientAnalyzer:
    """
    Normalises, deduplicates, and categorises user ingredient input.
    Prepares structured ingredient data for downstream agents.
    """

    # Common pantry/staple ingredients that are almost always available
    PANTRY_STAPLES = {
        "salt", "pepper", "black pepper", "water", "oil", "olive oil",
        "vegetable oil", "sugar", "flour", "baking powder", "baking soda",
        "vinegar", "soy sauce",
    }

    # Ingredient category mapping for dietary analysis
    CATEGORIES = {
        "protein": ["chicken", "beef", "pork", "lamb", "salmon", "fish", "tuna",
                    "eggs", "egg", "tofu", "tempeh", "lentils", "chickpeas",
                    "beans", "turkey", "shrimp", "prawns"],
        "dairy": ["milk", "cheese", "butter", "cream", "yoghurt", "yogurt",
                  "mozzarella", "feta", "cheddar", "parmesan", "ricotta"],
        "grain": ["rice", "pasta", "bread", "flour", "oats", "quinoa", "noodles",
                  "tortilla", "pita", "couscous", "barley"],
        "vegetable": ["onion", "garlic", "tomato", "carrot", "broccoli", "spinach",
                      "pepper", "mushroom", "zucchini", "cucumber", "celery",
                      "potato", "sweet potato", "cabbage", "lettuce", "kale"],
        "fruit": ["lemon", "lime", "orange", "apple", "banana", "berries",
                  "avocado", "tomato"],
        "spice": ["cumin", "turmeric", "paprika", "cinnamon", "chilli", "ginger",
                  "coriander", "oregano", "thyme", "basil", "bay leaf"],
    }

    def __init__(self):
        self._category_lookup = {}
        for cat, items in self.CATEGORIES.items():
            for item in items:
                self._category_lookup[item.lower()] = cat

    def normalise(self, ingredient: str) -> str:
        """Clean and normalise a single ingredient string."""
        ingredient = ingredient.strip().lower()
        # Remove quantities and units at the start (e.g., "2 cups flour" → "flour")
        ingredient = re.sub(
            r"^\d+[\d./]*\s*(cups?|tbsp|tsp|g|kg|ml|l|oz|lbs?|pieces?|cloves?)?\s*",
            "",
            ingredient,
            flags=re.IGNORECASE,
        )
        # Remove parenthetical notes
        ingredient = re.sub(r"\(.*?\)", "", ingredient).strip()
        return ingredient

    def process(self, raw_ingredients: List[str]) -> Dict[str, Any]:
        """
        Process raw ingredient list into structured analysis.

        Returns:
            {
                "normalised": List[str],          # cleaned ingredient names
                "categories": Dict[str, List],    # grouped by category
                "is_staple": Dict[str, bool],     # which are pantry staples
                "unique_count": int,
            }
        """
        normalised = []
        seen = set()
        for raw in raw_ingredients:
            if not raw or not raw.strip():
                continue
            norm = self.normalise(raw)
            if norm and norm not in seen:
                normalised.append(norm)
                seen.add(norm)

        categories: Dict[str, List[str]] = {cat: [] for cat in self.CATEGORIES}
        categories["other"] = []
        is_staple = {}

        for ing in normalised:
            is_staple[ing] = ing in self.PANTRY_STAPLES
            found_cat = False
            for keyword, cat in self._category_lookup.items():
                if keyword in ing or ing in keyword:
                    categories[cat].append(ing)
                    found_cat = True
                    break
            if not found_cat:
                categories["other"].append(ing)

        return {
            "normalised": normalised,
            "categories": {k: v for k, v in categories.items() if v},
            "is_staple": is_staple,
            "unique_count": len(normalised),
        }

    def validate(self, ingredients: List[str]) -> Tuple[bool, str]:
        """Return (is_valid, error_message). Ingredients must be non-empty."""
        if not ingredients:
            return False, "Please provide at least one ingredient."
        non_empty = [i for i in ingredients if i.strip()]
        if not non_empty:
            return False, "Please provide at least one non-empty ingredient."
        if len(non_empty) < 1:
            return False, "Please provide at least one ingredient to get recipe suggestions."
        return True, ""
