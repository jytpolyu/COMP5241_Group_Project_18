from flask import Flask, jsonify
from database import get_commit_data

app = Flask(__name__)

# 一个简单的 API 端点来返回提交记录
@app.route('/commits', methods=['GET'])
def commits():
    data = get_commit_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
