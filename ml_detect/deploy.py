from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/detect', methods=['POST'])
def detect():
    # 从请求体中获取数据
    data = request.json
    url = data.get('url')
    method = data.get('method')
    user_agent = data.get('user_agent')
    payload = data.get('payload')

    # 调用检测函数
    result = detect_attack(url, method, user_agent, payload)

    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(debug=True)
