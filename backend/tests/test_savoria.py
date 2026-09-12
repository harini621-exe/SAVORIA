"""
SAVORIA Backend Tests
Tests for ingredient processing, RAG retrieval, recipe generation workflow,
substitution logic, dietary adaptation, and API endpoints.
"""

import json
import sys
import os
import pytest
import asyncio

# Ensure backend root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── Ingredient Analyzer Tests ───────────────────────────────────────────────

class TestIngredientAnalyzer:
    def setup_method(self):
        from app.agents.ingredient_analyzer import IngredientAnalyzer
        self.analyzer = IngredientAnalyzer()

    def test_normalise_basic(self):
        assert self.analyzer.normalise("  Garlic  ") == "garlic"

    def test_normalise_strips_quantities(self):
        result = self.analyzer.normalise("2 cups flour")
        assert "flour" in result

    def test_normalise_removes_parentheses(self):
        result = self.analyzer.normalise("tomato (fresh)")
        assert "tomato" in result
        assert "(" not in result

    def test_process_deduplicates(self):
        result = self.analyzer.process(["garlic", "garlic", "Garlic"])
        assert result["unique_count"] == 1

    def test_process_categorises_protein(self):
        result = self.analyzer.process(["chicken", "eggs", "tofu"])
        assert "protein" in result["categories"]
        assert len(result["categories"]["protein"]) > 0

    def test_process_identifies_staples(self):
        result = self.analyzer.process(["salt", "olive oil", "chicken"])
        assert result["is_staple"]["salt"] is True
        assert result["is_staple"]["olive oil"] is True

    def test_validate_empty_list(self):
        valid, msg = self.analyzer.validate([])
        assert not valid
        assert "ingredient" in msg.lower()

    def test_validate_valid_list(self):
        valid, msg = self.analyzer.validate(["garlic", "onion", "tomato"])
        assert valid
        assert msg == ""

    def test_validate_whitespace_only(self):
        valid, msg = self.analyzer.validate(["  ", ""])
        assert not valid

    def test_process_empty_strings_excluded(self):
        result = self.analyzer.process(["garlic", "", "  "])
        assert "" not in result["normalised"]
        assert "garlic" in result["normalised"]


# ─── Preference Analyzer Tests ────────────────────────────────────────────────

class TestPreferenceAnalyzer:
    def setup_method(self):
        from app.agents.preference_analyzer import PreferenceAnalyzer
        self.analyzer = PreferenceAnalyzer()

    def test_normalise_dietary_aliases(self):
        prefs = self.analyzer.process("veg", None, None, None, None, None)
        assert prefs["dietary_preference"] == "vegetarian"

    def test_normalise_vegan(self):
        prefs = self.analyzer.process("plant-based", None, None, None, None, None)
        assert prefs["dietary_preference"] == "vegan"

    def test_none_dietary_returns_none(self):
        prefs = self.analyzer.process(None, None, None, None, None, None)
        assert prefs["dietary_preference"] is None

    def test_servings_clamp(self):
        prefs = self.analyzer.process(None, None, None, None, 50, None)
        assert prefs["servings"] == 20

    def test_servings_default(self):
        prefs = self.analyzer.process(None, None, None, None, None, None)
        assert prefs["servings"] == 2

    def test_time_clamp(self):
        prefs = self.analyzer.process(None, None, None, 1000, None, None)
        assert prefs["cooking_time_minutes"] == 480

    def test_cuisine_title_case(self):
        prefs = self.analyzer.process(None, "italian", None, None, None, None)
        assert prefs["cuisine_preference"] == "Italian"

    def test_avoid_ingredients_normalised(self):
        prefs = self.analyzer.process(None, None, None, None, None, ["Peanuts", " SHELLFISH "])
        assert "peanuts" in prefs["avoid_ingredients"]
        assert "shellfish" in prefs["avoid_ingredients"]


# ─── Substitution Advisor Tests ───────────────────────────────────────────────

class TestSubstitutionAdvisor:
    def setup_method(self):
        from app.agents.substitution_advisor import SubstitutionAdvisor
        self.advisor = SubstitutionAdvisor()

    def test_butter_substitutions_exist(self):
        subs = self.advisor.get_substitutions("butter")
        assert len(subs) > 0
        assert all("substitute" in s for s in subs)

    def test_eggs_vegan_substitution(self):
        subs = self.advisor.get_substitutions("eggs", dietary_preference="vegan")
        assert len(subs) > 0

    def test_unknown_ingredient_returns_empty(self):
        subs = self.advisor.get_substitutions("obscure_ingredient_xyz123")
        assert isinstance(subs, list)

    def test_partial_match(self):
        subs = self.advisor.get_substitutions("heavy cream")
        assert len(subs) > 0

    def test_available_ingredients_prioritised(self):
        # coconut cream should appear higher when user has coconut cream
        subs = self.advisor.get_substitutions("butter", available_ingredients=["coconut oil"])
        assert len(subs) > 0
        assert subs[0]["substitute"].lower().startswith("coconut")

    def test_max_three_returned(self):
        subs = self.advisor.get_substitutions("butter")
        assert len(subs) <= 3


