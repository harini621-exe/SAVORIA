"""
SAVORIA API Routes
Defines all FastAPI endpoints.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.agents.recipe_planner import recipe_planner
from app.agents.substitution_advisor import SubstitutionAdvisor
from app.agents.ingredient_analyzer import IngredientAnalyzer
from app.rag.retriever import recipe_rag
from app.models.schemas import (
    RecipeRequest, RecipeResponse, RecipeDetailResponse,
    SubstitutionRequest, SubstitutionResponse, SubstitutionItem,
    HealthResponse, ErrorResponse,
)
from app.config import get_settings
from app.utils.watsonx_client import watsonx_client

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

substitution_advisor = SubstitutionAdvisor()
ingredient_analyzer = IngredientAnalyzer()


# ─── Health ──────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """System health check endpoint."""
    rag_loaded = recipe_rag._loaded
    if not rag_loaded:
        try:
            recipe_rag.ensure_loaded()
            rag_loaded = recipe_rag._loaded
        except Exception:
            rag_loaded = False

    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        watsonx_configured=watsonx_client.is_configured(),
        rag_index_loaded=rag_loaded,
    )


# ─── Recipe Generation ────────────────────────────────────────────────────────

@router.post("/recipes/generate", response_model=RecipeResponse, tags=["Recipes"])
async def generate_recipes(request: RecipeRequest):
    """
    Main SAVORIA endpoint.
    
    Workflow:
    1. Analyse ingredients and preferences
    2. Retrieve relevant recipes via FAISS RAG
    3. Generate personalised suggestions via IBM watsonx.ai
    4. Return structured recipe list
    """
    try:
        valid, msg = ingredient_analyzer.validate(request.available_ingredients)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)

        result = await recipe_planner.plan_recipes(request)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Recipe generation error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in generate_recipes: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating recipes. Please try again.",
        )


# ─── Recipe Detail ────────────────────────────────────────────────────────────

@router.get("/recipes/{recipe_id}", response_model=RecipeDetailResponse, tags=["Recipes"])
async def get_recipe_detail(
    recipe_id: str,
    ingredients: Optional[str] = Query(
        default=None,
        description="Comma-separated available ingredients for availability marking"
    ),
):
    """
    Retrieve full recipe details by ID.
    Pass `ingredients` query param to mark which recipe ingredients the user has.
    """
    available = [i.strip() for i in ingredients.split(",")] if ingredients else []
    try:
        result = await recipe_planner.get_recipe_detail(recipe_id, available)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve recipe details.")


# ─── Recipe Listing ───────────────────────────────────────────────────────────

@router.get("/recipes", tags=["Recipes"])
async def list_recipes(
    cuisine: Optional[str] = Query(default=None),
    meal_type: Optional[str] = Query(default=None),
    dietary: Optional[str] = Query(default=None),
    difficulty: Optional[str] = Query(default=None),
    max_time: Optional[int] = Query(default=None),
    limit: int = Query(default=20, le=100),
):
    """Browse all recipes in the knowledge base with optional filters."""
    try:
        all_recipes = recipe_rag.get_all_recipes()

        if cuisine:
            all_recipes = [r for r in all_recipes if r.get("cuisine", "").lower() == cuisine.lower()]
        if meal_type:
            all_recipes = [r for r in all_recipes if r.get("meal_type", "").lower() == meal_type.lower()]
        if dietary:
            all_recipes = [r for r in all_recipes if dietary.lower() in [d.lower() for d in r.get("dietary_info", [])]]
        if difficulty:
            all_recipes = [r for r in all_recipes if r.get("difficulty", "").lower() == difficulty.lower()]
        if max_time is not None:
            all_recipes = [
                r for r in all_recipes
                if (r.get("cooking_time_minutes", 0) + r.get("prep_time_minutes", 0)) <= max_time
            ]

        return {
            "recipes": all_recipes[:limit],
            "total": len(all_recipes),
        }
    except Exception as e:
        logger.error(f"Error listing recipes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list recipes.")


# ─── Substitutions ────────────────────────────────────────────────────────────

@router.post("/substitutions", response_model=SubstitutionResponse, tags=["Substitutions"])
async def get_substitutions(request: SubstitutionRequest):
    """Get ingredient substitution suggestions."""
    subs = substitution_advisor.get_substitutions(
        ingredient=request.ingredient,
        available_ingredients=request.available_ingredients,
    )
    items = [
        SubstitutionItem(
            original=request.ingredient,
            substitute=s["substitute"],
            quantity_guidance=s.get("guidance"),
            effect_on_recipe=s.get("effect"),
        )
        for s in subs
    ]
    advice = (
        f"Found {len(items)} substitution(s) for '{request.ingredient}'."
        if items
        else f"No standard substitutions found for '{request.ingredient}'. Try omitting it or checking your pantry."
    )
    return SubstitutionResponse(
        ingredient=request.ingredient,
        substitutions=items,
        advice=advice,
    )


# ─── Ingredient Analysis ──────────────────────────────────────────────────────

@router.post("/ingredients/analyse", tags=["Ingredients"])
async def analyse_ingredients(ingredients: List[str]):
    """Analyse and normalise a list of ingredients."""
    valid, msg = ingredient_analyzer.validate(ingredients)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    analysis = ingredient_analyzer.process(ingredients)
    return analysis
