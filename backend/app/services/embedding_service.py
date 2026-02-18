"""
Embedding 服务 - 使用 sentence-transformers 生成文本向量
支持多语言，本地运行，无需 API Key
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingService:
    """文本向量化服务"""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        初始化 Embedding 模型
        
        Args:
            model_name: 模型名称
                - paraphrase-multilingual-MiniLM-L12-v2: 多语言，推荐
                - distiluse-base-multilingual-cased-v1: 更快的多语言模型
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        将单个文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本转换为向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表的列表
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def embed_recipe(self, recipe: dict) -> str:
        """
        将菜谱转换为可向量化的文本
        
        Args:
            recipe: 菜谱字典
            
        Returns:
            拼接后的文本
        """
        # 提取关键信息
        name = recipe.get('name', '')
        name_en = recipe.get('name_en', '')
        category = recipe.get('category', '')
        tags = ' '.join(recipe.get('tags', []))
        ingredients = ' '.join([i['name'] for i in recipe.get('ingredients', [])])
        
        # 构建语义文本（包含同义词和描述）
        text = f"""
        菜名: {name} {name_en}
        类型: {category}
        标签: {tags}
        食材: {ingredients}
        """
        
        return text.strip()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1)
        """
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        # 计算余弦相似度
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        return float(dot_product / (norm1 * norm2))


# 单例模式
embedding_service = EmbeddingService()