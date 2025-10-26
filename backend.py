from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """接收前端发送的文本"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': '文本为空'}), 400
        
        # 打印到控制台
        print(f"\n{'='*50}")
        print(f"📥 收到文本: {text}")
        print(f"📊 文本长度: {len(text)} 字符")
        print(f"{'='*50}\n")
        
        # 返回响应（后续这里可以调用你的AI API）
        response = {
            'status': 'success',
            'message': f'✅ 收到！文本长度: {len(text)} 字符',
            'received_text': text,
            'analysis': {
                'info': 'AI分析功能开发中...',
                'word_count': len(text.split()),
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok', 
        'message': '✅ 后端运行正常'
    }), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 后端服务启动成功！")
    print("📡 监听地址: http://0.0.0.0:5001")
    print("💡 测试地址: http://localhost:5001/api/health")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=True)