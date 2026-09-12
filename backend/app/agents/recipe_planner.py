"""
Recipe Planner Agent
Orchestrates the full SAVORIA agentic workflow.
This is the central coordinator that calls all other agents in sequence.
"""

import logging
import uuid
from typing import List, Dict, Any

from app.agents.ingredient_analyzer import IngredientAnalyzer
from app.agents.preference_analyzer import PreferenceAnalyzer
from app.agents.recipe_generator import RecipeGenerator
from app.agents.substitution_advisor import SubstitutionAdvisor
from app.agents.dietary_adapter import DietaryAdapter
from app.rag.retriever import recipe_rag
from app.models.schemas import (
    RecipeRequest, RecipeResponse, RecipeListItem,
    Recipe, RecipeDetailResponse, IngredientItem, CookingStep,
    SubstitutionItem, WasteReduction, NutritionInfo,
)

logger = logging.getLogger(__name__)

ingredient_analyzer = IngredientAnalyzer()
preference_analyzer = PreferenceAnalyzer()
recipe_generator = RecipeGenerator()
substitution_advisor = SubstitutionAdvisor()
dietary_adapter = DietaryAdapter()


def _dict_to_recipe_list_item(r: Dict[str, Any]) -> RecipeListItem:
    """Convert a raw recipe dict to a RecipeListItem schema."""
    ingredients = r.get("ingredients", [])
    available_count = sum(1 for i in ingredients if i.get("available", False))
    match_score = r.get("_combined_score") or r.get("_match_ratio")
    if match_score is None and ingredients:
        match_score = available_count / len(ingredients)

    return RecipeListItem(
        id=r.get("id", str(uuid.uuid4())),
        name=r.get("name", ""),
        description=r.get("description", ""),
        cuisine=r.get("cuisine", ""),
        meal_type=r.get("meal_type", ""),
        difficulty=r.get("difficulty", "Medium"),
        cooking_time_minutes=r.get("cooking_time_minutes", 30),
        prep_time_minutes=r.get("prep_time_minutes", 10),
        servings=r.get("servings", 2),
        dietary_info=r.get("dietary_info", []),
        match_score=round(match_score, 2) if match_score is not None else None,
        ingredients_available=available_count,
        ingredients_total=len(ingredients),
        tags=r.get("tags", []),
    )


def _dict_to_recipe(r: Dict[str, Any]) -> Recipe:
    """Convert a raw recipe dict to a full Recipe schema."""
    ingredients = [
        IngredientItem(
            name=ing.get("name", ""),
            quantity=ing.get("quantity"),
            unit=ing.get("unit"),
            available=ing.get("available", True),
        )
        for ing in r.get("ingredients", [])
    ]
    steps = [
        CookingStep(
            step_number=s.get("step_number", i + 1),
            instruction=s.get("instruction", ""),
            required_ingredients=s.get("required_ingredients"),
            tip=s.get("tip"),
        )
        for i, s in enumerate(r.get("steps", []))
    ]
    substitutions = [
        SubstitutionItem(
            original=s.get("original", ""),
            substitute=s.get("substitute", ""),
            quantity_guidance=s.get("quantity_guidance"),
            effect_on_recipe=s.get("effect_on_recipe"),
        )
        for s in r.get("substitutions", [])
    ]

    waste = None
    if r.get("waste_reduction"):
        wr = r["waste_reduction"]
        waste = WasteReduction(
            ingredients_used=wr.get("ingredients_used", []),
            ingredients_leftover=wr.get("ingredients_leftover", []),
            leftover_suggestions=wr.get("leftover_suggestions"),
        )

    nutrition = None
    if r.get("nutrition"):
        n = r["nutrition"]
        nutrition = NutritionInfo(
            calories_per_serving=n.get("calories_per_serving"),
            protein=n.get("protein"),
            carbs=n.get("carbs"),
            fat=n.get("fat"),
        )

    available_count = sum(1 for ing in r.get("ingredients", []) if ing.get("available", False))
    match_score = r.get("_combined_score") or r.get("_match_ratio")
    if match_score is None and r.get("ingredients"):
        match_score = available_count / len(r["ingredients"])

    return Recipe(
        id=r.get("id", str(uuid.uuid4())),
        name=r.get("name", ""),
        description=r.get("description", ""),
        cuisine=r.get("cuisine", ""),
        meal_type=r.get("meal_type", ""),
        difficulty=r.get("difficulty", "Medium"),
        cooking_time_minutes=r.get("cooking_time_minutes", 30),
        prep_time_minutes=r.get("prep_time_minutes", 10),
        servings=r.get("servings", 2),
        dietary_info=r.get("dietary_info", []),
        ingredients=ingredients,
        steps=steps,
        substitutions=substitutions,
        cooking_tips=r.get("cooking_tips", []),
        waste_reduction=waste,
        nutrition=nutrition,
        match_score=round(match_score, 2) if match_score is not None else None,
        tags=r.get("tags", []),
    )


