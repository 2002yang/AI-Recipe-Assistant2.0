import axios from 'axios';
import { ChatResponse, Recipe, RecipeMatch } from '../types';

const API_BASE = '/api';

export const chatApi = {
  sendMessage: async (
    message: string, 
    conversationId?: string
  ): Promise<ChatResponse> => {
    const response = await axios.post(`${API_BASE}/chat/message`, {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },

  createConversation: async (): Promise<{ conversation_id: string; message: string }> => {
    const response = await axios.post(`${API_BASE}/chat/new`);
    return response.data;
  },

  getHistory: async (conversationId: string) => {
    const response = await axios.get(`${API_BASE}/chat/history/${conversationId}`);
    return response.data;
  },
};

export const recipeApi = {
  getAllRecipes: async (): Promise<Recipe[]> => {
    const response = await axios.get(`${API_BASE}/recipes/list`);
    return response.data;
  },

  getRecipe: async (id: number): Promise<Recipe> => {
    const response = await axios.get(`${API_BASE}/recipes/${id}`);
    return response.data;
  },

  searchByIngredients: async (
    ingredients: string[],
    restrictions?: string[]
  ): Promise<{ results: RecipeMatch[] }> => {
    const response = await axios.post(`${API_BASE}/recipes/search`, {
      ingredients,
      restrictions,
    });
    return response.data;
  },

  getSubstitutions: async (recipeId: number, ingredientName: string) => {
    const response = await axios.get(
      `${API_BASE}/recipes/${recipeId}/substitutions/${ingredientName}`
    );
    return response.data;
  },
};

export const nutritionApi = {
  getRecipeNutrition: async (recipeId: number) => {
    const response = await axios.get(`${API_BASE}/nutrition/recipe/${recipeId}`);
    return response.data;
  },

  checkDietSuitability: async (recipeId: number, dietType: string) => {
    const response = await axios.get(
      `${API_BASE}/nutrition/recipe/${recipeId}/diet/${dietType}`
    );
    return response.data;
  },
};