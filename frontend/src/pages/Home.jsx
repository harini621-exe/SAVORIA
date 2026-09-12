import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const FEATURES = [
  {
    icon: '◈',
    title: 'Ingredient-Based Discovery',
    description: 'Enter what you have — SAVORIA finds and creates recipes tailored to your pantry, minimising waste and shopping.',
  },
  {
    icon: '◎',
    title: 'RAG-Powered Retrieval',
    description: 'A FAISS vector index retrieves the most relevant recipe context from our curated knowledge base before generation.',
  },
  {
    icon: '◇',
    title: 'IBM watsonx.ai Generation',
    description: 'IBM foundation models generate detailed, personalised recipes adapted to your dietary needs and preferences.',
  },
  {
    icon: '◈',
    title: 'Dietary Adaptation',
    description: 'Vegetarian, vegan, gluten-free, dairy-free, high-protein, and more — every recipe is adapted to your requirements.',
  },
  {
    icon: '◎',
    title: 'Smart Substitutions',
    description: 'Missing an ingredient? SAVORIA suggests practical alternatives so you can cook with confidence from what you have.',
  },
  {
    icon: '◇',
    title: 'Step-by-Step Cooking Mode',
    description: 'Follow a focused, distraction-free cooking interface one step at a time with progress tracking.',
  },
];

const CUISINES = [
  'Italian', 'Indian', 'Mexican', 'Asian', 'Mediterranean',
  'Middle Eastern', 'French', 'Japanese', 'Greek', 'Contemporary',
];

export default function Home() {
  return (
    <div className="home">
      {/* Hero */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <span className="hero-overline">AI-Powered Recipe Intelligence</span>
            <h1 className="hero-title">
              Cook brilliantly with<br />
              <span className="hero-title-accent">what you already have.</span>
            </h1>
            <p className="hero-description">
              SAVORIA uses Retrieval-Augmented Generation and IBM watsonx.ai to turn
              your available ingredients into personalised, professional meal suggestions —
              tailored to your dietary preferences, time, and taste.
            </p>
            <div className="hero-actions">
              <Link to="/create" className="btn btn-primary btn-lg">
                Start Cooking
              </Link>
              <Link to="/about" className="btn btn-secondary btn-lg">
                How It Works
              </Link>
            </div>
          </div>
          <div className="hero-visual" aria-hidden="true">
            <div className="hero-visual-inner">
              <div className="hero-recipe-preview">
                <div className="preview-line preview-title" />
                <div className="preview-line preview-short" />
                <div className="preview-ingredients">
                  {['garlic', 'pasta', 'olive oil', 'tomato', 'basil'].map((ing) => (
                    <span key={ing} className="preview-chip">{ing}</span>
                  ))}
                </div>
                <div className="preview-steps">
                  {[85, 70, 90, 60].map((w, i) => (
                    <div key={i} className="preview-step">
                      <div className="preview-step-num">{i + 1}</div>
                      <div className="preview-step-line" style={{ width: `${w}%` }} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cuisine strip */}
      <section className="cuisine-strip">
        <div className="container">
          <p className="cuisine-strip-label">Cuisines supported</p>
          <div className="cuisine-list">
            {CUISINES.map((c) => (
              <span key={c} className="cuisine-pill">{c}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="features-section">
        <div className="container">
          <div className="section-heading">
            <span className="overline">Capabilities</span>
            <h2>Everything you need to cook smarter</h2>
            <p>SAVORIA combines knowledge retrieval and AI generation into a seamless ingredient-to-meal workflow.</p>
          </div>
          <div className="features-grid">
            {FEATURES.map((f) => (
              <div key={f.title} className="feature-card">
                <div className="feature-icon" aria-hidden="true">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="workflow-section">
        <div className="container">
          <div className="section-heading">
            <span className="overline">How SAVORIA Works</span>
            <h2>From ingredients to plate</h2>
          </div>
          <div className="workflow-steps">
            {[
              { step: '01', title: 'Enter Your Ingredients', desc: 'List what you have in your fridge and pantry.' },
              { step: '02', title: 'Set Your Preferences', desc: 'Choose dietary requirements, cuisine, meal type, and cooking time.' },
              { step: '03', title: 'RAG Retrieval', desc: 'FAISS retrieves the most relevant recipes from our knowledge base.' },
              { step: '04', title: 'AI Generation', desc: 'IBM watsonx.ai generates personalised recipes with substitutions.' },
              { step: '05', title: 'Cook with Confidence', desc: 'Follow step-by-step cooking mode to prepare your meal.' },
            ].map((s, i) => (
              <div key={s.step} className="workflow-step">
                <div className="workflow-step-num">{s.step}</div>
                <div>
                  <h4>{s.title}</h4>
                  <p>{s.desc}</p>
                </div>
                {i < 4 && <div className="workflow-connector" aria-hidden="true" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-card">
            <h2>Ready to cook something delicious?</h2>
            <p>Enter your available ingredients and let SAVORIA generate your next meal.</p>
            <Link to="/create" className="btn btn-primary btn-lg">
              Create My Recipe
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
