export interface Nutrition {
  calories: number;
  protein: number;
  fat: number;
  carbs: number;
  fiber: number;
}

export interface Ingredient {
  name: string;
  amount: string;
  category: string;
}

export interface Recipe {
  id: number;
  name: string;
  name_en: string;
  category: string;
  difficulty: string;
  time: string;
  servings: number;
  ingredients: Ingredient[];
  substitutions: Record<string, string[]>;
  nutrition: Nutrition;
  tags: string[];
  steps: string[];
  tips: string[];
}

export interface RecipeMatch {
  recipe: Recipe;
  match_score: number;
  matched_ingredients: string[];
  missing_ingredients: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  suggested_recipes?: RecipeMatch[];
  detected_ingredients?: string[];
  detected_restrictions?: string[];
  nutrition_info?: {
    per_serving: Nutrition;
    daily_percentage: Record<string, number>;
    health_tips: string[];
  };
}