# ─── Dietary Adapter Tests ────────────────────────────────────────────────────

class TestDietaryAdapter:
    def setup_method(self):
        from app.agents.dietary_adapter import DietaryAdapter
        self.adapter = DietaryAdapter()

    def test_vegan_adaptation_exists(self):
        adaptation = self.adapter.get_adaptation("vegan")
        assert adaptation is not None
        assert "eggs" in adaptation["avoid_ingredients"]

    def test_gluten_free_adaptation(self):
        adaptation = self.adapter.get_adaptation("gluten-free")
        assert "flour" in adaptation["avoid_ingredients"]

    def test_unknown_preference_returns_none(self):
        adaptation = self.adapter.get_adaptation("alien-diet")
        assert adaptation is None

    def test_prompt_includes_instructions(self):
        prompt = self.adapter.build_adaptation_prompt("vegan")
        assert "vegan" in prompt.lower() or "VEGAN" in prompt

    def test_recipe_compatibility_chicken_vegetarian(self):
        recipe = {
            "ingredients": [
                {"name": "chicken breast"},
                {"name": "garlic"},
                {"name": "onion"},
            ]
        }
        result = self.adapter.check_recipe_compatibility(recipe, "vegetarian")
        assert result["compatible"] is False
        assert any("chicken" in issue for issue in result["issues"])

    def test_recipe_compatibility_all_veg(self):
        recipe = {
            "ingredients": [
                {"name": "garlic"},
                {"name": "onion"},
                {"name": "tomato"},
            ]
        }
        result = self.adapter.check_recipe_compatibility(recipe, "vegetarian")
        assert result["compatible"] is True

    def test_none_preference_returns_compatible(self):
        result = self.adapter.check_recipe_compatibility({}, None)
        assert result["compatible"] is True


# ─── RAG Retriever Tests ──────────────────────────────────────────────────────

class TestRecipeRAG:
    def setup_method(self):
        from app.rag.retriever import RecipeRAG
        self.rag = RecipeRAG(data_dir="data")

    def test_index_loads_or_builds(self):
        self.rag.ensure_loaded()
        assert self.rag._loaded
        assert len(self.rag.recipes) > 0

    def test_retrieve_returns_results(self):
        self.rag.ensure_loaded()
        results = self.rag.retrieve(
            available_ingredients=["garlic", "pasta", "olive oil"],
            top_k=3,
        )
        assert len(results) > 0
        assert len(results) <= 3

    def test_retrieve_with_dietary_filter(self):
        self.rag.ensure_loaded()
        results = self.rag.retrieve(
            available_ingredients=["lentils", "onion", "tomato"],
            dietary_preference="vegan",
            top_k=3,
        )
        assert len(results) > 0

    def test_retrieve_with_time_filter(self):
        self.rag.ensure_loaded()
        results = self.rag.retrieve(
            available_ingredients=["eggs", "onion"],
            cooking_time_minutes=15,
            top_k=5,
        )
        for r in results:
            total = r.get("cooking_time_minutes", 0) + r.get("prep_time_minutes", 0)
            assert total <= 15

    def test_get_recipe_by_id(self):
        self.rag.ensure_loaded()
        recipe = self.rag.get_recipe_by_id("r001")
        assert recipe is not None
        assert recipe["id"] == "r001"

    def test_get_recipe_nonexistent(self):
        self.rag.ensure_loaded()
        recipe = self.rag.get_recipe_by_id("nonexistent_id")
        assert recipe is None

    def test_retrieve_returns_match_score(self):
        self.rag.ensure_loaded()
        results = self.rag.retrieve(
            available_ingredients=["garlic", "tomato", "onion"],
            top_k=3,
        )
        for r in results:
            assert "_match_ratio" in r
            assert 0.0 <= r["_match_ratio"] <= 1.0

    def test_get_all_recipes(self):
        self.rag.ensure_loaded()
        all_recipes = self.rag.get_all_recipes()
        assert len(all_recipes) >= 10


# ─── Recipe Planner Integration Tests ────────────────────────────────────────

