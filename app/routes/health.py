"""
健康检查和配置路由
"""
from flask import Blueprint, jsonify
from datetime import datetime
from config import Config
from app.services.ai_service import AnalyzerFactory

bp = Blueprint('health', __name__)


@bp.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    config_info = Config.get_info()
    
    return jsonify({
        'status': 'ok',
        'message': '✅ 后端运行正常',
        'config': config_info,
        'available_providers': AnalyzerFactory.get_available_providers(),
        'timestamp': datetime.now().isoformat()
    }), 200


@bp.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置信息（不包含敏感信息）"""
    return jsonify({
        'config': Config.get_info(),
        'available_providers': AnalyzerFactory.get_available_providers(),
        'timestamp': datetime.now().isoformat()
    }), 200