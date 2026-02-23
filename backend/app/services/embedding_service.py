"""
Embedding 服务 - 使用简单的本地向量方法
"""
import os
from typing import List
import hashlib
import numpy as np


class EmbeddingService:
    """文本向量化服务"""
    
    def __init__(self):
        print("Embedding service initialized (using simple hash method)")
    
    def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量 (简单 hash 方法)"""
        return self._simple_embedding(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        return [self.embed_text(text) for text in texts]
    
    def _simple_embedding(self, text: str) -> List[float]:
        """简单的备用嵌入方法 - 基于 hash"""
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # 生成 384 维向量
        vector = []
        for i in range(384):
            byte_val = hash_bytes[i % len(hash_bytes)]
            float_val = (byte_val / 128.0) - 1.0
            # 添加一些基于位置的变换
            float_val += np.sin(i * 0.1) * 0.1
            vector.append(float_val)
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def embed_recipe(self, recipe: dict) -> str:
        """将菜谱转换为可向量化的文本"""
        name = recipe.get('name', '')
        name_en = recipe.get('name_en', '')
        category = recipe.get('category', '')
        tags = ' '.join(recipe.get('tags', []))
        ingredients = ' '.join([i['name'] for i in recipe.get('ingredients', [])])
        
        text = f"""
        菜名: {name} {name_en}
        类型: {category}
        标签: {tags}
        食材: {ingredients}
        """
        
        return text.strip()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        dot_product = np.dot(emb1, emb2)
        return float(dot_product)


embedding_service = EmbeddingService()
