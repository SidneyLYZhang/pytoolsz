from thefuzz import fuzz, process
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein

class FuzzyMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.fitted = False
    
    def _get_scorer(self, scorer):
        """获取相似度计算函数"""
        if callable(scorer):
            return scorer
            
        scorers = {
            "ratio": fuzz.ratio,
            "levenshtein": self.levenshtein_ratio,
            "partial": fuzz.partial_ratio,
            "token_sort": fuzz.token_sort_ratio,
            "token_set": fuzz.token_set_ratio,
            "partial_token_sort": fuzz.partial_token_sort_ratio,
            "partial_token_set": fuzz.partial_token_set_ratio,
            "wratio": fuzz.WRatio
        }
        return scorers.get(scorer, fuzz.WRatio)
    
    @staticmethod
    def levenshtein_ratio(s1, s2):
        """基于 Levenshtein 距离的相似度计算 (0-100)"""
        distance = Levenshtein.distance(s1, s2)
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 100
        return int(100 * (1 - distance / max_len))
    
    def match(self, target, choices, threshold=70, scorer="wratio", limit=1):
        """
        统一匹配方法：从列表中找出与目标最相似的元素
        
        参数:
            target (str): 目标字符串
            choices (list): 候选列表
            threshold (int): 相似度阈值(0-100)
            scorer (str or callable): 相似度计算方法或自定义函数
            limit (int): 返回结果数量
                - 1: 返回单个最佳匹配元素
                - >1: 返回前N个匹配结果 [(元素, 相似度), ...]
                - 0: 返回所有超过阈值的匹配结果
        
        返回:
            单个元素 或 匹配结果列表 [(元素, 相似度), ...] 或 None
        """
        scorer_func = self._get_scorer(scorer)
        
        # 当limit=1时，使用extractOne获取单个最佳匹配
        if limit == 1:
            result = process.extractOne(
                target, 
                choices, 
                scorer=scorer_func,
                score_cutoff=threshold
            )
            return result[0] if result else None
        
        # 当limit=0时，返回所有超过阈值的匹配结果
        if limit == 0:
            results = []
            for choice in choices:
                score = scorer_func(target, choice)
                if score >= threshold:
                    results.append((choice, score))
            # 按相似度降序排序
            return sorted(results, key=lambda x: x[1], reverse=True)
        
        # 当limit>1时，使用extract获取前N个匹配结果
        return process.extract(
            target, 
            choices, 
            scorer=scorer_func,
            limit=limit
        )
    
    def match_cross(self, list1, list2, threshold=70, scorer="wratio"):
        """
        从list1中找出与list2各元素最相似的匹配项
        
        参数:
            list1 (list): 候选列表
            list2 (list): 目标列表
            threshold (int): 相似度阈值(0-100)
            scorer (str or callable): 相似度计算方法或自定义函数
        
        返回:
            匹配字典 {目标元素: (匹配元素, 相似度)}
        """
        scorer_func = self._get_scorer(scorer)
        results = {}
        for target in list2:
            result = process.extractOne(
                target, 
                list1, 
                scorer=scorer_func,
                score_cutoff=threshold
            )
            if result:
                results[target] = result
        return results
    
    def filter_regex(self, choices, pattern):
        """
        使用正则表达式筛选列表
        
        参数:
            choices (list): 待筛选列表
            pattern (str): 正则表达式
            
        返回:
            匹配元素列表
        """
        regex = re.compile(pattern)
        return [item for item in choices if regex.search(item)]
    
    def _fit_vectorizer(self, corpus):
        """训练词向量模型"""
        self.vectorizer.fit(corpus)
        self.fitted = True
    
    def match_semantic(self, target, choices, threshold=0.7):
        """
        基于词义相似度匹配
        
        参数:
            target (str): 目标字符串
            choices (list): 候选列表
            threshold (float): 余弦相似度阈值(0-1)
        
        返回:
            匹配结果列表 [(元素, 相似度), ...]
        """
        if not self.fitted:
            self._fit_vectorizer(choices + [target])
        
        # 转换文本为向量
        target_vec = self.vectorizer.transform([target])
        choices_vec = self.vectorizer.transform(choices)
        
        # 计算余弦相似度
        similarities = cosine_similarity(target_vec, choices_vec)[0]
        
        # 获取匹配结果
        results = []
        for i, sim in enumerate(similarities):
            if sim >= threshold:
                results.append((choices[i], round(sim, 4)))
        
        # 按相似度排序
        return sorted(results, key=lambda x: x[1], reverse=True)