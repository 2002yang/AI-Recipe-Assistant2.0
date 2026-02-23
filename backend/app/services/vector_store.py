"""
向量数据库服务 - 使用 ChromaDB 存储和检索菜谱向量
提供语义搜索能力
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
import os
from app.services.embedding_service import embedding_service


class RecipeVectorStore:
    """菜谱向量数据库"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        初始化向量数据库
        
        Args:
            persist_directory: 数据持久化目录
        """
        self.persist_directory = persist_directory
        
        # 初始化 ChromaDB 客户端  本地持久化模式 数据保存在 ./chroma_db
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="recipes",
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        
        print(f"Vector store initialized. Collection: recipes")
        print(f"Current document count: {self.collection.count()}")
    
    def add_recipes(self, recipes: List[Dict[str, Any]]) -> bool:
        """
        批量添加菜谱到向量库
        
        Args:
            recipes: 菜谱列表
            
        Returns:
            是否成功
        """
        if not recipes:
            return True
        
        try:
            # 准备数据
            ids = []
            documents = []
            metadatas = []
            
            for recipe in recipes:
                recipe_id = str(recipe['id'])
                
                # 生成向量文本
                doc_text = embedding_service.embed_recipe(recipe)
                
                # 准备元数据
                metadata = {
                    'id': recipe['id'],
                    'name': recipe['name'],
                    'category': recipe.get('category', ''),
                    'difficulty': recipe.get('difficulty', ''),
                    'time': recipe.get('time', ''),
                    'tags': json.dumps(recipe.get('tags', [])),
                    'ingredients': json.dumps([i['name'] for i in recipe.get('ingredients', [])]),
                    'calories': recipe.get('nutrition', {}).get('calories', 0)
                }
                
                ids.append(recipe_id)
                documents.append(doc_text)
                metadatas.append(metadata)
            
            # 生成向量
            print(f"Generating embeddings for {len(recipes)} recipes...")
            embeddings = embedding_service.embed_texts(documents)
            
            # 添加到数据库
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"Added {len(recipes)} recipes to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding recipes to vector store: {e}")
            return False
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        语义搜索菜谱
        
        Args:
            query: 搜索查询（自然语言）
            n_results: 返回结果数量
            filters: 过滤条件，如 {"category": "川菜"}
            
        Returns:
            匹配的菜谱列表
        """
        try:
            # 生成查询向量
            query_embedding = embedding_service.embed_text(query)
            
            # 构建 where 条件
            where_clause = None
            if filters:
                where_clause = filters
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["metadatas", "documents", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, recipe_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # 转换距离为相似度分数 (余弦距离 -> 余弦相似度)
                    similarity = 1 - distance
                    
                    formatted_results.append({
                        'id': int(metadata['id']),
                        'name': metadata['name'],
                        'category': metadata['category'],
                        'difficulty': metadata['difficulty'],
                        'time': metadata['time'],
                        'tags': json.loads(metadata['tags']),
                        'ingredients': json.loads(metadata['ingredients']),
                        'calories': metadata['calories'],
                        'similarity': round(similarity, 3),
                        'vector_text': results['documents'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def search_by_ingredients(
        self, 
        ingredients: List[str], 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        基于食材搜索（保留原有功能，但使用向量语义）
        
        Args:
            ingredients: 食材列表
            n_results: 返回数量
            
        Returns:
            匹配的菜谱列表
        """
        # 构建语义查询
        query = f"包含{ '、'.join(ingredients)}的菜"
        
        return self.search(query, n_results=n_results)
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict]:
        """
        通过 ID 获取菜谱
        
        Args:
            recipe_id: 菜谱ID
            
        Returns:
            菜谱信息
        """
        try:
            result = self.collection.get(
                ids=[str(recipe_id)],
                include=["metadatas"]
            )
            
            if result['ids']:
                metadata = result['metadatas'][0]
                return {
                    'id': int(metadata['id']),
                    'name': metadata['name'],
                    'category': metadata['category'],
                    'difficulty': metadata['difficulty'],
                    'time': metadata['time'],
                    'tags': json.loads(metadata['tags']),
                    'ingredients': json.loads(metadata['ingredients']),
                    'calories': metadata['calories']
                }
            return None
            
        except Exception as e:
            print(f"Error getting recipe: {e}")
            return None
    
    def delete_all(self):
        """清空所有数据（谨慎使用）"""
        self.client.delete_collection("recipes")
        self.collection = self.client.create_collection(
            name="recipes",
            metadata={"hnsw:space": "cosine"}
        )
        print("Vector store cleared")


# 单例模式
vector_store = RecipeVectorStore()