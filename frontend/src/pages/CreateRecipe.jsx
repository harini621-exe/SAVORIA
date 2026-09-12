import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateRecipes } from '../utils/api';
import { getUserPreferences, saveUserPreferences } from '../utils/storage';
import './CreateRecipe.css';

const DIETARY_OPTIONS = [
  { value: '', label: 'None / No restriction' },
  { value: 'vegetarian', label: 'Vegetarian' },
  { value: 'vegan', label: 'Vegan' },
  { value: 'gluten-free', label: 'Gluten-Free' },
  { value: 'dairy-free', label: 'Dairy-Free' },
  { value: 'high-protein', label: 'High-Protein' },
  { value: 'low-carb', label: 'Low-Carb' },
  { value: 'low-spice', label: 'Low-Spice' },
];

const CUISINE_OPTIONS = [
  { value: '', label: 'Any cuisine' },
  { value: 'Italian', label: 'Italian' },
  { value: 'Indian', label: 'Indian' },
  { value: 'Mexican', label: 'Mexican' },
  { value: 'Asian', label: 'Asian' },
  { value: 'Japanese', label: 'Japanese' },
  { value: 'Mediterranean', label: 'Mediterranean' },
  { value: 'Middle Eastern', label: 'Middle Eastern' },
  { value: 'French', label: 'French' },
  { value: 'Greek', label: 'Greek' },
  { value: 'Contemporary', label: 'Contemporary' },
];

const MEAL_OPTIONS = [
  { value: '', label: 'Any meal type' },
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'snack', label: 'Snack' },
];

const TIME_OPTIONS = [
  { value: '', label: 'Any time' },
  { value: 15, label: 'Under 15 minutes' },
  { value: 30, label: 'Under 30 minutes' },
  { value: 45, label: 'Under 45 minutes' },
  { value: 60, label: 'Under 1 hour' },
  { value: 90, label: 'Under 1.5 hours' },
];

