"""
SAVORIA RAG Pipeline
Builds and queries a FAISS vector index over the recipe knowledge base.
Retrieval is kept separate from generation to clearly demonstrate the RAG architecture.
"""

import json
import logging
import os
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)

# Lazy imports for optional heavy dependencies
_faiss = None
_SentenceTransformer = None


def _load_faiss():
    global _faiss
    if _faiss is None:
        import faiss
        _faiss = faiss
    return _faiss


def _load_sentence_transformer():
    global _SentenceTransformer
    if _SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer
        _SentenceTransformer = SentenceTransformer
    return _SentenceTransformer


class RecipeRAG:
    """
    Lightweight RAG pipeline:
    1. Builds a FAISS index over recipe text embeddings.
    2. Given user ingredients + preferences, retrieves the most relevant recipes.
    3. Returns structured context ready for the generation stage.
    """

    INDEX_FILE = "recipe_index.faiss"
    META_FILE = "recipe_meta.pkl"

    def __init__(self, data_dir: str = "data", embedding_model: str = "all-MiniLM-L6-v2"):
        self.data_dir = Path(data_dir)
        self.embedding_model_name = embedding_model
        self.recipes: List[Dict[str, Any]] = []
        self.index = None
        self.embedder = None
        self._loaded = False

    def _get_embedder(self):
        if self.embedder is None:
            ST = _load_sentence_transformer()
            self.embedder = ST(self.embedding_model_name)
        return self.embedder

    def _recipe_to_text(self, recipe: Dict[str, Any]) -> str:
        """
        Convert a recipe into a rich text document for embedding.
        Includes name, cuisine, ingredients, dietary info, and description.
        """
        ingredients = " ".join(
            ing["name"] for ing in recipe.get("ingredients", [])
        )
        dietary = " ".join(recipe.get("dietary_info", []))
        tags = " ".join(recipe.get("tags", []))
        steps_text = " ".join(
            s["instruction"] for s in recipe.get("steps", [])[:3]  # first 3 steps
        )
        return (
            f"{recipe['name']} {recipe['description']} "
            f"cuisine:{recipe['cuisine']} meal_type:{recipe['meal_type']} "
            f"ingredients:{ingredients} dietary:{dietary} tags:{tags} "
            f"difficulty:{recipe['difficulty']} {steps_text}"
        )

    def build_index(self) -> None:
        """Load recipes from JSON and build/save FAISS index."""
        recipe_path = self.data_dir / "recipes.json"
        if not recipe_path.exists():
            raise FileNotFoundError(f"Recipe data not found at {recipe_path}")

        with open(recipe_path, "r", encoding="utf-8") as f:
            self.recipes = json.load(f)

        logger.info(f"Building FAISS index for {len(self.recipes)} recipes...")
        texts = [self._recipe_to_text(r) for r in self.recipes]
        embedder = self._get_embedder()
        embeddings = embedder.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        embeddings = np.array(embeddings, dtype=np.float32)

        faiss = _load_faiss()
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product = cosine similarity (with normalised vectors)
        self.index.add(embeddings)

        # Persist index and metadata
        index_path = self.data_dir / self.INDEX_FILE
        meta_path = self.data_dir / self.META_FILE
        faiss.write_index(self.index, str(index_path))
        with open(meta_path, "wb") as f:
            pickle.dump(self.recipes, f)

        logger.info(f"FAISS index saved to {index_path}")
        self._loaded = True

    def load_index(self) -> bool:
        """Load a pre-built FAISS index from disk. Returns True if successful."""
        index_path = self.data_dir / self.INDEX_FILE
        meta_path = self.data_dir / self.META_FILE

        if not index_path.exists() or not meta_path.exists():
            return False

        faiss = _load_faiss()
        self.index = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as f:
            self.recipes = pickle.load(f)

        self._loaded = True
        logger.info(f"FAISS index loaded: {len(self.recipes)} recipes")
        return True

    def ensure_loaded(self) -> None:
        """Ensure index is available, building it if necessary."""
        if not self._loaded:
            if not self.load_index():
                self.build_index()

    def retrieve(
        self,
        available_ingredients: List[str],
        dietary_preference: str = None,
        cuisine_preference: str = None,
        meal_type: str = None,
        cooking_time_minutes: int = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant recipes for the given user context.
        
        Strategy:
        1. Build a rich query string from ingredients + preferences.
        2. Embed the query and search FAISS index.
        3. Apply hard filters (dietary, cooking time) post-retrieval.
        4. Return top_k results with match metadata.
        """
        self.ensure_loaded()

        # Build rich query
        query_parts = ["recipe with ingredients: " + ", ".join(available_ingredients)]
        if dietary_preference:
            query_parts.append(f"dietary:{dietary_preference}")
        if cuisine_preference:
            query_parts.append(f"cuisine:{cuisine_preference}")
        if meal_type:
            query_parts.append(f"meal type:{meal_type}")

        query = " ".join(query_parts)

        embedder = self._get_embedder()
        query_emb = embedder.encode([query], normalize_embeddings=True)
        query_emb = np.array(query_emb, dtype=np.float32)

        # Retrieve more candidates before filtering
        k_candidates = min(len(self.recipes), top_k * 3)
        scores, indices = self.index.search(query_emb, k_candidates)

        available_lower = {ing.lower().strip() for ing in available_ingredients}
        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            recipe = dict(self.recipes[idx])

            # Hard filter: cooking time
            if cooking_time_minutes is not None:
                total_time = recipe.get("cooking_time_minutes", 999) + recipe.get("prep_time_minutes", 0)
                if total_time > cooking_time_minutes:
                    continue

            # Hard filter: dietary preference
            if dietary_preference:
                dietary_info = [d.lower() for d in recipe.get("dietary_info", [])]
                pref_lower = dietary_preference.lower()
                # Map common aliases
                alias_map = {
                    "veg": "vegetarian", "veggie": "vegetarian",
                    "plant-based": "vegan", "no-gluten": "gluten-free",
                    "no-dairy": "dairy-free", "lactose-free": "dairy-free",
                }
                mapped = alias_map.get(pref_lower, pref_lower)
                if mapped not in dietary_info:
                    # Soft filter — do not hard exclude, just deprioritise
                    score *= 0.5

            # Calculate ingredient match score
            recipe_ingredients = {
                ing["name"].lower() for ing in recipe.get("ingredients", [])
            }
            matched = available_lower.intersection(recipe_ingredients)
            # Fuzzy partial match
            partial_matched = set()
            for avail in available_lower:
                for rec_ing in recipe_ingredients:
                    if avail in rec_ing or rec_ing in avail:
                        partial_matched.add(rec_ing)
            all_matched = matched | partial_matched
            match_ratio = len(all_matched) / max(len(recipe_ingredients), 1)

            recipe["_semantic_score"] = float(score)
            recipe["_match_ratio"] = match_ratio
            recipe["_matched_ingredients"] = list(all_matched)
            recipe["_combined_score"] = float(score) * 0.5 + match_ratio * 0.5

            results.append(recipe)

        # Sort by combined score
        results.sort(key=lambda r: r["_combined_score"], reverse=True)
        return results[:top_k]

    def get_recipe_by_id(self, recipe_id: str) -> Dict[str, Any] | None:
        """Retrieve a single recipe by ID."""
        self.ensure_loaded()
        for recipe in self.recipes:
            if recipe["id"] == recipe_id:
                return recipe
        return None

    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """Return all recipes in the knowledge base."""
        self.ensure_loaded()
        return self.recipes


# Module-level singleton
recipe_rag = RecipeRAG(data_dir="data")
