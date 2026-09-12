"""
Dietary Adaptation Module
Adjusts recipe context and generation prompts based on dietary preferences.
"""

from typing import Dict, Any, List, Optional


# Adaptation rules for dietary preferences
DIETARY_ADAPTATIONS: Dict[str, Dict[str, Any]] = {
    "vegetarian": {
        "avoid_ingredients": ["chicken", "beef", "pork", "lamb", "fish", "salmon", "tuna",
                               "turkey", "bacon", "ham", "shrimp", "prawns", "gelatin"],
        "substitutes": {
            "chicken": "paneer or chickpeas",
            "beef": "mushrooms or lentils",
            "pork": "tofu or tempeh",
            "fish": "tofu or jackfruit",
            "shrimp": "mushrooms or hearts of palm",
        },
        "instructions": "Ensure the recipe contains no meat, poultry, or seafood. Use plant-based protein alternatives.",
    },
    "vegan": {
        "avoid_ingredients": ["chicken", "beef", "pork", "lamb", "fish", "salmon", "tuna",
                               "turkey", "bacon", "eggs", "milk", "cream", "butter", "cheese",
                               "yoghurt", "honey", "gelatin", "whey"],
        "substitutes": {
            "eggs": "flax eggs or chia eggs",
            "milk": "oat milk or almond milk",
            "cream": "coconut cream",
            "butter": "coconut oil or vegan margarine",
            "cheese": "nutritional yeast or vegan cheese",
            "honey": "maple syrup or agave",
            "chicken": "tofu, tempeh, or chickpeas",
            "beef": "lentils or mushrooms",
        },
        "instructions": "The recipe must be fully plant-based with no animal products including dairy, eggs, or honey.",
    },
    "gluten-free": {
        "avoid_ingredients": ["flour", "wheat flour", "bread flour", "pasta", "soy sauce",
                               "bread", "tortilla", "pita", "couscous", "barley", "rye",
                               "breadcrumbs"],
        "substitutes": {
            "soy sauce": "tamari (gluten-free soy sauce)",
            "pasta": "rice pasta or rice noodles",
            "flour": "rice flour or almond flour",
            "bread": "gluten-free bread",
            "breadcrumbs": "crushed gluten-free crackers or almond flour",
            "couscous": "quinoa",
        },
        "instructions": "Ensure all ingredients are gluten-free. Use tamari instead of soy sauce, and gluten-free flour/pasta.",
    },
    "dairy-free": {
        "avoid_ingredients": ["milk", "cream", "butter", "cheese", "yoghurt", "mozzarella",
                               "parmesan", "feta", "ricotta", "ghee", "whey"],
        "substitutes": {
            "milk": "oat milk or almond milk",
            "cream": "coconut cream",
            "butter": "coconut oil or olive oil",
            "cheese": "vegan cheese or nutritional yeast",
            "yoghurt": "coconut yoghurt",
            "mozzarella": "vegan mozzarella",
        },
        "instructions": "Remove all dairy products. Use plant-based alternatives for milk, cream, butter, and cheese.",
    },
    "high-protein": {
        "avoid_ingredients": [],
        "substitutes": {},
        "instructions": "Emphasise protein-rich ingredients such as chicken, fish, eggs, tofu, lentils, or chickpeas. Suggest protein additions where natural.",
    },
    "low-carb": {
        "avoid_ingredients": ["pasta", "rice", "bread", "sugar", "tortilla", "couscous", "oats"],
        "substitutes": {
            "pasta": "zucchini noodles or shirataki noodles",
            "rice": "cauliflower rice",
            "bread": "lettuce wraps",
            "tortilla": "lettuce wraps or low-carb tortilla",
        },
        "instructions": "Minimise carbohydrates. Suggest low-carb alternatives for rice, pasta, and bread.",
    },
    "low-spice": {
        "avoid_ingredients": ["chilli", "chilli powder", "red chilli flakes", "cayenne", "jalapeño",
                               "sriracha", "hot sauce"],
        "substitutes": {
            "chilli powder": "sweet paprika",
            "red chilli flakes": "a pinch of black pepper",
            "cayenne": "mild paprika",
        },
        "instructions": "Use minimal spice. Replace hot chilli with mild sweet paprika or black pepper.",
    },
}


class DietaryAdapter:
    """
    Adapts recipe context and generation instructions based on dietary preferences.
    """

    def get_adaptation(self, dietary_preference: Optional[str]) -> Optional[Dict[str, Any]]:
        """Return the adaptation ruleset for a given dietary preference."""
        if not dietary_preference:
            return None
        return DIETARY_ADAPTATIONS.get(dietary_preference.lower())

    def build_adaptation_prompt(self, dietary_preference: Optional[str]) -> str:
        """Build specific dietary adaptation instructions for the generation prompt."""
        if not dietary_preference:
            return ""
        adaptation = self.get_adaptation(dietary_preference)
        if not adaptation:
            return f"Please adapt the recipe to be suitable for {dietary_preference} requirements."

        lines = [f"DIETARY ADAPTATION — {dietary_preference.upper()}:"]
        lines.append(adaptation["instructions"])

        if adaptation["substitutes"]:
            lines.append("\nRequired substitutions:")
            for original, substitute in list(adaptation["substitutes"].items())[:5]:
                lines.append(f"  - Replace {original} with {substitute}")

        return "\n".join(lines)

    def check_recipe_compatibility(
        self, recipe: Dict[str, Any], dietary_preference: Optional[str]
    ) -> Dict[str, Any]:
        """
        Check if a recipe is compatible with a dietary preference.
        Returns compatibility status and problematic ingredients.
        """
        if not dietary_preference:
            return {"compatible": True, "issues": [], "adaptable": True}

        adaptation = self.get_adaptation(dietary_preference)
        if not adaptation:
            return {"compatible": True, "issues": [], "adaptable": True}

        recipe_ingredients = [
            ing["name"].lower() for ing in recipe.get("ingredients", [])
        ]
        avoid = [a.lower() for a in adaptation["avoid_ingredients"]]

        issues = []
        for ing in recipe_ingredients:
            for avoid_item in avoid:
                if avoid_item in ing or ing in avoid_item:
                    issues.append(ing)
                    break

        adaptable = all(
            any(avoid_item in str(adaptation["substitutes"]).lower() for avoid_item in [issue])
            for issue in issues
        ) if issues else True

        return {
            "compatible": len(issues) == 0,
            "issues": issues,
            "adaptable": adaptable or len(issues) <= 3,
        }
