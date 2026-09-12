import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { getRecipeDetail, getSubstitutions } from '../utils/api';
import { saveRecipe, unsaveRecipe, isRecipeSaved, addRecentRecipe } from '../utils/storage';
import './RecipeDetail.css';

function IngredientsList({ ingredients }) {
  return (
    <div className="ingredients-list">
      {ingredients.map((ing, i) => (
        <div key={i} className={`ingredient-row ${ing.available ? 'available' : 'missing'}`}>
          <div className="ingredient-status-dot" />
          <span className="ingredient-name">{ing.name}</span>
          {(ing.quantity || ing.unit) && (
            <span className="ingredient-qty">{ing.quantity} {ing.unit}</span>
          )}
          {!ing.available && (
            <span className="ingredient-missing-label">Need to source</span>
          )}
        </div>
      ))}
    </div>
  );
}

function WasteReductionPanel({ wasteReduction }) {
  if (!wasteReduction) return null;
  const { ingredients_used, ingredients_leftover, leftover_suggestions } = wasteReduction;
  return (
    <div className="waste-panel">
      <h3>Food Waste Reduction</h3>
      <div className="waste-grid">
        <div className="waste-section">
          <h4 className="waste-section-title used">Using from your kitchen</h4>
          <div className="waste-ingredients">
            {ingredients_used.map((ing) => (
              <span key={ing} className="ingredient-chip">{ing}</span>
            ))}
            {ingredients_used.length === 0 && <span className="waste-none">None identified</span>}
          </div>
        </div>
        <div className="waste-section">
          <h4 className="waste-section-title leftover">Remaining ingredients</h4>
          <div className="waste-ingredients">
            {ingredients_leftover.map((ing) => (
              <span key={ing} className="ingredient-chip missing">{ing}</span>
            ))}
            {ingredients_leftover.length === 0 && (
              <span className="waste-none">None — great use of your ingredients!</span>
            )}
          </div>
        </div>
      </div>
      {leftover_suggestions && (
        <p className="leftover-suggestions">{leftover_suggestions}</p>
      )}
    </div>
  );
}

