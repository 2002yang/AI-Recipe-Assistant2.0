import { Nutrition } from '../../types';
import { Flame, Dumbbell, Droplet, Wheat, Leaf } from 'lucide-react';

interface NutritionPanelProps {
  nutrition: {
    per_serving: Nutrition;
    daily_percentage: Record<string, number>;
    health_tips: string[];
  };
}

export const NutritionPanel: React.FC<NutritionPanelProps> = ({ nutrition }) => {
  const { per_serving, daily_percentage, health_tips } = nutrition;

  const nutritionItems = [
    {
      label: '热量',
      value: per_serving.calories,
      unit: '千卡',
      percentage: daily_percentage.calories,
      icon: Flame,
      color: 'text-orange-500',
      bgColor: 'bg-orange-50',
    },
    {
      label: '蛋白质',
      value: per_serving.protein,
      unit: '克',
      percentage: daily_percentage.protein,
      icon: Dumbbell,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
    },
    {
      label: '脂肪',
      value: per_serving.fat,
      unit: '克',
      percentage: daily_percentage.fat,
      icon: Droplet,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50',
    },
    {
      label: '碳水',
      value: per_serving.carbs,
      unit: '克',
      percentage: daily_percentage.carbs,
      icon: Wheat,
      color: 'text-green-500',
      bgColor: 'bg-green-50',
    },
    {
      label: '纤维',
      value: per_serving.fiber,
      unit: '克',
      percentage: null,
      icon: Leaf,
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-50',
    },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-orange-100 overflow-hidden">
      <div className="bg-gradient-to-r from-green-500 to-emerald-500 px-4 py-3">
        <div className="flex items-center space-x-2 text-white">
          <Flame className="w-5 h-5" />
          <h3 className="font-semibold">营养信息（每份）</h3>
        </div>
      </div>

      <div className="p-4">
        {/* Nutrition Grid */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {nutritionItems.slice(0, 3).map((item, index) => (
            <div key={index} className={`${item.bgColor} rounded-xl p-3 text-center`}>
              <item.icon className={`w-5 h-5 ${item.color} mx-auto mb-1`} />
              <div className="text-lg font-bold text-gray-800">
                {item.value}
                <span className="text-xs font-normal text-gray-500 ml-0.5">
                  {item.unit}
                </span>
              </div>
              <div className="text-xs text-gray-500">{item.label}</div>
              {item.percentage && (
                <div className={`text-xs ${item.color} mt-1`}>
                  占日需{item.percentage}%
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-3">
          {nutritionItems.slice(3).map((item, index) => (
            <div key={index} className={`${item.bgColor} rounded-xl p-3 text-center`}>
              <item.icon className={`w-5 h-5 ${item.color} mx-auto mb-1`} />
              <div className="text-lg font-bold text-gray-800">
                {item.value}
                <span className="text-xs font-normal text-gray-500 ml-0.5">
                  {item.unit}
                </span>
              </div>
              <div className="text-xs text-gray-500">{item.label}</div>
            </div>
          ))}
        </div>

        {/* Health Tips */}
        {health_tips.length > 0 && (
          <div className="mt-4 space-y-2">
            <h4 className="text-sm font-medium text-gray-700">💡 健康提示</h4>
            {health_tips.map((tip, index) => (
              <p key={index} className="text-xs text-gray-600 bg-gray-50 p-2 rounded-lg">
                {tip}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};