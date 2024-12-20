import pandas as pd
import numpy as np
from joblib import load


class MlDetect(object):
    def __init__(self, http_data):

        if http_data.body:
            self.body = http_data.body[0]
        else:
            self.body = ""
        self.path = []
        self.path.append(http_data.uri)


    def run(self):
        model = load('ml_detect/rf.joblib')
        vectorizer = load('ml_detect/rf_vectorizer.joblib')

        vector_content = vectorizer.transform([self.body]).toarray()
        vector_path = vectorizer.transform(self.path).toarray()

        # 转换为DataFrame以便于预测
        vector_df = pd.DataFrame(
            np.hstack([vector_content, vector_path]),
            columns=[f"vector_content_{i}" for i in range(vector_content.shape[1])] + \
                    [f"vector_path_{i}" for i in range(vector_path.shape[1])]
        )

        # 预测是否为攻击
        prediction = model.predict(vector_df)

        if prediction == 1:
            return {"status": True, "type": "ml_detect"}
        else:
            return {"status": False}

