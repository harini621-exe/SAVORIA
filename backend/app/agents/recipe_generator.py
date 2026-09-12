"""
Recipe Generator Agent
Constructs prompts and orchestrates IBM watsonx.ai calls to generate personalised recipes.
"""

import json
import logging
import re
import uuid
from typing import List, Dict, Any, Optional

from app.utils.watsonx_client import watsonx_client
from app.agents.substitution_advisor import SubstitutionAdvisor
from app.agents.dietary_adapter import DietaryAdapter

logger = logging.getLogger(__name__)

substitution_advisor = SubstitutionAdvisor()
dietary_adapter = DietaryAdapter()


SYSTEM_PROMPT = """You are SAVORIA, an expert culinary AI assistant and professional chef.
Your role is to generate detailed, practical, and delicious personalised recipes.

CRITICAL: You MUST respond with valid JSON ONLY. No markdown. No code fences. No ```json tags. No explanation before or after. Start your response directly with { and end with }. Any non-JSON output will break the application.

Every recipe you produce is practical, uses real cooking techniques, and provides accurate step-by-step instructions.
You maximise the use of ingredients the user already has available."""


def _build_generation_prompt(
    available_ingredients: List[str],
    preferences: Dict[str, Any],
    retrieved_context: List[Dict[str, Any]],
    substitution_context: str,
    dietary_instructions: str,
    servings: int,
) -> str:
    """Construct the user-facing generation prompt with full RAG context."""

    ingredients_str = ", ".join(available_ingredients)
    avoid_str = (
        ", ".join(preferences.get("avoid_ingredients", [])) or "none"
    )

    # Use only top-2 retrieved recipes as context (keeps prompt shorter)
    context_recipes = []
    for r in retrieved_context[:2]:
        ing_list = ", ".join(ing["name"] for ing in r.get("ingredients", [])[:6])
        context_recipes.append(
            f"- {r['name']} ({r['cuisine']}, {r['meal_type']}): ingredients: {ing_list}."
        )
    context_str = "\n".join(context_recipes) if context_recipes else "None."

    # Generate ONE detailed recipe — quality over quantity; we blend with RAG for the other two
    prompt = f"""Generate ONE personalised recipe using these available ingredients: {ingredients_str}

Avoid: {avoid_str}
{_format_preferences(preferences)}
{dietary_instructions if dietary_instructions else ""}
Reference context (adapt freely): {context_str}

Rules: maximise use of available ingredients; include 4-6 cooking steps; be practical and specific.

Return ONLY this JSON (no other text, no markdown):
{{"recipes":[{{"id":"gen_001","name":"...","description":"...","cuisine":"...","meal_type":"{preferences.get('meal_type','dinner')}","difficulty":"Easy","cooking_time_minutes":25,"prep_time_minutes":10,"servings":{servings},"dietary_info":[],"tags":[],"ingredients":[{{"name":"...","quantity":"...","unit":"...","available":true}}],"steps":[{{"step_number":1,"instruction":"...","required_ingredients":[],"tip":null}}],"substitutions":[{{"original":"...","substitute":"...","quantity_guidance":"...","effect_on_recipe":"..."}}],"cooking_tips":["..."],"nutrition":{{"calories_per_serving":"...","protein":"...","carbs":"...","fat":"..."}},"waste_reduction":{{"ingredients_used":["{available_ingredients[0] if available_ingredients else ''}"],"ingredients_leftover":[],"leftover_suggestions":"..."}}}}]}}"""
    return prompt


def _format_preferences(preferences: Dict[str, Any]) -> str:
    lines = []
    if preferences.get("dietary_preference"):
        lines.append(f"Dietary: {preferences['dietary_preference']}")
    if preferences.get("cuisine_preference"):
        lines.append(f"Cuisine: {preferences['cuisine_preference']}")
    if preferences.get("meal_type"):
        lines.append(f"Meal type: {preferences['meal_type']}")
    if preferences.get("cooking_time_minutes"):
        lines.append(f"Max cooking time: {preferences['cooking_time_minutes']} minutes")
    return "\n".join(lines) if lines else "No specific preferences"


def _extract_json(text: str) -> Optional[Dict]:
    """
    Robustly extract JSON from model output.
    Handles: pure JSON, markdown code fences, JSON embedded in prose.
    """
    text = text.strip()

    # 1. Strip markdown code fences: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 2. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Find the outermost JSON object by tracking brace depth
    start = text.find('{')
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    # Try to repair common issues: trailing commas
                    repaired = re.sub(r',\s*([}\]])', r'\1', candidate)
                    try:
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        pass
                break
    return None


