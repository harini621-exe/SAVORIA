/**
 * SAVORIA API Client
 * Centralised Axios instance for all backend communication.
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 90000, // 90s — AI generation can take time
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging in development
api.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.debug(`[SAVORIA API] ${config.method?.toUpperCase()} ${config.url}`);
  }
  return config;
});

// Response error normalisation
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred. Please try again.';
    return Promise.reject(new Error(message));
  }
);

// ─── API Functions ──────────────────────────────────────────────────────────

export const generateRecipes = (requestData) =>
  api.post('/api/recipes/generate', requestData).then((r) => r.data);

export const getRecipeDetail = (recipeId, ingredients = []) => {
  const params = ingredients.length ? `?ingredients=${ingredients.join(',')}` : '';
  return api.get(`/api/recipes/${recipeId}${params}`).then((r) => r.data);
};

export const listRecipes = (filters = {}) => {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') params.append(k, v);
  });
  return api.get(`/api/recipes?${params}`).then((r) => r.data);
};

export const getSubstitutions = (ingredient, availableIngredients = []) =>
  api
    .post('/api/substitutions', {
      ingredient,
      available_ingredients: availableIngredients,
    })
    .then((r) => r.data);

export const analyseIngredients = (ingredients) =>
  api.post('/api/ingredients/analyse', ingredients).then((r) => r.data);

export const healthCheck = () => api.get('/api/health').then((r) => r.data);

export default api;
