"""
文本分析路由
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.text_analyzer import get_text_analyzer
from app.services.ai_service import AnalyzerFactory
from config import Config

bp = Blueprint('analysis', __name__)


@bp.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    文本分析接口（智能判断使用单词解析或AI分析）
    
    请求体:
    {
        "text": "要分析的文本",
        "force_type": "word" | "sentence" (可选，强制使用某种分析类型)
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        force_type = data.get('force_type')  # 可选：'word' 或 'sentence'
        
        if not text:
            return jsonify({
                'error': '文本为空',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # 打印接收信息
        print(f"\n{'='*60}")
        print(f"📥 收到分析请求")
        print(f"📝 文本: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"📊 长度: {len(text)} 字符")
        if force_type:
            print(f"🎯 强制类型: {force_type}")
        print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 分析文本
        analyzer = get_text_analyzer()
        result = analyzer.analyze(text, force_type=force_type)
        
        # 检查分析是否成功
        if result.get('status') == 'error':
            print(f"❌ 分析失败: {result.get('error')}")
            return jsonify({
                'error': f"分析失败: {result.get('error')}",
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # 构建响应（符合前端 AnalysisResult 模型）
        response = {
            'original_text': text,
            'analysis': {
                'type': result.get('analysis_type'),  # 'word' 或 'sentence'
                'method': result.get('method'),       # 'word_parser' 或 'ai_analysis'
                # 'language': result.get('language'),
                'result': result.get('result'),
                'status': result.get('status'),
                # 'stats': {
                #     'character_count': result.get('character_count'),
                #     'word_count': len(text.split()) if result.get('language') == '英文' else len(text),
                # }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # 如果使用了AI，添加AI信息
        # if result.get('method') == 'ai_analysis':
        #     response['analysis']['provider'] = result.get('provider')
        #     response['analysis']['model'] = result.get('model')
        
        print(f"✅ 分析完成")
        print(f"📤 分析类型: {result.get('analysis_type')} | 方法: {result.get('method')}")
        print(f"{'='*60}\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ 服务器错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': f'服务器错误: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@bp.route('/api/analyze/word', methods=['POST'])
def analyze_word():
    """
    单词解析接口（强制使用单词解析器）
    
    请求体:
    {
        "text": "単語"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'error': '文本为空',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        print(f"\n📚 收到单词解析请求: {text}")
        
        # 强制使用单词解析
        analyzer = get_text_analyzer()
        result = analyzer.analyze(text, force_type='word')
        
        response = {
            'original_text': text,
            'analysis': {
                'type': 'word',
                'method': 'word_parser',
                'language': result.get('language'),
                'result': result.get('result'),
                'status': result.get('status')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 单词解析完成\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return jsonify({
            'error': f'错误: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@bp.route('/api/analyze/sentence', methods=['POST'])
def analyze_sentence():
    """
    句子分析接口（强制使用AI分析）
    
    请求体:
    {
        "text": "今天天气真好。"
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'error': '文本为空',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        print(f"\n🤖 收到句子分析请求: {text[:50]}...")
        
        # 强制使用AI分析
        analyzer = get_text_analyzer()
        result = analyzer.analyze(text, force_type='sentence')
        
        response = {
            'original_text': text,
            'analysis': {
                'type': 'sentence',
                'method': 'ai_analysis',
                'provider': result.get('provider'),
                'model': result.get('model'),
                'language': result.get('language'),
                'result': result.get('result'),
                'status': result.get('status')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ 句子分析完成\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return jsonify({
            'error': f'错误: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@bp.route('/api/switch-provider', methods=['POST'])
def switch_provider():
    """
    切换AI提供商
    
    请求体:
    {
        "provider": "openai" | "claude" | "gemini" | "ollama" | "echo"
    }
    """
    try:
        data = request.get_json()
        new_provider = data.get('provider', '').lower()
        
        available = AnalyzerFactory.get_available_providers()
        if new_provider not in available:
            return jsonify({
                'error': f'不支持的提供商: {new_provider}',
                'available_providers': available
            }), 400
        
        Config.AI_PROVIDER = new_provider
        
        # 验证新配置
        if new_provider != 'echo':
            config_valid, error_msg = Config.validate()
            if not config_valid:
                return jsonify({
                    'error': f'配置错误: {error_msg}',
                    'note': '请检查相应的API密钥是否已设置'
                }), 400
        
        print(f"🔄 已切换到: {new_provider}")
        
        return jsonify({
            'message': f'已切换到 {new_provider}',
            'config': Config.get_info()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500