import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from scipy.sparse import hstack
from joblib import dump, load

# sklearn==1.6.1 joblib==1.4.2

# 读取数据
data = pd.read_csv('csic_database_cleaned.csv')
data = data.fillna("")

# Type,Method,User-Agent,Pragma,Cache-Control,Accept,Accept-encoding,Accept-charset,language,host,cookie,content-type,connection,lenght,content,classification,URL
# Method  URL(path)  User-Agent  cookie  content-type content
# path content

# 使用CountVectorizer并优化参数
vectorizer = CountVectorizer(
    max_features=1000,    # 限制特征数
    max_df=0.9,          # 去除在90%以上文档中出现的词
    min_df=5,            # 去除出现次数过少的词
    binary=True          # 使用二进制特征而不是计数，可以减少内存使用
)

# 保持稀疏矩阵格式
vector_content = vectorizer.fit_transform(data['content'])
vector_path = vectorizer.transform(data['path'])

# 使用scipy的hstack直接合并稀疏矩阵
X = hstack([vector_content, vector_path])

# 标签
y = data['classification']

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 使用更轻量级的随机森林配置
model = RandomForestClassifier(
    n_estimators=50,      # 减少树的数量
    max_depth=30,         # 限制树的深度
    min_samples_split=5,  # 增加分裂所需的最小样本数
    n_jobs=-1,           # 使用所有CPU核心
    random_state=42
)

model.fit(X_train, y_train)
dump(model, "rf.joblib")
dump(vectorizer, 'rf_vectorizer.joblib')

# 模型预测
y_pred = model.predict(X_test)

# 打印评估报告
print(classification_report(y_test, y_pred))
