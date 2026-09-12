import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import RecipeCard from '../components/RecipeCard';
import './Suggestions.css';

const SORT_OPTIONS = [
  { value: 'match', label: 'Best Match' },
  { value: 'time', label: 'Quickest First' },
  { value: 'difficulty', label: 'Easiest First' },
];

const FILTER_DIETARY = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'high-protein'];

export default function Suggestions() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state;

  const [sortBy, setSortBy] = useState('match');
  const [filterDietary, setFilterDietary] = useState('');
  const [filterMeal, setFilterMeal] = useState('');

  if (!state || !state.recipes) {
    return (
      <div className="page-wrapper">
        <div className="container">
          <div className="empty-state">
            <h3>No recipes to show</h3>
            <p>Head to the ingredient setup page to generate personalised recipe suggestions.</p>
            <Link to="/create" className="btn btn-primary">Create Recipe</Link>
          </div>
        </div>
      </div>
    );
  }

  const { recipes, querySummary, retrievedCount, availableIngredients } = state;

  // Sort recipes
  const sorted = [...recipes].sort((a, b) => {
    if (sortBy === 'match') return (b.match_score || 0) - (a.match_score || 0);
    if (sortBy === 'time') return ((a.cooking_time_minutes || 0) + (a.prep_time_minutes || 0))
      - ((b.cooking_time_minutes || 0) + (b.prep_time_minutes || 0));
    if (sortBy === 'difficulty') {
      const order = { Easy: 0, Medium: 1, Hard: 2 };
      return (order[a.difficulty] || 1) - (order[b.difficulty] || 1);
    }
    return 0;
  });

  // Filter recipes
  const filtered = sorted.filter((r) => {
    if (filterDietary && !r.dietary_info?.includes(filterDietary)) return false;
    if (filterMeal && r.meal_type !== filterMeal) return false;
    return true;
  });

  const handleSelectRecipe = (recipe) => {
    navigate(`/recipe/${recipe.id}`, {
      state: { recipe, availableIngredients },
    });
  };

  const uniqueMealTypes = [...new Set(recipes.map((r) => r.meal_type))];

  return (
    <div className="page-wrapper">
      <div className="container">
        {/* Header */}
        <div className="suggestions-header">
          <div>
            <Link to="/create" className="back-link">
              ← Edit ingredients
            </Link>
            <h1>Recipe Suggestions</h1>
            <p className="query-summary">{querySummary}</p>
            {retrievedCount > 0 && (
              <p className="rag-info">
                Retrieved {retrievedCount} relevant recipes from knowledge base via RAG.
              </p>
            )}
          </div>
        </div>

        {/* Controls */}
        <div className="suggestions-controls">
          <div className="suggestions-count">
            {filtered.length} recipe{filtered.length !== 1 ? 's' : ''} found
          </div>

          <div className="suggestions-filters">
            {/* Sort */}
            <div className="filter-group">
              <label className="filter-label">Sort:</label>
              <div className="filter-pills">
                {SORT_OPTIONS.map((s) => (
                  <button
                    key={s.value}
                    className={`filter-pill ${sortBy === s.value ? 'active' : ''}`}
                    onClick={() => setSortBy(s.value)}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Dietary filter */}
            <div className="filter-group">
              <label className="filter-label">Dietary:</label>
              <div className="filter-pills">
                <button
                  className={`filter-pill ${filterDietary === '' ? 'active' : ''}`}
                  onClick={() => setFilterDietary('')}
                >All</button>
                {FILTER_DIETARY.map((d) => (
                  <button
                    key={d}
                    className={`filter-pill ${filterDietary === d ? 'active' : ''}`}
                    onClick={() => setFilterDietary(filterDietary === d ? '' : d)}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Meal type filter */}
            {uniqueMealTypes.length > 1 && (
              <div className="filter-group">
                <label className="filter-label">Meal:</label>
                <div className="filter-pills">
                  <button
                    className={`filter-pill ${filterMeal === '' ? 'active' : ''}`}
                    onClick={() => setFilterMeal('')}
                  >All</button>
                  {uniqueMealTypes.map((m) => (
                    <button
                      key={m}
                      className={`filter-pill ${filterMeal === m ? 'active' : ''}`}
                      onClick={() => setFilterMeal(filterMeal === m ? '' : m)}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recipe grid */}
        {filtered.length === 0 ? (
          <div className="empty-state">
            <h3>No recipes match your filters</h3>
            <p>Try removing some filters to see more results.</p>
            <button
              className="btn btn-secondary"
              onClick={() => { setFilterDietary(''); setFilterMeal(''); }}
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div className="suggestions-grid">
            {filtered.map((recipe) => (
              <RecipeCard
                key={recipe.id}
                recipe={recipe}
                availableIngredients={availableIngredients}
                onSelect={handleSelectRecipe}
              />
            ))}
          </div>
        )}

        {/* Available ingredients reminder */}
        {availableIngredients?.length > 0 && (
          <div className="ingredients-reminder card">
            <div className="card-body">
              <p className="ingredients-reminder-label">Your available ingredients</p>
              <div className="ingredient-chips">
                {availableIngredients.map((ing) => (
                  <span key={ing} className="ingredient-chip">{ing}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
