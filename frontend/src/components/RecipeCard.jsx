import React from 'react';
import { Link } from 'react-router-dom';
import { isRecipeSaved, saveRecipe, unsaveRecipe } from '../utils/storage';
import './RecipeCard.css';

function DifficultyBadge({ difficulty }) {
  const cls = difficulty?.toLowerCase() === 'easy' ? 'badge-easy'
    : difficulty?.toLowerCase() === 'hard' ? 'badge-hard'
    : 'badge-medium';
  return <span className={`badge ${cls}`}>{difficulty}</span>;
}

function MatchScore({ score, available, total }) {
  if (score === null || score === undefined) return null;
  const pct = Math.round(score * 100);
  return (
    <div className="match-score">
      <div className="match-score-bar">
        <div className="match-score-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="match-score-label">
        {available}/{total} ingredients
      </span>
    </div>
  );
}

export default function RecipeCard({ recipe, availableIngredients = [], onSelect }) {
  const [saved, setSaved] = React.useState(isRecipeSaved(recipe.id));

  const handleSave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (saved) {
      unsaveRecipe(recipe.id);
    } else {
      saveRecipe(recipe);
    }
    setSaved(!saved);
  };

  const totalTime = (recipe.cooking_time_minutes || 0) + (recipe.prep_time_minutes || 0);

  return (
    <article className="recipe-card" onClick={() => onSelect?.(recipe)}>
      <div className="recipe-card-header">
        <div className="recipe-card-meta-top">
          <span className="recipe-card-cuisine tag tag-neutral">{recipe.cuisine}</span>
          <span className="recipe-card-meal-type">{recipe.meal_type}</span>
        </div>
        <button
          className={`save-btn ${saved ? 'saved' : ''}`}
          onClick={handleSave}
          aria-label={saved ? 'Unsave recipe' : 'Save recipe'}
          title={saved ? 'Remove from saved' : 'Save recipe'}
        >
          {saved ? '♥' : '♡'}
        </button>
      </div>

      <div className="recipe-card-body">
        <h3 className="recipe-card-title">{recipe.name}</h3>
        <p className="recipe-card-description">{recipe.description}</p>

        <MatchScore
          score={recipe.match_score}
          available={recipe.ingredients_available}
          total={recipe.ingredients_total}
        />
      </div>

      <div className="recipe-card-footer">
        <div className="recipe-card-stats">
          <span className="stat" title="Total time">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
            {totalTime} min
          </span>
          <span className="stat" title="Servings">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            {recipe.servings}
          </span>
          <DifficultyBadge difficulty={recipe.difficulty} />
        </div>

        <div className="recipe-card-dietary">
          {(recipe.dietary_info || []).slice(0, 2).map((d) => (
            <span key={d} className="tag tag-accent">{d}</span>
          ))}
        </div>
      </div>
    </article>
  );
}
