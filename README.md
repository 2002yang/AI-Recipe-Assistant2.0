# 美食推荐与食谱智能助手

基于 AI 的智能美食推荐和食谱助手，帮助用户根据手头已有的食材、饮食偏好以及营养需求，快速找到合适的菜谱，并获得清晰的烹饪指导。

## 🌟 项目特点

- 🤖 **AI 智能推荐**：基于 DeepSeek API 理解自然语言，提供个性化菜谱推荐
- 🥘 **50道精选中餐**：涵盖家常菜、川菜、汤品等多种类型
- 💬 **多轮对话支持**：支持追问、澄清和上下文理解
- 🥗 **营养分析**：详细的热量、蛋白质、脂肪、碳水分析
- 🔄 **食材替代**：智能推荐缺失食材的替代方案
- ⚡ **快速响应**：优化的推荐算法，响应迅速
- 📱 **友好界面**：现代化的 Web 界面，响应式设计

## 🛠️ 技术架构

### 后端
- **框架**：FastAPI (Python)
- **AI 服务**：DeepSeek API
- **数据存储**：JSON 文件（50道菜谱）
- **算法**：TF-IDF + 余弦相似度食材匹配

### 前端
- **框架**：React 18 + TypeScript
- **样式**：Tailwind CSS
- **构建工具**：Vite
- **HTTP 客户端**：Axios

## 📦 项目结构

```
ai-recipe-assistant/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── routers/           # API 路由
│   │   │   ├── chat.py        # 对话API
│   │   │   ├── recipes.py     # 菜谱API
│   │   │   └── nutrition.py   # 营养API
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── nlp_service.py      # AI服务
│   │   │   ├── recipe_matcher.py   # 菜谱匹配
│   │   │   ├── nutrition_calc.py   # 营养计算
│   │   │   └── conversation.py     # 对话管理
│   │   └── data/
│   │       └── recipes.json   # 50道菜谱数据
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/          # 聊天组件
│   │   │   ├── RecipeCard/    # 食谱卡片
│   │   │   └── NutritionInfo/ # 营养信息
│   │   ├── services/api.ts    # API 服务
│   │   └── types/index.ts     # TypeScript 类型
│   ├── package.json
│   └── index.html
│
└── tests/                      # 测试文件
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- DeepSeek API Key（已内置）

### 1. 克隆项目

```bash
git clone <repository-url>
cd ai-recipe-assistant
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端服务将在 http://localhost:8000 启动
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 4. 访问应用

打开浏览器访问 http://localhost:5173 即可使用！

## 💡 使用示例

### 场景1：基于食材推荐
**用户**："我家里有番茄、鸡蛋、洋葱和大蒜，能做什么菜？"

**系统**：
- 识别食材：番茄、鸡蛋、洋葱、大蒜
- 推荐：番茄炒蛋（匹配度90%）、番茄鸡蛋汤（匹配度85%）
- 显示已有食材和还需食材

### 场景2：饮食限制
**用户**："我对海鲜过敏，推荐一些菜"

**系统**：
- 记住限制：无海鲜
- 过滤菜谱：排除蒜蓉粉丝蒸虾、白灼虾等
- 推荐：番茄炒蛋、麻婆豆腐等

### 场景3：营养咨询
**用户**："红烧肉的热量是多少？适合减肥吃吗？"

**系统**：
- 显示营养：每份450卡、蛋白质15g、脂肪38g
- 健康提示：热量较高，建议搭配蔬菜食用
- 减肥建议：不太适合，建议单次食用不超过100g

### 场景4：食材替代
**用户**："想做宫保鸡丁，但没有花生，用什么可以替代？"

**系统**：
- 替代建议：腰果（口感最接近）、杏仁（更香脆）、核桃（营养更丰富）
- 解释：这些坚果提供相似的口感和香脆度

### 场景5：多轮对话
**用户**："我想做番茄炒蛋"
**系统**："好的！番茄炒蛋是一道经典家常菜..."
**用户**："需要多长时间？"
**系统**："番茄炒蛋制作时间约10分钟，非常简单..."
**用户**："能提前准备吗？"
**系统**："可以！你可以提前切好番茄和打蛋液..."

## 📊 API 文档

### 对话相关
- `POST /api/chat/message` - 发送消息
- `POST /api/chat/new` - 创建新对话
- `GET /api/chat/history/{conversation_id}` - 获取对话历史

### 菜谱相关
- `GET /api/recipes/list` - 获取菜谱列表
- `GET /api/recipes/{recipe_id}` - 获取菜谱详情
- `POST /api/recipes/search` - 基于食材搜索
- `GET /api/recipes/{recipe_id}/substitutions/{ingredient}` - 获取替代建议

### 营养相关
- `GET /api/nutrition/recipe/{recipe_id}` - 获取菜谱营养
- `GET /api/nutrition/recipe/{recipe_id}/diet/{diet_type}` - 检查饮食适合性
- `GET /api/nutrition/daily-needs` - 计算每日营养需求

## 🧪 运行测试

```bash
cd backend

# 安装测试依赖
pip install -r requirements-test.txt

# 运行测试
pytest tests/ -v
```

## 🔍 代码审查报告

### 优点
1. ✅ **清晰的架构**：MVC分层，职责分离
2. ✅ **类型安全**：全面使用 TypeScript 和 Pydantic
3. ✅ **异步支持**：FastAPI 异步处理，性能优秀
4. ✅ **模块设计**：服务层、路由层分离，易于测试和维护
5. ✅ **错误处理**：完整的异常处理机制
6. ✅ **数据验证**：输入输出都有严格的类型验证

### 建议改进
1. 🔧 **数据库**：当前使用 JSON 文件，生产环境建议迁移到 PostgreSQL
2. 🔧 **缓存**：添加 Redis 缓存热门查询
3. 🔧 **日志**：完善日志记录，便于问题排查
4. 🔧 **限流**：API 添加速率限制防止滥用
5. 🔧 **认证**：添加用户认证系统保存个人偏好

## 📈 性能优化

- **算法优化**：菜谱匹配使用倒排索引，时间复杂度 O(n)
- **异步处理**：AI 调用和数据库操作都是异步
- **数据缓存**：菜谱数据启动时加载到内存
- **前端优化**：组件懒加载，减少首屏加载时间

## 🎯 项目亮点

1. **完整的 AI 集成**：不只是简单调用 API，而是完整的意图解析、上下文管理、个性化回复
2. **丰富的菜谱数据**：50道经典中餐，包含完整食材、步骤、营养信息
3. **智能匹配算法**：基于食材重叠度和饮食限制的智能推荐
4. **多轮对话能力**：维护对话上下文，支持复杂交互
5. **现代化前端**：React + TypeScript + Tailwind，界面美观、交互流畅

## 📄 许可证

MIT License

## 🙏 致谢

- DeepSeek 提供 AI 能力支持
- 开源社区提供的工具和库

---

**Made with ❤️ for food lovers**