import React from 'react';
import { Link } from 'react-router-dom';
import './About.css';

const TECH_STACK = [
  { category: 'Frontend', items: ['React 18', 'React Router v6', 'Vite', 'Axios', 'CSS Custom Properties'] },
  { category: 'Backend', items: ['Python 3.11+', 'FastAPI', 'Pydantic v2', 'Uvicorn', 'HTTPx'] },
  { category: 'RAG & Retrieval', items: ['FAISS (Facebook AI Similarity Search)', 'sentence-transformers (all-MiniLM-L6-v2)', 'NumPy', 'scikit-learn'] },
  { category: 'AI Generation', items: ['IBM watsonx.ai', 'Meta LLaMA 3.3 70B Instruct', 'IBM IAM Authentication'] },
  { category: 'Storage', items: ['Browser localStorage (recipes, progress)', 'JSON flat-file knowledge base', 'FAISS binary index'] },
];

const WORKFLOW_STEPS = [
  {
    step: '01',
    title: 'Ingredient & Preference Analysis',
    desc: 'The Ingredient Analyzer normalises, deduplicates, and categorises your input. The Preference Analyzer validates dietary requirements and maps aliases.',
    agent: 'IngredientAnalyzer · PreferenceAnalyzer',
  },
  {
    step: '02',
    title: 'RAG Retrieval (FAISS)',
    desc: 'A FAISS cosine-similarity vector index built from sentence-transformer embeddings of the recipe knowledge base retrieves the top-K most relevant recipes.',
    agent: 'RecipeRAG · FAISS IndexFlatIP',
  },
  {
    step: '03',
    title: 'Context Construction',
    desc: 'Retrieved recipes, substitution advice, and dietary adaptation rules are assembled into a structured prompt for the foundation model.',
    agent: 'SubstitutionAdvisor · DietaryAdapter',
  },
  {
    step: '04',
    title: 'IBM watsonx.ai Generation',
    desc: 'The RecipeGenerator sends the structured prompt to IBM watsonx.ai (Meta LLaMA 3.3 70B Instruct) via the REST API to generate personalised recipes.',
    agent: 'RecipeGenerator · WatsonxClient',
  },
  {
    step: '05',
    title: 'Recipe Planning & Structuring',
    desc: 'The RecipePlanner orchestrates all agents, sanitises the generated output, computes ingredient availability, and builds the complete structured response.',
    agent: 'RecipePlanner',
  },
  {
    step: '06',
    title: 'Cooking Mode',
    desc: 'A focused step-by-step interface with progress tracking, keyboard navigation, and local storage persistence guides the user through preparation.',
    agent: 'Frontend CookingMode',
  },
];

export default function About() {
  return (
    <div className="page-wrapper">
      <div className="container">
        <div className="about-page">
          {/* Header */}
          <div className="about-header">
            <div className="section-heading">
              <span className="overline">About SAVORIA</span>
              <h1>AI-Powered Recipe Intelligence</h1>
              <p>
                SAVORIA is a full-stack intelligent recipe preparation agent that combines
                Retrieval-Augmented Generation (RAG) and IBM watsonx.ai to generate
                personalised, practical meal suggestions from your available ingredients.
              </p>
            </div>
          </div>

          {/* Problem & Solution */}
          <div className="about-section">
            <div className="about-two-col">
              <div>
                <h2>The Problem</h2>
                <p>
                  People frequently waste food because they do not know what meals they can prepare
                  with what they already have. Generic recipe search requires knowing what to cook
                  in advance and rarely adapts to available ingredients, dietary restrictions,
                  or time constraints.
                </p>
              </div>
              <div>
                <h2>The SAVORIA Solution</h2>
                <p>
                  SAVORIA inverts the traditional recipe-search paradigm — you provide ingredients,
                  and SAVORIA retrieves and generates adapted recipes. The RAG pipeline ensures
                  generation is grounded in a real recipe knowledge base rather than hallucinated content.
                </p>
              </div>
            </div>
          </div>

          {/* Architecture */}
          <div className="about-section">
            <div className="section-heading">
              <span className="overline">System Architecture</span>
              <h2>How SAVORIA Works</h2>
            </div>
            <div className="workflow-diagram">
              {WORKFLOW_STEPS.map((s, i) => (
                <div key={s.step} className="workflow-diagram-step">
                  <div className="wf-number">{s.step}</div>
                  <div className="wf-content">
                    <h3>{s.title}</h3>
                    <p>{s.desc}</p>
                    <span className="wf-agent">{s.agent}</span>
                  </div>
                  {i < WORKFLOW_STEPS.length - 1 && (
                    <div className="wf-connector" aria-hidden="true" />
                  )}
                </div>
              ))}
            </div>
            <div className="architecture-diagram-note">
              <p>See <code>docs/architecture.png</code> for the full technical architecture diagram.</p>
            </div>
          </div>

          {/* RAG Pipeline */}
          <div className="about-section">
            <div className="section-heading">
              <span className="overline">RAG Pipeline</span>
              <h2>Retrieval-Augmented Generation</h2>
            </div>
            <div className="rag-pipeline-card card">
              <div className="card-body">
                <div className="rag-pipeline-steps">
                  {[
                    { label: 'Recipe Knowledge Base', desc: '20 curated recipes in JSON format covering multiple cuisines, meal types, and dietary requirements.' },
                    { label: 'Sentence Embedding', desc: 'Each recipe is converted to a dense vector using all-MiniLM-L6-v2 from sentence-transformers.' },
                    { label: 'FAISS Index', desc: 'Normalised embeddings are stored in a FAISS IndexFlatIP for cosine-similarity nearest-neighbour search.' },
                    { label: 'Query Construction', desc: 'User ingredients, dietary preferences, and meal type are assembled into a rich query string and embedded.' },
                    { label: 'Top-K Retrieval', desc: 'The top-K most semantically similar recipes are retrieved, scored by both semantic similarity and ingredient match ratio.' },
                    { label: 'Context Assembly', desc: 'Retrieved recipes, substitution guidance, and dietary adaptation rules are injected into the generation prompt.' },
                    { label: 'Foundation Model Generation', desc: 'IBM watsonx.ai generates 3 personalised recipes using the assembled RAG context, ensuring groundedness.' },
                  ].map((item, i) => (
                    <div key={i} className="rag-step">
                      <div className="rag-step-num">{i + 1}</div>
                      <div>
                        <strong>{item.label}</strong>
                        <p>{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Tech stack */}
          <div className="about-section">
            <div className="section-heading">
              <span className="overline">Technology</span>
              <h2>Technology Stack</h2>
            </div>
            <div className="tech-grid">
              {TECH_STACK.map((cat) => (
                <div key={cat.category} className="tech-card card">
                  <div className="card-body">
                    <h3>{cat.category}</h3>
                    <ul>
                      {cat.items.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="about-cta">
            <h2>Try SAVORIA</h2>
            <p>Enter your available ingredients to generate your first personalised recipe.</p>
            <Link to="/create" className="btn btn-primary btn-lg">Start Cooking</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
