import { useState } from 'react';
import { RecipeMatch } from '../../types';
import { Clock, ChefHat, Flame, CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';

interface RecipeCardProps {
  match: RecipeMatch;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ match }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { recipe, match_score, matched_ingredients, missing_ingredients } = match;

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case '简单':
        return 'bg-green-100 text-green-700';
      case '中等':
        return 'bg-yellow-100 text-yellow-700';
      case '困难':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="p-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900">{recipe.name}</h4>
            <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
              <span className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{recipe.time}</span>
              </span>
              <span className={`px-2 py-0.5 rounded-full text-xs ${getDifficultyColor(recipe.difficulty)}`}>
                {recipe.difficulty}
              </span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-orange-500">
              {Math.round(match_score * 100)}%
            </div>
            <div className="text-xs text-gray-400">匹配度</div>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mt-2">
          {recipe.tags.slice(0, 3).map((tag, i) => (
            <span
              key={i}
              className="px-2 py-0.5 bg-orange-50 text-orange-600 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Ingredients Status */}
        <div className="mt-3 space-y-1">
          {matched_ingredients.length > 0 && (
            <div className="flex items-start space-x-2 text-xs">
              <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-gray-600">
                已有: {matched_ingredients.join('、')}
              </span>
            </div>
          )}
          {missing_ingredients.length > 0 && (
            <div className="flex items-start space-x-2 text-xs">
              <XCircle className="w-3 h-3 text-orange-400 mt-0.5 flex-shrink-0" />
              <span className="text-gray-500">
                还需: {missing_ingredients.slice(0, 3).join('、')}
                {missing_ingredients.length > 3 && ` 等${missing_ingredients.length}种`}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-3 bg-white">
          {/* Nutrition */}
          <div className="flex items-center space-x-4 mb-3 text-xs text-gray-600">
            <span className="flex items-center space-x-1">
              <Flame className="w-3 h-3 text-orange-500" />
              <span>{recipe.nutrition.calories}卡</span>
            </span>
            <span>蛋白质 {recipe.nutrition.protein}g</span>
            <span>脂肪 {recipe.nutrition.fat}g</span>
          </div>

          {/* Steps Preview */}
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-700">制作步骤:</p>
            {recipe.steps.slice(0, 3).map((step, i) => (
              <p key={i} className="text-xs text-gray-600 line-clamp-1">
                {i + 1}. {step}
              </p>
            ))}
            {recipe.steps.length > 3 && (
              <p className="text-xs text-gray-400">
                ...还有{recipe.steps.length - 3}步
              </p>
            )}
          </div>

          {/* Tips */}
          {recipe.tips.length > 0 && (
            <div className="mt-3 p-2 bg-yellow-50 rounded-lg">
              <p className="text-xs text-yellow-700">
                💡 {recipe.tips[0]}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Toggle Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full py-2 flex items-center justify-center text-xs text-gray-500 hover:bg-gray-100 transition-colors border-t border-gray-200"
      >
        {isExpanded ? (
          <>
            <ChevronUp className="w-4 h-4 mr-1" />
            收起详情
          </>
        ) : (
          <>
            <ChevronDown className="w-4 h-4 mr-1" />
            查看详情
          </>
        )}
      </button>
    </div>
  );
};