function IngredientInput({ ingredients, onChange, placeholder, label, hint }) {
  const [inputValue, setInputValue] = useState('');

  const addIngredient = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !ingredients.includes(trimmed.toLowerCase())) {
      onChange([...ingredients, trimmed.toLowerCase()]);
      setInputValue('');
    }
  };

  const removeIngredient = (ing) => onChange(ingredients.filter((i) => i !== ing));

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addIngredient();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text');
    const items = pasted.split(/[,\n]+/).map((s) => s.trim().toLowerCase()).filter(Boolean);
    const unique = items.filter((i) => !ingredients.includes(i));
    if (unique.length) onChange([...ingredients, ...unique]);
  };

  return (
    <div className="ingredient-input-section">
      <label className="form-label">{label}</label>
      {hint && <p className="form-hint" style={{ marginBottom: 'var(--space-2)' }}>{hint}</p>}
      <div className="ingredient-input-row">
        <input
          type="text"
          className="form-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder={placeholder}
          aria-label={label}
        />
        <button
          type="button"
          className="btn btn-secondary"
          onClick={addIngredient}
          disabled={!inputValue.trim()}
        >
          Add
        </button>
      </div>
      {ingredients.length > 0 && (
        <div className="ingredient-chips" role="list" aria-label={`Added ${label.toLowerCase()}`}>
          {ingredients.map((ing) => (
            <span key={ing} className="ingredient-chip" role="listitem">
              {ing}
              <button
                className="remove-btn"
                onClick={() => removeIngredient(ing)}
                aria-label={`Remove ${ing}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CreateRecipe() {
  const navigate = useNavigate();
  const savedPrefs = getUserPreferences();

  const [availableIngredients, setAvailableIngredients] = useState(
    savedPrefs.availableIngredients || []
  );
  const [avoidIngredients, setAvoidIngredients] = useState(
    savedPrefs.avoidIngredients || []
  );
  const [dietary, setDietary] = useState(savedPrefs.dietary || '');
  const [cuisine, setCuisine] = useState(savedPrefs.cuisine || '');
  const [mealType, setMealType] = useState(savedPrefs.mealType || '');
  const [cookingTime, setCookingTime] = useState(savedPrefs.cookingTime || '');
  const [servings, setServings] = useState(savedPrefs.servings || 2);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Save preferences on change
  useEffect(() => {
    saveUserPreferences({
      availableIngredients, avoidIngredients,
      dietary, cuisine, mealType, cookingTime, servings,
    });
  }, [availableIngredients, avoidIngredients, dietary, cuisine, mealType, cookingTime, servings]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (availableIngredients.length === 0) {
      setError('Please add at least one available ingredient to get started.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestData = {
        available_ingredients: availableIngredients,
        avoid_ingredients: avoidIngredients,
        dietary_preference: dietary || null,
        cuisine_preference: cuisine || null,
        meal_type: mealType || null,
        cooking_time_minutes: cookingTime ? parseInt(cookingTime) : null,
        servings: servings || 2,
      };

      const result = await generateRecipes(requestData);

      // Navigate to results with data
      navigate('/suggestions', {
        state: {
          recipes: result.recipes,
          querySummary: result.query_summary,
          retrievedCount: result.retrieved_context_count,
          availableIngredients,
          requestData,
        },
      });
    } catch (err) {
      setError(err.message || 'Failed to generate recipes. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setAvailableIngredients([]);
    setAvoidIngredients([]);
    setDietary('');
    setCuisine('');
    setMealType('');
    setCookingTime('');
    setServings(2);
  };

  return (
    <div className="page-wrapper">
      <div className="container">
        <div className="create-recipe-page">
          {/* Header */}
          <div className="page-header">
            <h1>What's in your kitchen?</h1>
            <p>Enter your available ingredients and preferences. SAVORIA will retrieve relevant recipes and generate personalised meal suggestions for you.</p>
          </div>

          <form onSubmit={handleSubmit} className="create-form" noValidate>
            <div className="create-form-grid">
              {/* Main ingredient input */}
              <div className="create-form-main">
                <div className="form-section card">
                  <div className="card-body">
                    <h2 className="form-section-title">Available Ingredients</h2>
                    <p className="form-section-desc">
                      List everything you have in your fridge, freezer, and pantry.
                      Basic staples like salt, oil, and water are assumed.
                    </p>
                    <IngredientInput
                      ingredients={availableIngredients}
                      onChange={setAvailableIngredients}
                      label="Your ingredients"
                      placeholder="e.g. garlic, chicken breast, tomatoes…"
                      hint="Type an ingredient and press Enter or comma to add it. You can also paste a comma-separated list."
                    />
                    {availableIngredients.length === 0 && (
                      <div className="quick-examples">
                        <span className="quick-examples-label">Quick start:</span>
                        {[
                          ['garlic', 'pasta', 'olive oil', 'tomato'],
                          ['chicken', 'onion', 'ginger', 'tomato', 'spices'],
                          ['eggs', 'oats', 'banana', 'milk'],
                          ['lentils', 'onion', 'cumin', 'tomato'],
                        ].map((set, i) => (
                          <button
                            key={i}
                            type="button"
                            className="btn btn-ghost btn-sm"
                            onClick={() => setAvailableIngredients(set)}
                          >
                            {set.slice(0, 3).join(', ')}…
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <div className="form-section card">
                  <div className="card-body">
                    <h2 className="form-section-title">Ingredients to Avoid</h2>
                    <p className="form-section-desc">Optional — list any ingredients you cannot or do not want to use.</p>
                    <IngredientInput
                      ingredients={avoidIngredients}
                      onChange={setAvoidIngredients}
                      label="Avoid these ingredients"
                      placeholder="e.g. peanuts, shellfish…"
                      hint="Optional. Press Enter to add."
                    />
                  </div>
                </div>
              </div>

              {/* Preferences sidebar */}
              <div className="create-form-sidebar">
                <div className="form-section card">
                  <div className="card-body">
                    <h2 className="form-section-title">Preferences</h2>

                    <div className="form-group">
                      <label className="form-label" htmlFor="dietary">Dietary Requirement</label>
                      <select
                        id="dietary"
                        className="form-select"
                        value={dietary}
                        onChange={(e) => setDietary(e.target.value)}
                      >
                        {DIETARY_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="cuisine">Cuisine</label>
                      <select
                        id="cuisine"
                        className="form-select"
                        value={cuisine}
                        onChange={(e) => setCuisine(e.target.value)}
                      >
                        {CUISINE_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="mealType">Meal Type</label>
                      <select
                        id="mealType"
                        className="form-select"
                        value={mealType}
                        onChange={(e) => setMealType(e.target.value)}
                      >
                        {MEAL_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="cookingTime">Available Cooking Time</label>
                      <select
                        id="cookingTime"
                        className="form-select"
                        value={cookingTime}
                        onChange={(e) => setCookingTime(e.target.value)}
                      >
                        {TIME_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="servings">
                        Servings
                        <span className="servings-value">{servings}</span>
                      </label>
                      <input
                        id="servings"
                        type="range"
                        min="1"
                        max="8"
                        value={servings}
                        onChange={(e) => setServings(parseInt(e.target.value))}
                        className="servings-slider"
                      />
                      <div className="servings-labels">
                        <span>1</span>
                        <span>4</span>
                        <span>8</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="form-actions">
                  {error && (
                    <div className="alert alert-error" role="alert">
                      <span>{error}</span>
                    </div>
                  )}

                  <button
                    type="submit"
                    className="btn btn-primary btn-lg"
                    disabled={loading || availableIngredients.length === 0}
                    style={{ width: '100%' }}
                  >
                    {loading ? (
                      <>
                        <div className="spinner" />
                        Generating recipes…
                      </>
                    ) : (
                      'Find My Recipes'
                    )}
                  </button>

                  {loading && (
                    <p className="loading-hint">
                      Retrieving recipes and generating personalised suggestions with IBM watsonx.ai. This may take up to 30 seconds.
                    </p>
                  )}

                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={clearAll}
                    style={{ width: '100%' }}
                  >
                    Clear all
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