function SubstitutionPanel({ substitutions }) {
  if (!substitutions || substitutions.length === 0) return null;
  return (
    <div className="substitution-panel">
      <h3>Ingredient Substitutions</h3>
      <div className="substitution-list">
        {substitutions.map((sub, i) => (
          <div key={i} className="substitution-item">
            <div className="sub-original">{sub.original}</div>
            <div className="sub-arrow">→</div>
            <div className="sub-details">
              <span className="sub-substitute">{sub.substitute}</span>
              {sub.quantity_guidance && (
                <span className="sub-guidance">{sub.quantity_guidance}</span>
              )}
              {sub.effect_on_recipe && (
                <span className="sub-effect">{sub.effect_on_recipe}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function RecipeDetail() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state || {};

  const [recipe, setRecipe] = useState(state.recipe || null);
  const [similarRecipes, setSimilarRecipes] = useState([]);
  const [loading, setLoading] = useState(!state.recipe);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);
  const [activeTab, setActiveTab] = useState('ingredients');

  const availableIngredients = state.availableIngredients || [];

  useEffect(() => {
    if (!recipe) {
      setLoading(true);
      getRecipeDetail(id, availableIngredients)
        .then((data) => {
          setRecipe(data.recipe);
          setSimilarRecipes(data.similar_recipes || []);
          addRecentRecipe(data.recipe);
          setSaved(isRecipeSaved(data.recipe.id));
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    } else {
      addRecentRecipe(recipe);
      setSaved(isRecipeSaved(recipe.id));
    }
  }, [id]);

  const handleSave = () => {
    if (saved) {
      unsaveRecipe(recipe.id);
    } else {
      saveRecipe(recipe);
    }
    setSaved(!saved);
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <div className="container">
          <div className="loading-container">
            <div className="spinner" style={{ width: 32, height: 32 }} />
            <p>Loading recipe…</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="page-wrapper">
        <div className="container">
          <div className="empty-state">
            <h3>Recipe not found</h3>
            <p>{error || 'This recipe could not be loaded.'}</p>
            <Link to="/create" className="btn btn-primary">Find More Recipes</Link>
          </div>
        </div>
      </div>
    );
  }

  const totalTime = (recipe.cooking_time_minutes || 0) + (recipe.prep_time_minutes || 0);
  const availableCount = recipe.ingredients?.filter((i) => i.available).length || 0;
  const totalIngredients = recipe.ingredients?.length || 0;

  return (
    <div className="page-wrapper">
      <div className="container">
        <div className="recipe-detail-page">
          {/* Back navigation */}
          <button className="back-link" onClick={() => navigate(-1)}>
            ← Back to suggestions
          </button>

          {/* Recipe header */}
          <div className="recipe-detail-header">
            <div className="recipe-detail-meta">
              <div className="recipe-detail-tags">
                <span className="tag tag-neutral">{recipe.cuisine}</span>
                <span className="tag tag-neutral" style={{ textTransform: 'capitalize' }}>{recipe.meal_type}</span>
                {recipe.dietary_info?.map((d) => (
                  <span key={d} className="tag tag-accent">{d}</span>
                ))}
              </div>
              <h1 className="recipe-detail-title">{recipe.name}</h1>
              <p className="recipe-detail-description">{recipe.description}</p>

              <div className="recipe-stats-row">
                <div className="recipe-stat">
                  <span className="recipe-stat-label">Prep time</span>
                  <span className="recipe-stat-value">{recipe.prep_time_minutes} min</span>
                </div>
                <div className="recipe-stat-divider" />
                <div className="recipe-stat">
                  <span className="recipe-stat-label">Cook time</span>
                  <span className="recipe-stat-value">{recipe.cooking_time_minutes} min</span>
                </div>
                <div className="recipe-stat-divider" />
                <div className="recipe-stat">
                  <span className="recipe-stat-label">Total</span>
                  <span className="recipe-stat-value">{totalTime} min</span>
                </div>
                <div className="recipe-stat-divider" />
                <div className="recipe-stat">
                  <span className="recipe-stat-label">Serves</span>
                  <span className="recipe-stat-value">{recipe.servings}</span>
                </div>
                <div className="recipe-stat-divider" />
                <div className="recipe-stat">
                  <span className="recipe-stat-label">Difficulty</span>
                  <span className="recipe-stat-value">{recipe.difficulty}</span>
                </div>
              </div>

              {recipe.match_score !== null && recipe.match_score !== undefined && (
                <div className="ingredient-match-info">
                  <div className="match-bar-container">
                    <div
                      className="match-bar-fill"
                      style={{ width: `${Math.round((recipe.match_score || 0) * 100)}%` }}
                    />
                  </div>
                  <span className="match-label">
                    {availableCount}/{totalIngredients} ingredients available
                  </span>
                </div>
              )}
            </div>

            <div className="recipe-detail-actions">
              <button
                className={`btn ${saved ? 'btn-primary' : 'btn-secondary'}`}
                onClick={handleSave}
              >
                {saved ? '♥ Saved' : '♡ Save Recipe'}
              </button>
              <button
                className="btn btn-accent"
                onClick={() =>
                  navigate(`/cook/${recipe.id}`, {
                    state: { recipe, availableIngredients },
                  })
                }
              >
                Start Cooking
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="recipe-tabs">
            {['ingredients', 'instructions', 'substitutions', 'tips'].map((tab) => (
              <button
                key={tab}
                className={`recipe-tab ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          <div className="recipe-tab-content">
            {activeTab === 'ingredients' && (
              <div className="tab-panel">
                <div className="ingredients-section">
                  <div className="ingredients-legend">
                    <span className="legend-item">
                      <span className="ingredient-status-dot available" />
                      You have this
                    </span>
                    <span className="legend-item">
                      <span className="ingredient-status-dot missing" />
                      Need to source
                    </span>
                  </div>
                  <IngredientsList ingredients={recipe.ingredients || []} />
                </div>
                <WasteReductionPanel wasteReduction={recipe.waste_reduction} />
              </div>
            )}

            {activeTab === 'instructions' && (
              <div className="tab-panel">
                <div className="steps-list">
                  {(recipe.steps || []).map((step) => (
                    <div key={step.step_number} className="step-item">
                      <div className="step-number">{step.step_number}</div>
                      <div className="step-content">
                        <p className="step-instruction">{step.instruction}</p>
                        {step.required_ingredients?.length > 0 && (
                          <div className="step-ingredients">
                            {step.required_ingredients.map((ing) => (
                              <span key={ing} className="tag tag-primary">{ing}</span>
                            ))}
                          </div>
                        )}
                        {step.tip && (
                          <div className="step-tip">
                            <strong>Tip:</strong> {step.tip}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'substitutions' && (
              <div className="tab-panel">
                <SubstitutionPanel substitutions={recipe.substitutions} />
                {(!recipe.substitutions || recipe.substitutions.length === 0) && (
                  <div className="empty-state" style={{ padding: 'var(--space-10)' }}>
                    <h3>No substitutions listed</h3>
                    <p>This recipe works well as-is with the ingredients listed.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'tips' && (
              <div className="tab-panel">
                <div className="tips-section">
                  {recipe.cooking_tips?.length > 0 ? (
                    <ul className="tips-list">
                      {recipe.cooking_tips.map((tip, i) => (
                        <li key={i} className="tip-item">{tip}</li>
                      ))}
                    </ul>
                  ) : (
                    <div className="empty-state" style={{ padding: 'var(--space-10)' }}>
                      <h3>No additional tips</h3>
                      <p>Follow the instructions as listed.</p>
                    </div>
                  )}
                  {recipe.nutrition && (
                    <div className="nutrition-panel">
                      <h3>Nutritional Information</h3>
                      <p className="nutrition-disclaimer">Approximate values per serving.</p>
                      <div className="nutrition-grid">
                        {recipe.nutrition.calories_per_serving && (
                          <div className="nutrition-item">
                            <span className="nutrition-value">{recipe.nutrition.calories_per_serving}</span>
                            <span className="nutrition-label">Calories</span>
                          </div>
                        )}
                        {recipe.nutrition.protein && (
                          <div className="nutrition-item">
                            <span className="nutrition-value">{recipe.nutrition.protein}</span>
                            <span className="nutrition-label">Protein</span>
                          </div>
                        )}
                        {recipe.nutrition.carbs && (
                          <div className="nutrition-item">
                            <span className="nutrition-value">{recipe.nutrition.carbs}</span>
                            <span className="nutrition-label">Carbs</span>
                          </div>
                        )}
                        {recipe.nutrition.fat && (
                          <div className="nutrition-item">
                            <span className="nutrition-value">{recipe.nutrition.fat}</span>
                            <span className="nutrition-label">Fat</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
