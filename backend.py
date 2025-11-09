"""
EPUB Reader 后端服务 - 主文件
"""
from app import create_app
from config import Config


def print_startup_info():
    """打印启动信息"""
    print("\n" + "="*70)
    print("🚀 EPUB Reader 后端服务启动成功！")
    print("="*70)
    print(f"📡 监听地址: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"🤖 AI提供商: {Config.AI_PROVIDER}")
    print(f"🎯 当前模型: {Config.get_info()['model']}")
    print("-"*70)
    print("📍 可用接口:")
    print(f"   - GET  /api/health              健康检查")
    print(f"   - GET  /api/config              获取配置")
    print(f"   - POST /api/analyze             智能分析（自动判断）")
    print(f"   - POST /api/analyze/word        单词解析（强制）")
    print(f"   - POST /api/analyze/sentence    句子分析（强制）")
    print(f"   - POST /api/switch-provider     切换AI提供商")
    print("-"*70)
    print(f"💡 测试命令:")
    print(f"   curl http://localhost:{Config.FLASK_PORT}/api/health")
    print("="*70)
    
    if Config.AI_PROVIDER == 'echo':
        print("⚠️  当前使用 Echo 测试模式")
        print("💡 配置真实的AI API密钥以使用实际AI分析功能")
        print("   在 .env 文件中设置相应的 API_KEY")
        print("="*70)
    
    print()


if __name__ == '__main__':
    # 创建应用
    app = create_app()
    
    # 打印启动信息
    print_startup_info()
    
    # 启动服务
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )