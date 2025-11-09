"""
应用程序主包
"""
from flask import Flask
from flask_cors import CORS

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    CORS(app)
    
    # 注册蓝图
    from app.routes import health, analysis
    app.register_blueprint(health.bp)
    app.register_blueprint(analysis.bp)
    
    return app