"""
初始化向量数据库 - 将菜谱数据导入 ChromaDB
运行一次即可
"""
import json
import os
from app.services.vector_store import vector_store


def init_vector_database():
    """初始化向量数据库"""
    print("=" * 50)
    print("初始化菜谱向量数据库")
    print("=" * 50)
    
    # 加载菜谱数据
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'recipes.json')
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        recipes = data['recipes']
    
    print(f"\n加载了 {len(recipes)} 道菜谱")
    
    # 清空现有数据（可选）
    # vector_store.delete_all()
    
    # 检查是否已有数据
    current_count = vector_store.collection.count()
    if current_count > 0:
        print(f"\n数据库中已有 {current_count} 条记录")
        response = input("是否重新导入？(y/n): ").strip().lower()
        if response == 'y':
            vector_store.delete_all()
        else:
            print("跳过导入")
            return
    
    # 导入数据
    print("\n正在生成向量并导入数据库...")
    success = vector_store.add_recipes(recipes)
    
    if success:
        print(f"\n✅ 成功导入 {len(recipes)} 道菜谱到向量数据库")
        print(f"数据库位置: {vector_store.persist_directory}")
    else:
        print("\n❌ 导入失败")


if __name__ == "__main__":
    init_vector_database()