def _sanitise_recipe(recipe: Dict[str, Any], available_ingredients: List[str]) -> Dict[str, Any]:
    """Ensure generated recipe has all required fields and correct availability flags."""
    available_lower = {a.lower().strip() for a in available_ingredients}

    # Ensure ID
    if not recipe.get("id"):
        recipe["id"] = f"gen_{uuid.uuid4().hex[:8]}"

    # Fix availability flags
    for ing in recipe.get("ingredients", []):
        ing_name = ing.get("name", "").lower()
        ing["available"] = any(
            ing_name in avail or avail in ing_name
            for avail in available_lower
        )

    # Ensure steps are numbered
    for i, step in enumerate(recipe.get("steps", []), 1):
        if "step_number" not in step:
            step["step_number"] = i

    # Ensure required fields exist
    recipe.setdefault("tags", [])
    recipe.setdefault("substitutions", [])
    recipe.setdefault("cooking_tips", [])
    recipe.setdefault("dietary_info", [])
    recipe.setdefault("waste_reduction", None)
    recipe.setdefault("nutrition", None)

    return recipe


def _build_fallback_recipe(
    recipe_data: Dict[str, Any],
    available_ingredients: List[str],
    servings: int,
    preferences: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a structured recipe from RAG-retrieved data when watsonx.ai is unavailable.
    This ensures the app is still usable for demo purposes without AI credits.
    """
    available_lower = {a.lower().strip() for a in available_ingredients}
    recipe = dict(recipe_data)
    recipe["id"] = f"rag_{recipe_data.get('id', uuid.uuid4().hex[:8])}"
    recipe["servings"] = servings

    # Mark ingredient availability
    for ing in recipe.get("ingredients", []):
        ing_name = ing.get("name", "").lower()
        ing["available"] = any(
            ing_name in avail or avail in ing_name
            for avail in available_lower
        )

    # Build waste reduction data
    used = [
        ing["name"] for ing in recipe.get("ingredients", [])
        if ing.get("available", False)
    ]
    leftover = [a for a in available_ingredients if not any(
        a.lower() in ing["name"].lower() or ing["name"].lower() in a.lower()
        for ing in recipe.get("ingredients", [])
    )]
    recipe["waste_reduction"] = {
        "ingredients_used": used,
        "ingredients_leftover": leftover[:5],
        "leftover_suggestions": (
            f"The remaining {', '.join(leftover[:3])} can be used in salads, soups, or stir-fries."
            if leftover else "You're using most of your available ingredients efficiently!"
        ),
    }

    recipe.setdefault("tags", [])
    recipe.setdefault("substitutions", [])
    recipe.setdefault("cooking_tips", [])
    return recipe


class RecipeGenerator:
    """
    Orchestrates the full RAG + generation workflow:
    1. Uses retrieved recipe context as grounding.
    2. Builds a structured prompt with ingredient and preference context.
    3. Calls IBM watsonx.ai to generate personalised recipes.
    4. Falls back to RAG-retrieved recipes if AI is unavailable.
    5. Sanitises and structures the output.
    """

    async def generate(
        self,
        available_ingredients: List[str],
        preferences: Dict[str, Any],
        retrieved_recipes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate personalised recipes using IBM watsonx.ai with RAG context.
        Falls back to retrieved recipes if AI generation fails.
        """
        servings = preferences.get("servings", 2)
        dietary_pref = preferences.get("dietary_preference")

        # Build substitution and dietary context
        sub_context = "No specific substitutions needed."
        if retrieved_recipes:
            sub_context = substitution_advisor.build_substitution_context(
                retrieved_recipes[0], available_ingredients
            )
        dietary_instructions = dietary_adapter.build_adaptation_prompt(dietary_pref)

        # Try AI generation first
        if watsonx_client.is_configured():
            try:
                prompt = _build_generation_prompt(
                    available_ingredients=available_ingredients,
                    preferences=preferences,
                    retrieved_context=retrieved_recipes,
                    substitution_context=sub_context,
                    dietary_instructions=dietary_instructions,
                    servings=servings,
                )
                raw = await watsonx_client.generate(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=prompt,
                    max_tokens=3000,
                )
                parsed = _extract_json(raw)
                if parsed and "recipes" in parsed:
                    ai_recipes = [
                        _sanitise_recipe(r, available_ingredients)
                        for r in parsed["recipes"]
                    ]
                    logger.info(f"AI generation produced {len(ai_recipes)} recipe(s)")
                    # Blend: 1 AI recipe + up to 2 RAG fallbacks to give 3 total
                    rag_fill = [
                        _build_fallback_recipe(r, available_ingredients, servings, preferences)
                        for r in retrieved_recipes
                        if r.get("id") not in {x.get("id") for x in ai_recipes}
                    ][:2]
                    combined = (ai_recipes + rag_fill)[:3]
                    return combined
                else:
                    logger.warning(
                        f"AI response did not contain valid JSON; falling back to RAG. "
                        f"Raw response preview (first 500 chars): {raw[:500] if raw else 'empty'}"
                    )
            except Exception as exc:
                logger.error(f"watsonx.ai generation failed: {exc}; using RAG fallback")

        # Fallback: use retrieved recipes directly
        logger.info(f"Using RAG fallback with {len(retrieved_recipes)} retrieved recipes")
        fallback = [
            _build_fallback_recipe(r, available_ingredients, servings, preferences)
            for r in retrieved_recipes[:3]
        ]
        return fallback
