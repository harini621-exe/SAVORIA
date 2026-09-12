"""
Substitution Advisor Agent
Provides practical ingredient substitution recommendations.
"""

from typing import List, Dict, Any, Optional


# Curated substitution knowledge base
SUBSTITUTION_KNOWLEDGE: Dict[str, List[Dict[str, str]]] = {
    "butter": [
        {"substitute": "coconut oil", "guidance": "3/4 the amount", "effect": "Slight coconut flavour; makes it dairy-free"},
        {"substitute": "olive oil", "guidance": "3/4 the amount", "effect": "Better for savoury dishes; dairy-free"},
        {"substitute": "margarine", "guidance": "equal amount", "effect": "Closest texture; check dairy-free labels"},
    ],
    "milk": [
        {"substitute": "oat milk", "guidance": "equal amount", "effect": "Mildly sweet; excellent in most recipes"},
        {"substitute": "almond milk", "guidance": "equal amount", "effect": "Lighter flavour; dairy-free"},
        {"substitute": "coconut milk", "guidance": "equal amount", "effect": "Adds richness; dairy-free"},
    ],
    "eggs": [
        {"substitute": "flax egg (1 tbsp ground flax + 3 tbsp water)", "guidance": "1 per egg; rest 5 mins", "effect": "Vegan; works for baking"},
        {"substitute": "chia egg (1 tbsp chia + 3 tbsp water)", "guidance": "1 per egg; rest 5 mins", "effect": "Vegan; slight texture"},
        {"substitute": "mashed banana (1/4 cup)", "guidance": "per egg", "effect": "Adds sweetness; best for baked goods"},
    ],
    "cream": [
        {"substitute": "coconut cream", "guidance": "equal amount", "effect": "Dairy-free; adds subtle coconut flavour"},
        {"substitute": "cashew cream", "guidance": "equal amount", "effect": "Neutral flavour; vegan"},
        {"substitute": "evaporated milk", "guidance": "equal amount", "effect": "Lower fat; richer than regular milk"},
    ],
    "soy sauce": [
        {"substitute": "tamari", "guidance": "equal amount", "effect": "Gluten-free; very similar flavour"},
        {"substitute": "coconut aminos", "guidance": "equal amount", "effect": "Soy-free; slightly sweeter"},
        {"substitute": "fish sauce", "guidance": "1/2 the amount", "effect": "Adds umami; not vegetarian"},
    ],
    "parmesan": [
        {"substitute": "nutritional yeast", "guidance": "2-3 tbsp per 50g", "effect": "Vegan; cheesy umami flavour"},
        {"substitute": "pecorino romano", "guidance": "equal amount", "effect": "Sharper; saltier"},
        {"substitute": "grana padano", "guidance": "equal amount", "effect": "Milder; very similar"},
    ],
    "heavy cream": [
        {"substitute": "coconut cream", "guidance": "equal amount", "effect": "Dairy-free; slight coconut note"},
        {"substitute": "greek yoghurt", "guidance": "equal amount", "effect": "Tangy; do not boil"},
        {"substitute": "evaporated milk", "guidance": "equal amount", "effect": "Less rich; lower fat"},
    ],
    "bread flour": [
        {"substitute": "all-purpose flour", "guidance": "equal amount", "effect": "Slightly less chewy structure"},
        {"substitute": "plain flour", "guidance": "equal amount", "effect": "Works well; slightly softer"},
    ],
    "tahini": [
        {"substitute": "peanut butter", "guidance": "equal amount", "effect": "Different but pleasant nutty flavour"},
        {"substitute": "sunflower seed butter", "guidance": "equal amount", "effect": "Nut-free; similar texture"},
        {"substitute": "almond butter", "guidance": "equal amount", "effect": "Mildly sweet; nutty"},
    ],
    "lemon juice": [
        {"substitute": "lime juice", "guidance": "equal amount", "effect": "Slightly more floral acidity"},
        {"substitute": "white wine vinegar", "guidance": "half the amount", "effect": "More acidic; no citrus flavour"},
        {"substitute": "apple cider vinegar", "guidance": "half the amount", "effect": "Mild fruity acidity"},
    ],
    "garlic": [
        {"substitute": "garlic powder", "guidance": "1/4 tsp per clove", "effect": "Less pungent; convenient"},
        {"substitute": "shallots", "guidance": "1/2 shallot per clove", "effect": "Milder, sweeter flavour"},
        {"substitute": "asafoetida (hing)", "guidance": "pinch", "effect": "Strong; use very sparingly"},
    ],
    "ginger": [
        {"substitute": "ground ginger", "guidance": "1/4 tsp per 1 tsp fresh", "effect": "Less bright; more mellow"},
        {"substitute": "galangal", "guidance": "equal amount", "effect": "More piney; common in Thai cooking"},
    ],
    "fresh coriander": [
        {"substitute": "fresh parsley", "guidance": "equal amount", "effect": "Different herb flavour; similar freshness"},
        {"substitute": "fresh basil", "guidance": "equal amount", "effect": "Sweeter herb note"},
        {"substitute": "dried coriander", "guidance": "1/3 the amount", "effect": "Less bright; use as garnish"},
    ],
    "chickpeas": [
        {"substitute": "cannellini beans", "guidance": "equal amount", "effect": "Softer texture; milder flavour"},
        {"substitute": "lentils", "guidance": "equal amount", "effect": "Different texture; cook faster"},
        {"substitute": "butter beans", "guidance": "equal amount", "effect": "Creamy; good for dips"},
    ],
    "tomato passata": [
        {"substitute": "blended canned tomatoes", "guidance": "equal amount", "effect": "Same result; blend and strain"},
        {"substitute": "tomato purée diluted with water", "guidance": "1 tbsp purée + 150ml water per 200ml", "effect": "More concentrated; adjust seasoning"},
    ],
    "mozzarella": [
        {"substitute": "vegan mozzarella", "guidance": "equal amount", "effect": "Dairy-free; melts less smoothly"},
        {"substitute": "provolone", "guidance": "equal amount", "effect": "Slightly stronger flavour"},
        {"substitute": "fontina", "guidance": "equal amount", "effect": "Creamier and richer"},
    ],
    "feta": [
        {"substitute": "ricotta salata", "guidance": "equal amount", "effect": "Milder and less salty"},
        {"substitute": "tofu feta (marinated firm tofu)", "guidance": "equal amount", "effect": "Vegan; use marinated tofu"},
        {"substitute": "goat cheese", "guidance": "equal amount", "effect": "Tangier and creamier"},
    ],
}


