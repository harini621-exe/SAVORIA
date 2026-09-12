import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CreateRecipe from './pages/CreateRecipe';
import Suggestions from './pages/Suggestions';
import RecipeDetail from './pages/RecipeDetail';
import CookingMode from './pages/CookingMode';
import SavedRecipes from './pages/SavedRecipes';
import About from './pages/About';
import './styles/globals.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Cooking mode is fullscreen — no navbar */}
        <Route path="/cook/:id" element={<CookingMode />} />
        
        {/* All other pages have the navbar */}
        <Route
          path="*"
          element={
            <>
              <Navbar />
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/create" element={<CreateRecipe />} />
                <Route path="/suggestions" element={<Suggestions />} />
                <Route path="/recipe/:id" element={<RecipeDetail />} />
                <Route path="/saved" element={<SavedRecipes />} />
                <Route path="/about" element={<About />} />
              </Routes>
            </>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
