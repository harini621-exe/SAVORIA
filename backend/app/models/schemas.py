"""
SAVORIA Pydantic Models
Defines all request/response data models for the API.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ─── Request Models ──────────────────────────────────────────────────────────

class RecipeRequest(BaseModel):
    available_ingredients: List[str] = Field(
        ..., min_length=1, description="Ingredients the user has available"
    )
    avoid_ingredients: Optional[List[str]] = Field(
        default=[], description="Ingredients to avoid"
    )
    dietary_preference: Optional[str] = Field(
        default=None, description="e.g. vegetarian, vegan, gluten-free"
    )
    cuisine_preference: Optional[str] = Field(
        default=None, description="e.g. Italian, Indian, Mexican"
    )
    meal_type: Optional[str] = Field(
        default=None, description="e.g. breakfast, lunch, dinner, snack"
    )
    cooking_time_minutes: Optional[int] = Field(
        default=None, description="Maximum available cooking time in minutes"
    )
    servings: Optional[int] = Field(
        default=2, description="Number of servings desired"
    )


class SubstitutionRequest(BaseModel):
    ingredient: str = Field(..., description="Ingredient to find substitutes for")
    recipe_context: Optional[str] = Field(
        default=None, description="Recipe context for better substitution advice"
    )
    available_ingredients: Optional[List[str]] = Field(
        default=[], description="What the user has available"
    )


# ─── Response Models ──────────────────────────────────────────────────────────

class IngredientItem(BaseModel):
    name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    available: bool = True  # whether the user has this ingredient


class SubstitutionItem(BaseModel):
    original: str
    substitute: str
    quantity_guidance: Optional[str] = None
    effect_on_recipe: Optional[str] = None


class CookingStep(BaseModel):
    step_number: int
    instruction: str
    required_ingredients: Optional[List[str]] = None
    tip: Optional[str] = None


class NutritionInfo(BaseModel):
    calories_per_serving: Optional[str] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None


class WasteReduction(BaseModel):
    ingredients_used: List[str] = []
    ingredients_leftover: List[str] = []
    leftover_suggestions: Optional[str] = None


class Recipe(BaseModel):
    id: str
    name: str
    description: str
    cuisine: str
    meal_type: str
    difficulty: str  # Easy / Medium / Hard
    cooking_time_minutes: int
    prep_time_minutes: int
    servings: int
    dietary_info: List[str] = []
    ingredients: List[IngredientItem] = []
    steps: List[CookingStep] = []
    substitutions: List[SubstitutionItem] = []
    cooking_tips: List[str] = []
    waste_reduction: Optional[WasteReduction] = None
    nutrition: Optional[NutritionInfo] = None
    match_score: Optional[float] = None  # 0-1 how well it matches available ingredients
    tags: List[str] = []


class RecipeListItem(BaseModel):
    """Lightweight version for the suggestions list."""
    id: str
    name: str
    description: str
    cuisine: str
    meal_type: str
    difficulty: str
    cooking_time_minutes: int
    prep_time_minutes: int
    servings: int
    dietary_info: List[str] = []
    match_score: Optional[float] = None
    ingredients_available: int = 0
    ingredients_total: int = 0
    tags: List[str] = []


class RecipeResponse(BaseModel):
    recipes: List[RecipeListItem]
    total: int
    query_summary: str
    retrieved_context_count: int


class RecipeDetailResponse(BaseModel):
    recipe: Recipe
    similar_recipes: List[RecipeListItem] = []


class SubstitutionResponse(BaseModel):
    ingredient: str
    substitutions: List[SubstitutionItem]
    advice: str


class HealthResponse(BaseModel):
    status: str
    version: str
    watsonx_configured: bool
    rag_index_loaded: bool


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