class SubstitutionAdvisor:
    """
    Provides ingredient substitution recommendations from a curated knowledge base.
    Used both as a standalone tool and as part of recipe generation context.
    """

    def get_substitutions(
        self,
        ingredient: str,
        available_ingredients: Optional[List[str]] = None,
        dietary_preference: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Look up substitutions for an ingredient.
        Prioritises substitutes the user already has if available_ingredients provided.
        """
        ingredient_lower = ingredient.lower().strip()

        # Direct match
        subs = SUBSTITUTION_KNOWLEDGE.get(ingredient_lower, [])

        # Partial match
        if not subs:
            for key, val in SUBSTITUTION_KNOWLEDGE.items():
                if key in ingredient_lower or ingredient_lower in key:
                    subs = val
                    break

        if not subs:
            return []

        # Filter by dietary preference
        if dietary_preference:
            pref = dietary_preference.lower()
            if pref in ("vegan", "dairy-free"):
                subs = [
                    s for s in subs
                    if "dairy-free" in s.get("effect", "").lower()
                    or "vegan" in s.get("effect", "").lower()
                ] or subs  # fall back to all if none match

        # Prioritise subs the user has
        if available_ingredients:
            available_lower = {a.lower() for a in available_ingredients}
            subs_with_availability = []
            for sub in subs:
                sub_name = sub["substitute"].split("(")[0].strip().lower()
                has_it = any(
                    sub_name in avail or avail in sub_name
                    for avail in available_lower
                )
                subs_with_availability.append({**sub, "_has_ingredient": has_it})
            subs_with_availability.sort(key=lambda x: x["_has_ingredient"], reverse=True)
            subs = [{k: v for k, v in s.items() if k != "_has_ingredient"} for s in subs_with_availability]

        return subs[:3]  # Return top 3 substitutions

    def build_substitution_context(self, recipe: Dict[str, Any], available_ingredients: List[str]) -> str:
        """Build a substitution context string for prompt construction."""
        available_lower = {a.lower() for a in available_ingredients}
        missing = []

        for ing in recipe.get("ingredients", []):
            name = ing["name"].lower()
            if not any(name in avail or avail in name for avail in available_lower):
                missing.append(ing["name"])

        if not missing:
            return "All main ingredients are available. No substitutions needed."

        lines = [f"Missing ingredients and suggested substitutes:"]
        for m in missing[:5]:  # limit to 5 for prompt length
            subs = self.get_substitutions(m, list(available_lower))
            if subs:
                sub_str = "; or ".join(
                    f"{s['substitute']} ({s['guidance']})" for s in subs[:2]
                )
                lines.append(f"- {m}: substitute with {sub_str}")
            else:
                lines.append(f"- {m}: no standard substitute found; may be omitted or sourced separately")

        return "\n".join(lines)