class RecipePlanner:
    """
    Central agentic coordinator implementing the SAVORIA workflow:
    
    User Input
    → Ingredient Analysis
    → Preference Analysis  
    → RAG Retrieval (FAISS)
    → Recipe Generation (IBM watsonx.ai)
    → Substitution & Dietary Adaptation
    → Structured Response
    """

    async def plan_recipes(self, request: RecipeRequest) -> RecipeResponse:
        """
        Full pipeline: analyse → retrieve → generate → structure.
        """
        # Step 1: Analyse ingredients
        ingredient_analysis = ingredient_analyzer.process(request.available_ingredients)
        valid, error_msg = ingredient_analyzer.validate(request.available_ingredients)
        if not valid:
            raise ValueError(error_msg)

        normalised_ingredients = ingredient_analysis["normalised"]
        logger.info(f"Analysed {len(normalised_ingredients)} ingredients: {normalised_ingredients[:5]}")

        # Step 2: Analyse preferences
        preferences = preference_analyzer.process(
            dietary_preference=request.dietary_preference,
            cuisine_preference=request.cuisine_preference,
            meal_type=request.meal_type,
            cooking_time_minutes=request.cooking_time_minutes,
            servings=request.servings,
            avoid_ingredients=request.avoid_ingredients,
        )
        logger.info(f"Preferences: {preferences}")

        # Step 3: RAG retrieval
        retrieved = recipe_rag.retrieve(
            available_ingredients=normalised_ingredients,
            dietary_preference=preferences.get("dietary_preference"),
            cuisine_preference=preferences.get("cuisine_preference"),
            meal_type=preferences.get("meal_type"),
            cooking_time_minutes=preferences.get("cooking_time_minutes"),
            top_k=6,
        )
        logger.info(f"RAG retrieved {len(retrieved)} candidates")

        # Filter out avoided ingredients from retrieved results
        avoid = preferences.get("avoid_ingredients", [])
        if avoid:
            filtered = []
            for r in retrieved:
                recipe_ings = [i["name"].lower() for i in r.get("ingredients", [])]
                skip = any(
                    any(av in ri or ri in av for ri in recipe_ings)
                    for av in avoid
                )
                if not skip:
                    filtered.append(r)
            retrieved = filtered or retrieved  # fall back if everything filtered

        # Step 4: Generate personalised recipes
        generated = await recipe_generator.generate(
            available_ingredients=normalised_ingredients,
            preferences=preferences,
            retrieved_recipes=retrieved,
        )

        # Build query summary
        summary_parts = [f"Recipes using: {', '.join(normalised_ingredients[:5])}"]
        if preferences.get("dietary_preference"):
            summary_parts.append(f"({preferences['dietary_preference']})")
        if preferences.get("cuisine_preference"):
            summary_parts.append(f"• {preferences['cuisine_preference']} cuisine")
        if preferences.get("meal_type"):
            summary_parts.append(f"• {preferences['meal_type']}")
        query_summary = " ".join(summary_parts)

        recipe_list = [_dict_to_recipe_list_item(r) for r in generated]

        return RecipeResponse(
            recipes=recipe_list,
            total=len(recipe_list),
            query_summary=query_summary,
            retrieved_context_count=len(retrieved),
        )

    async def get_recipe_detail(
        self, recipe_id: str, available_ingredients: List[str] = None
    ) -> RecipeDetailResponse:
        """
        Retrieve full recipe detail by ID.
        Marks ingredient availability based on user's available ingredients.
        """
        recipe_data = recipe_rag.get_recipe_by_id(recipe_id)
        if not recipe_data:
            raise ValueError(f"Recipe '{recipe_id}' not found.")

        recipe_data = dict(recipe_data)
        available = available_ingredients or []
        available_lower = {a.lower().strip() for a in available}

        # Mark availability
        for ing in recipe_data.get("ingredients", []):
            ing_name = ing["name"].lower()
            ing["available"] = any(
                ing_name in avail or avail in ing_name
                for avail in available_lower
            )

        # Build waste reduction if not present
        if not recipe_data.get("waste_reduction") and available:
            used = [
                ing["name"] for ing in recipe_data.get("ingredients", [])
                if ing.get("available", False)
            ]
            leftover = [
                a for a in available
                if not any(
                    a.lower() in ing["name"].lower() or ing["name"].lower() in a.lower()
                    for ing in recipe_data.get("ingredients", [])
                )
            ]
            recipe_data["waste_reduction"] = {
                "ingredients_used": used,
                "ingredients_leftover": leftover[:5],
                "leftover_suggestions": (
                    f"Leftover {', '.join(leftover[:3])} can be used in salads, soups, or as sides."
                    if leftover else "Great — you're using most of your available ingredients!"
                ),
            }

        # Get similar recipes via RAG
        similar_retrieved = recipe_rag.retrieve(
            available_ingredients=[ing["name"] for ing in recipe_data.get("ingredients", [])[:5]],
            top_k=4,
        )
        similar = [
            _dict_to_recipe_list_item(r)
            for r in similar_retrieved
            if r.get("id") != recipe_id
        ][:3]

        return RecipeDetailResponse(
            recipe=_dict_to_recipe(recipe_data),
            similar_recipes=similar,
        )


# Module-level singleton
recipe_planner = RecipePlanner()
