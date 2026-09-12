"""
Preference Analyzer Agent
Processes and validates user dietary preferences and meal constraints.
"""

from typing import Optional, Dict, Any, List


DIETARY_OPTIONS = [
    "vegetarian", "vegan", "gluten-free", "dairy-free",
    "high-protein", "low-carb", "low-spice", "nut-free",
]

CUISINE_OPTIONS = [
    "Italian", "Indian", "Mexican", "Asian", "Chinese", "Japanese",
    "Mediterranean", "Middle Eastern", "French", "European",
    "American", "Contemporary", "Thai", "Greek",
]

MEAL_TYPE_OPTIONS = ["breakfast", "lunch", "dinner", "snack"]


class PreferenceAnalyzer:
    """
    Validates and structures user meal preferences and dietary restrictions.
    Provides context for recipe retrieval and generation.
    """

    def process(
        self,
        dietary_preference: Optional[str],
        cuisine_preference: Optional[str],
        meal_type: Optional[str],
        cooking_time_minutes: Optional[int],
        servings: Optional[int],
        avoid_ingredients: Optional[List[str]],
    ) -> Dict[str, Any]:
        """
        Process and normalise all preference fields.

        Returns structured preference context dictionary.
        """
        return {
            "dietary_preference": self._normalise_dietary(dietary_preference),
            "cuisine_preference": self._normalise_cuisine(cuisine_preference),
            "meal_type": self._normalise_meal_type(meal_type),
            "cooking_time_minutes": self._validate_time(cooking_time_minutes),
            "servings": self._validate_servings(servings),
            "avoid_ingredients": [a.strip().lower() for a in (avoid_ingredients or []) if a.strip()],
        }

    def _normalise_dietary(self, pref: Optional[str]) -> Optional[str]:
        if not pref or not pref.strip():
            return None
        pref = pref.strip().lower()
        # Alias normalisation
        aliases = {
            "veg": "vegetarian", "veggie": "vegetarian",
            "plant-based": "vegan", "no-gluten": "gluten-free",
            "no dairy": "dairy-free", "lactose free": "dairy-free",
            "lactose-free": "dairy-free", "protein": "high-protein",
        }
        return aliases.get(pref, pref)

    def _normalise_cuisine(self, cuisine: Optional[str]) -> Optional[str]:
        if not cuisine or not cuisine.strip():
            return None
        return cuisine.strip().title()

    def _normalise_meal_type(self, meal_type: Optional[str]) -> Optional[str]:
        if not meal_type or not meal_type.strip():
            return None
        return meal_type.strip().lower()

    def _validate_time(self, minutes: Optional[int]) -> Optional[int]:
        if minutes is None:
            return None
        return max(5, min(minutes, 480))  # clamp between 5 and 480 minutes

    def _validate_servings(self, servings: Optional[int]) -> int:
        if not servings or servings < 1:
            return 2
        return min(servings, 20)

    def build_context_string(self, preferences: Dict[str, Any]) -> str:
        """Build a human-readable preference summary for prompt construction."""
        parts = []
        if preferences.get("dietary_preference"):
            parts.append(f"Dietary requirement: {preferences['dietary_preference']}")
        if preferences.get("cuisine_preference"):
            parts.append(f"Cuisine preference: {preferences['cuisine_preference']}")
        if preferences.get("meal_type"):
            parts.append(f"Meal type: {preferences['meal_type']}")
        if preferences.get("cooking_time_minutes"):
            parts.append(f"Available cooking time: {preferences['cooking_time_minutes']} minutes")
        if preferences.get("servings"):
            parts.append(f"Servings needed: {preferences['servings']}")
        if preferences.get("avoid_ingredients"):
            parts.append(f"Ingredients to avoid: {', '.join(preferences['avoid_ingredients'])}")
        return "\n".join(parts) if parts else "No specific preferences."
