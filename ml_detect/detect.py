import numpy as np
from scipy.sparse import hstack
from joblib import load


class MlDetect(object):
    # 类变量用于存储加载的模型和向量器
    _model = None
    _vectorizer = None
    
    @classmethod
    def _load_models(cls):
        """懒加载模型，只在第一次使用时加载"""
        if cls._model is None or cls._vectorizer is None:
            cls._model = load('ml_detect/rf.joblib')
            cls._vectorizer = load('ml_detect/rf_vectorizer.joblib')
    
    def __init__(self, http_data):
        # 确保模型已加载
        self._load_models()
        
        if http_data.body:
            self.body = http_data.body[0]
        else:
            self.body = ""
        self.path = http_data.uri


    def run(self):
        # 保持稀疏矩阵格式
        vector_content = self._vectorizer.transform([self.body])
        vector_path = self._vectorizer.transform([self.path])
        
        # 直接使用稀疏矩阵
        X = hstack([vector_content, vector_path])
        
        # 预测
        prediction = self._model.predict(X)
        
        return {
            "status": bool(prediction[0]),
            "type": "ml_detect" if prediction[0] else None
        }