class TestRecipePlannerIntegration:
    """Integration tests for the full pipeline (no AI calls)."""

    @pytest.mark.asyncio
    async def test_plan_recipes_basic(self):
        from app.agents.recipe_planner import RecipePlanner
        from app.models.schemas import RecipeRequest
        planner = RecipePlanner()
        request = RecipeRequest(
            available_ingredients=["garlic", "pasta", "olive oil", "tomato"],
        )
        result = await planner.plan_recipes(request)
        assert result.total > 0
        assert len(result.recipes) > 0
        assert result.retrieved_context_count > 0

    @pytest.mark.asyncio
    async def test_plan_recipes_with_preferences(self):
        from app.agents.recipe_planner import RecipePlanner
        from app.models.schemas import RecipeRequest
        planner = RecipePlanner()
        request = RecipeRequest(
            available_ingredients=["lentils", "onion", "garlic", "tomato", "cumin"],
            dietary_preference="vegan",
            meal_type="dinner",
            servings=3,
        )
        result = await planner.plan_recipes(request)
        assert result.total > 0

    @pytest.mark.asyncio
    async def test_plan_recipes_invalid_input(self):
        from app.agents.recipe_planner import RecipePlanner
        from app.models.schemas import RecipeRequest
        planner = RecipePlanner()
        request = RecipeRequest(available_ingredients=["  ", ""])
        with pytest.raises(ValueError):
            await planner.plan_recipes(request)

    @pytest.mark.asyncio
    async def test_get_recipe_detail(self):
        from app.agents.recipe_planner import RecipePlanner
        planner = RecipePlanner()
        result = await planner.get_recipe_detail(
            "r001", ["garlic", "spaghetti", "olive oil"]
        )
        assert result.recipe.id == "r001"
        assert len(result.recipe.steps) > 0
        # Check availability marking works
        available_ings = [i for i in result.recipe.ingredients if i.available]
        assert len(available_ings) > 0

    @pytest.mark.asyncio
    async def test_get_recipe_not_found(self):
        from app.agents.recipe_planner import RecipePlanner
        planner = RecipePlanner()
        with pytest.raises(ValueError):
            await planner.get_recipe_detail("nonexistent_recipe_xyz")


# ─── API Endpoint Tests ───────────────────────────────────────────────────────

class TestAPIEndpoints:
    """FastAPI endpoint integration tests using TestClient."""

    def setup_method(self):
        from fastapi.testclient import TestClient
        from app.main import app
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "watsonx_configured" in data

    def test_root_endpoint(self):
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "SAVORIA" in data["name"]

    def test_generate_recipes_endpoint(self):
        response = self.client.post(
            "/api/recipes/generate",
            json={
                "available_ingredients": ["garlic", "pasta", "olive oil", "tomato"],
                "servings": 2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) > 0

    def test_generate_recipes_empty_ingredients(self):
        response = self.client.post(
            "/api/recipes/generate",
            json={"available_ingredients": []},
        )
        assert response.status_code in (400, 422)

    def test_get_recipe_detail_endpoint(self):
        response = self.client.get("/api/recipes/r001")
        assert response.status_code == 200
        data = response.json()
        assert data["recipe"]["id"] == "r001"

    def test_get_recipe_not_found(self):
        response = self.client.get("/api/recipes/nonexistent_xyz_999")
        assert response.status_code == 404

    def test_list_recipes_endpoint(self):
        response = self.client.get("/api/recipes")
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) > 0

    def test_list_recipes_filtered(self):
        response = self.client.get("/api/recipes?meal_type=breakfast")
        assert response.status_code == 200
        data = response.json()
        for r in data["recipes"]:
            assert r["meal_type"] == "breakfast"

    def test_substitution_endpoint(self):
        response = self.client.post(
            "/api/substitutions",
            json={"ingredient": "butter"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ingredient"] == "butter"
        assert len(data["substitutions"]) > 0

    def test_analyse_ingredients_endpoint(self):
        response = self.client.post(
            "/api/ingredients/analyse",
            json=["garlic", "onion", "tomato", "2 cups flour"],
        )
        assert response.status_code == 200
        data = response.json()
        assert "normalised" in data
        assert "categories" in data


# ─── Watsonx Client Configuration Tests ──────────────────────────────────────

class TestWatsonxClient:
    def setup_method(self):
        from app.utils.watsonx_client import WatsonxClient
        self.client = WatsonxClient()

    def test_is_configured_with_credentials(self):
        """When IBM_API_KEY and IBM_PROJECT_ID are set, client should be configured."""
        import os
        if os.getenv("IBM_API_KEY") and os.getenv("IBM_PROJECT_ID"):
            assert self.client.is_configured() is True

    def test_not_configured_without_credentials(self):
        """Client should not be configured when credentials are missing."""
        from app.utils.watsonx_client import WatsonxClient
        from unittest.mock import MagicMock
        client = WatsonxClient()
        # Temporarily override the settings on the client to simulate no credentials
        mock_settings = MagicMock()
        mock_settings.IBM_API_KEY = ""
        mock_settings.IBM_PROJECT_ID = ""
        original_settings = client.settings
        client.settings = mock_settings
        assert not client.is_configured()
        client.settings = original_settings

    @pytest.mark.asyncio
    async def test_generate_raises_when_not_configured(self):
        """generate() should raise RuntimeError when credentials are absent."""
        from app.utils.watsonx_client import WatsonxClient
        from unittest.mock import patch, MagicMock
        client = WatsonxClient()
        # Override is_configured to return False
        with patch.object(client, "is_configured", return_value=False):
            with pytest.raises(RuntimeError, match="not configured"):
                await client.generate("sys", "user")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
