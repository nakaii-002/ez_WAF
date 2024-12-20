import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from joblib import dump, load

# 读取数据
data = pd.read_csv('csic_database_cleaned.csv')
data = data.fillna("")

# Type,Method,User-Agent,Pragma,Cache-Control,Accept,Accept-encoding,Accept-charset,language,host,cookie,content-type,connection,lenght,content,classification,URL
# Method  URL(path)  User-Agent  cookie  content-type content
# path content

# 对请求负载进行简单的词频转换
vectorizer = CountVectorizer(max_features=10000, max_df=0.9)
vector_content = vectorizer.fit_transform(data['content']).toarray()
vector_path = vectorizer.transform(data['path']).toarray()
vector_df = pd.DataFrame(
    np.hstack([vector_content, vector_path]),
    columns = [f"vector_content_{i}" for i in range(vector_content.shape[1])] + \
          [f"vector_path_{i}" for i in range(vector_path.shape[1])]
)
dump(vectorizer, 'rf_vectorizer.joblib')

# 将特征组合在一起
# X = pd.concat([data[['Method', 'User-Agent', 'content-type']], vector_df], axis=1)
X = vector_df

# 标签
y = data['classification']

# 数据集划分：训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 初始化并训练模型
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
dump(model, "rf.joblib")

# 模型预测
y_pred = model.predict(X_test)

# 打印评估报告
print(classification_report(y_test, y_pred))
