from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class Ingredient(BaseModel):
    name: str
    amount: str
    category: str


class Nutrition(BaseModel):
    calories: int
    protein: float
    fat: float
    carbs: float
    fiber: float


class Recipe(BaseModel):
    id: int
    name: str
    name_en: str
    category: str
    difficulty: str
    time: str
    servings: int
    ingredients: List[Ingredient]
    substitutions: Dict[str, List[str]]
    nutrition: Nutrition
    tags: List[str]
    steps: List[str]
    tips: List[str]


class RecipeListItem(BaseModel):
    id: int
    name: str
    difficulty: str
    time: str
    tags: List[str]
    match_score: Optional[float] = None