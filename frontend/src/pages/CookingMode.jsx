import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom';
import { getRecipeDetail } from '../utils/api';
import { getCookingProgress, saveCookingProgress, clearCookingProgress } from '../utils/storage';
import './CookingMode.css';

export default function CookingMode() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state || {};

  const [recipe, setRecipe] = useState(state.recipe || null);
  const [loading, setLoading] = useState(!state.recipe);
  const [error, setError] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [showIngredients, setShowIngredients] = useState(false);

  useEffect(() => {
    if (!recipe) {
      getRecipeDetail(id, state.availableIngredients || [])
        .then((data) => {
          setRecipe(data.recipe);
          const progress = getCookingProgress(data.recipe.id);
          setCurrentStep(progress.currentStep || 0);
        })
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    } else {
      const progress = getCookingProgress(recipe.id);
      setCurrentStep(progress.currentStep || 0);
    }
  }, [id]);

  useEffect(() => {
    if (recipe) {
      saveCookingProgress(recipe.id, { currentStep, completed });
    }
  }, [currentStep, completed, recipe]);

  const steps = recipe?.steps || [];
  const totalSteps = steps.length;
  const currentStepData = steps[currentStep];
  const progress = totalSteps > 0 ? ((currentStep) / totalSteps) * 100 : 0;

  const goNext = useCallback(() => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep((s) => s + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      setCompleted(true);
      clearCookingProgress(recipe.id);
    }
  }, [currentStep, totalSteps, recipe]);

  const goPrev = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((s) => s - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [currentStep]);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') goNext();
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') goPrev();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [goNext, goPrev]);

  if (loading) {
    return (
      <div className="cooking-mode">
        <div className="cooking-loading">
          <div className="spinner" style={{ width: 32, height: 32 }} />
          <p>Loading recipe…</p>
        </div>
      </div>
    );
  }

  if (error || !recipe) {
    return (
      <div className="cooking-mode">
        <div className="cooking-error">
          <h2>Recipe not found</h2>
          <p>{error}</p>
          <Link to="/create" className="btn btn-primary">Back to Start</Link>
        </div>
      </div>
    );
  }

  if (completed) {
    return (
      <div className="cooking-mode">
        <div className="cooking-complete">
          <div className="complete-icon">✓</div>
          <h1>Recipe Complete!</h1>
          <h2 className="complete-recipe-name">{recipe.name}</h2>
          <p>Well done — your meal is ready. Enjoy!</p>
          <div className="complete-actions">
            <button
              className="btn btn-secondary"
              onClick={() => { setCompleted(false); setCurrentStep(0); }}
            >
              Cook Again
            </button>
            <Link to={`/recipe/${recipe.id}`} className="btn btn-secondary">
              View Recipe
            </Link>
            <Link to="/create" className="btn btn-primary">
              Find Another Recipe
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cooking-mode">
      {/* Header */}
      <div className="cooking-header">
        <button
          className="cooking-back"
          onClick={() => navigate(-1)}
          aria-label="Exit cooking mode"
        >
          ← Exit
        </button>
        <div className="cooking-header-title">
          <h2>{recipe.name}</h2>
          <div className="cooking-time-info">
            {recipe.cooking_time_minutes} min cook · {recipe.servings} servings
          </div>
        </div>
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setShowIngredients(!showIngredients)}
        >
          {showIngredients ? 'Hide' : 'Show'} All Ingredients
        </button>
      </div>

      {/* Ingredients drawer */}
      {showIngredients && (
        <div className="cooking-ingredients-drawer">
          <div className="cooking-ingredients-grid">
            {recipe.ingredients?.map((ing, i) => (
              <div key={i} className={`cooking-ingredient ${ing.available ? 'available' : 'missing'}`}>
                <span className="ci-dot" />
                <span className="ci-name">{ing.name}</span>
                {(ing.quantity || ing.unit) && (
                  <span className="ci-qty">{ing.quantity} {ing.unit}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Progress */}
      <div className="cooking-progress">
        <div className="progress-bar-track">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="cooking-progress-label">
          Step {currentStep + 1} of {totalSteps}
        </div>
      </div>

      {/* Step breadcrumbs */}
      <div className="step-breadcrumbs">
        {steps.map((_, i) => (
          <button
            key={i}
            className={`step-dot ${i < currentStep ? 'done' : ''} ${i === currentStep ? 'current' : ''}`}
            onClick={() => setCurrentStep(i)}
            aria-label={`Go to step ${i + 1}`}
          />
        ))}
      </div>

      {/* Main step card */}
      {currentStepData && (
        <div className="cooking-step-card">
          <div className="step-card-number">Step {currentStepData.step_number}</div>
          <p className="step-card-instruction">{currentStepData.instruction}</p>

          {currentStepData.required_ingredients?.length > 0 && (
            <div className="step-card-ingredients">
              <span className="step-card-ing-label">For this step:</span>
              <div className="step-card-ing-chips">
                {currentStepData.required_ingredients.map((ing) => (
                  <span key={ing} className="tag tag-primary">{ing}</span>
                ))}
              </div>
            </div>
          )}

          {currentStepData.tip && (
            <div className="step-card-tip">
              <span className="step-tip-label">Tip</span>
              <p>{currentStepData.tip}</p>
            </div>
          )}
        </div>
      )}

      {/* Navigation */}
      <div className="cooking-nav">
        <button
          className="btn btn-secondary btn-lg cooking-nav-btn"
          onClick={goPrev}
          disabled={currentStep === 0}
        >
          ← Previous
        </button>
        <div className="cooking-keyboard-hint">
          Use arrow keys to navigate
        </div>
        <button
          className="btn btn-primary btn-lg cooking-nav-btn"
          onClick={goNext}
        >
          {currentStep === totalSteps - 1 ? 'Complete Recipe' : 'Next Step →'}
        </button>
      </div>
    </div>
  );
}
