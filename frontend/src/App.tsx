import { useState, useRef, useEffect } from 'react';
import { ChatInterface } from './components/Chat/ChatInterface';
import { RecipeCard } from './components/RecipeCard/RecipeCard';
import { NutritionPanel } from './components/NutritionInfo/NutritionPanel';
import { ChefHat, MessageCircle, BookOpen, Heart } from 'lucide-react';
import { chatApi } from './services/api';
import { ChatResponse } from './types';
import './App.css';

function App() {
  const [conversationId, setConversationId] = useState<string>('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState<ChatResponse | null>(null);

  useEffect(() => {
    // 初始化对话
    chatApi.createConversation().then((data) => {
      setConversationId(data.conversation_id);
      setMessages([{ role: 'assistant', content: data.message }]);
    });
  }, []);

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || !conversationId) return;

    // 添加用户消息
    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(message, conversationId);
      
      // 添加助手回复
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.message },
      ]);
      
      setCurrentResponse(response);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '抱歉，发生了错误，请稍后再试。' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-orange-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-orange-400 to-red-500 p-2 rounded-xl">
                <ChefHat className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  美食推荐与食谱智能助手
                </h1>
                <p className="text-sm text-gray-500">
                  AI驱动的个性化烹饪助手
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1 text-orange-600">
                <Heart className="w-5 h-5" />
                <span className="text-sm font-medium">50道精选菜谱</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Chat Interface */}
          <div className="lg:col-span-2">
            <ChatInterface
              messages={messages}
              isLoading={isLoading}
              onSendMessage={handleSendMessage}
            />
          </div>

          {/* Right: Recipe & Nutrition Info */}
          <div className="space-y-6">
            {/* Suggested Recipes */}
            {currentResponse?.suggested_recipes && currentResponse.suggested_recipes.length > 0 && (
              <div className="bg-white rounded-2xl shadow-lg border border-orange-100 overflow-hidden">
                <div className="bg-gradient-to-r from-orange-500 to-red-500 px-4 py-3">
                  <div className="flex items-center space-x-2 text-white">
                    <BookOpen className="w-5 h-5" />
                    <h3 className="font-semibold">推荐菜谱</h3>
                  </div>
                </div>
                <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
                  {currentResponse.suggested_recipes.map((match, index) => (
                    <RecipeCard key={index} match={match} />
                  ))}
                </div>
              </div>
            )}

            {/* Nutrition Info */}
            {currentResponse?.nutrition_info && (
              <NutritionPanel nutrition={currentResponse.nutrition_info} />
            )}

            {/* Quick Tips */}
            <div className="bg-white rounded-2xl shadow-lg border border-orange-100 p-4">
              <div className="flex items-center space-x-2 text-orange-600 mb-3">
                <MessageCircle className="w-5 h-5" />
                <h3 className="font-semibold">使用提示</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start space-x-2">
                  <span className="text-orange-500 mt-1">•</span>
                  <span>输入"我有番茄、鸡蛋，能做什么？"获取菜谱推荐</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-orange-500 mt-1">•</span>
                  <span>说"我是素食主义者"系统会记住您的饮食偏好</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-orange-500 mt-1">•</span>
                  <span>询问"这道菜的热量是多少？"获取营养信息</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-orange-500 mt-1">•</span>
                  <span>"没有花生可以用什么代替？"获得食材替代建议</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;