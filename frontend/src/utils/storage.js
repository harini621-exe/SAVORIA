/**
 * SAVORIA Local Storage Utilities
 * Manages saved recipes, recent recipes, and user preferences.
 */

const KEYS = {
  SAVED_RECIPES: 'savoria_saved_recipes',
  RECENT_RECIPES: 'savoria_recent_recipes',
  USER_PREFERENCES: 'savoria_user_preferences',
  COOKING_PROGRESS: 'savoria_cooking_progress',
};

const MAX_RECENT = 10;

// ─── Saved Recipes ────────────────────────────────────────────────────────────

export const getSavedRecipes = () => {
  try {
    return JSON.parse(localStorage.getItem(KEYS.SAVED_RECIPES) || '[]');
  } catch {
    return [];
  }
};

export const saveRecipe = (recipe) => {
  const saved = getSavedRecipes();
  const exists = saved.find((r) => r.id === recipe.id);
  if (!exists) {
    const updated = [{ ...recipe, savedAt: new Date().toISOString() }, ...saved];
    localStorage.setItem(KEYS.SAVED_RECIPES, JSON.stringify(updated));
  }
};

export const unsaveRecipe = (recipeId) => {
  const saved = getSavedRecipes().filter((r) => r.id !== recipeId);
  localStorage.setItem(KEYS.SAVED_RECIPES, JSON.stringify(saved));
};

export const isRecipeSaved = (recipeId) =>
  getSavedRecipes().some((r) => r.id === recipeId);

// ─── Recent Recipes ───────────────────────────────────────────────────────────

export const getRecentRecipes = () => {
  try {
    return JSON.parse(localStorage.getItem(KEYS.RECENT_RECIPES) || '[]');
  } catch {
    return [];
  }
};

export const addRecentRecipe = (recipe) => {
  const recent = getRecentRecipes().filter((r) => r.id !== recipe.id);
  const updated = [{ ...recipe, viewedAt: new Date().toISOString() }, ...recent].slice(0, MAX_RECENT);
  localStorage.setItem(KEYS.RECENT_RECIPES, JSON.stringify(updated));
};

// ─── User Preferences ─────────────────────────────────────────────────────────

export const getUserPreferences = () => {
  try {
    return JSON.parse(localStorage.getItem(KEYS.USER_PREFERENCES) || '{}');
  } catch {
    return {};
  }
};

export const saveUserPreferences = (preferences) => {
  localStorage.setItem(KEYS.USER_PREFERENCES, JSON.stringify(preferences));
};

// ─── Cooking Progress ─────────────────────────────────────────────────────────

export const getCookingProgress = (recipeId) => {
  try {
    const all = JSON.parse(localStorage.getItem(KEYS.COOKING_PROGRESS) || '{}');
    return all[recipeId] || { currentStep: 0, completed: false };
  } catch {
    return { currentStep: 0, completed: false };
  }
};

export const saveCookingProgress = (recipeId, progress) => {
  try {
    const all = JSON.parse(localStorage.getItem(KEYS.COOKING_PROGRESS) || '{}');
    all[recipeId] = { ...progress, updatedAt: new Date().toISOString() };
    localStorage.setItem(KEYS.COOKING_PROGRESS, JSON.stringify(all));
  } catch {
    // Silently fail — non-critical
  }
};

export const clearCookingProgress = (recipeId) => {
  try {
    const all = JSON.parse(localStorage.getItem(KEYS.COOKING_PROGRESS) || '{}');
    delete all[recipeId];
    localStorage.setItem(KEYS.COOKING_PROGRESS, JSON.stringify(all));
  } catch {}
};
