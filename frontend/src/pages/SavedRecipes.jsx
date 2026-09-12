import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getSavedRecipes, getRecentRecipes, unsaveRecipe } from '../utils/storage';
import RecipeCard from '../components/RecipeCard';
import './SavedRecipes.css';

export default function SavedRecipes() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('saved');
  const [savedRecipes, setSavedRecipes] = useState(getSavedRecipes());
  const [recentRecipes, setRecentRecipes] = useState(getRecentRecipes());

  useEffect(() => {
    setSavedRecipes(getSavedRecipes());
    setRecentRecipes(getRecentRecipes());
  }, [activeTab]);

  const handleUnsave = (id) => {
    unsaveRecipe(id);
    setSavedRecipes(getSavedRecipes());
  };

  const handleSelect = (recipe) => {
    navigate(`/recipe/${recipe.id}`, { state: { recipe } });
  };

  const displayList = activeTab === 'saved' ? savedRecipes : recentRecipes;

  return (
    <div className="page-wrapper">
      <div className="container">
        <div className="saved-page">
          <div className="page-header">
            <h1>My Recipes</h1>
            <p>Your saved recipes and recently viewed meals.</p>
          </div>

          <div className="saved-tabs">
            <button
              className={`recipe-tab ${activeTab === 'saved' ? 'active' : ''}`}
              onClick={() => setActiveTab('saved')}
            >
              Saved ({savedRecipes.length})
            </button>
            <button
              className={`recipe-tab ${activeTab === 'recent' ? 'active' : ''}`}
              onClick={() => setActiveTab('recent')}
            >
              Recently Viewed ({recentRecipes.length})
            </button>
          </div>

          {displayList.length === 0 ? (
            <div className="empty-state">
              {activeTab === 'saved' ? (
                <>
                  <h3>No saved recipes yet</h3>
                  <p>Save recipes from suggestions or recipe detail pages to find them here quickly.</p>
                  <Link to="/create" className="btn btn-primary">Find Recipes</Link>
                </>
              ) : (
                <>
                  <h3>No recently viewed recipes</h3>
                  <p>Recipes you view will appear here for quick access.</p>
                  <Link to="/create" className="btn btn-primary">Browse Recipes</Link>
                </>
              )}
            </div>
          ) : (
            <div className="suggestions-grid">
              {displayList.map((recipe) => (
                <RecipeCard
                  key={recipe.id}
                  recipe={recipe}
                  onSelect={handleSelect}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
