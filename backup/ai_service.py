"""
AI 文本分析服务
支持多种 LLM API：OpenAI, Claude, Gemini, Ollama
"""
import json
import asyncio
from typing import Dict, Optional
from config import Config

# ================================
# 基础分析器类
# ================================
class BaseAnalyzer:
    """LLM 分析器基类"""
    
    def __init__(self):
        self.config = Config
    
    async def analyze(self, text: str) -> Dict:
        """分析文本（需要子类实现）"""
        raise NotImplementedError
    
    def _build_prompt(self, text: str) -> str:
        """构建分析提示词"""
        return f"""请分析以下文本，提供详细的语言学习辅助信息：

文本: {text}

请提供以下分析：
1. 语言类型（中文/日文/英文）
2. 翻译（如果是外语，翻译成中文；如果是中文，翻译成英文）
3. 语法结构分析
4. 重点词汇及解释
5. 文化背景或使用场景说明

请以JSON格式返回结果。"""


# ================================
# OpenAI 分析器
# ================================
class OpenAIAnalyzer(BaseAnalyzer):
    """OpenAI GPT 分析器"""
    
    def __init__(self):
        super().__init__()
        from openai import OpenAI
        
        # 支持自定义 base_url（用于代理或兼容接口）
        client_kwargs = {'api_key': self.config.OPENAI_API_KEY}
        if self.config.OPENAI_BASE_URL:
            client_kwargs['base_url'] = self.config.OPENAI_BASE_URL
        
        self.client = OpenAI(**client_kwargs)
    
    async def analyze(self, text: str) -> Dict:
        """使用 OpenAI API 分析文本"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的语言学习助手，擅长分析中文、日文和英文文本。"
                    },
                    {
                        "role": "user",
                        "content": self._build_prompt(text)
                    }
                ],
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE,
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析为JSON，如果失败则返回原始文本
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {'raw_response': content}
            
            return {
                'provider': 'OpenAI',
                'model': self.config.OPENAI_MODEL,
                'analysis': analysis_data,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'provider': 'OpenAI',
                'error': str(e),
                'status': 'error'
            }


# ================================
# Anthropic Claude 分析器
# ================================
class ClaudeAnalyzer(BaseAnalyzer):
    """Anthropic Claude 分析器"""
    
    def __init__(self):
        super().__init__()
        import anthropic
        self.client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
    
    async def analyze(self, text: str) -> Dict:
        """使用 Claude API 分析文本"""
        try:
            message = self.client.messages.create(
                model=self.config.ANTHROPIC_MODEL,
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE,
                system="你是一个专业的语言学习助手，擅长分析中文、日文和英文文本。",
                messages=[
                    {
                        "role": "user",
                        "content": self._build_prompt(text)
                    }
                ]
            )
            
            content = message.content[0].text
            
            # 尝试解析为JSON
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {'raw_response': content}
            
            return {
                'provider': 'Claude',
                'model': self.config.ANTHROPIC_MODEL,
                'analysis': analysis_data,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'provider': 'Claude',
                'error': str(e),
                'status': 'error'
            }


# ================================
# Google Gemini 分析器
# ================================
class GeminiAnalyzer(BaseAnalyzer):
    """Google Gemini 分析器"""
    
    def __init__(self):
        super().__init__()
        import google.generativeai as genai
        genai.configure(api_key=self.config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
    
    async def analyze(self, text: str) -> Dict:
        """使用 Gemini API 分析文本"""
        try:
            response = self.model.generate_content(
                self._build_prompt(text),
                generation_config={
                    'temperature': self.config.TEMPERATURE,
                    'max_output_tokens': self.config.MAX_TOKENS,
                }
            )
            
            content = response.text
            
            # 尝试解析为JSON
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {'raw_response': content}
            
            return {
                'provider': 'Gemini',
                'model': self.config.GEMINI_MODEL,
                'analysis': analysis_data,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'provider': 'Gemini',
                'error': str(e),
                'status': 'error'
            }


# ================================
# Ollama 本地模型分析器
# ================================
class OllamaAnalyzer(BaseAnalyzer):
    """Ollama 本地模型分析器"""
    
    def __init__(self):
        super().__init__()
        import requests
        self.base_url = self.config.OLLAMA_BASE_URL
        self.requests = requests
    
    async def analyze(self, text: str) -> Dict:
        """使用 Ollama 本地模型分析文本"""
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.config.OLLAMA_MODEL,
                    "prompt": self._build_prompt(text),
                    "stream": False,
                    "options": {
                        "temperature": self.config.TEMPERATURE,
                        "num_predict": self.config.MAX_TOKENS,
                    }
                },
                timeout=self.config.TIMEOUT
            )
            
            response.raise_for_status()
            content = response.json()['response']
            
            # 尝试解析为JSON
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {'raw_response': content}
            
            return {
                'provider': 'Ollama',
                'model': self.config.OLLAMA_MODEL,
                'analysis': analysis_data,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'provider': 'Ollama',
                'error': str(e),
                'status': 'error'
            }


# ================================
# Echo 测试分析器（不调用实际API）
# ================================
class EchoAnalyzer(BaseAnalyzer):
    """Echo 分析器 - 用于测试，不调用实际API"""
    
    async def analyze(self, text: str) -> Dict:
        """返回模拟的分析结果"""
        
        # 简单的语言检测
        chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        japanese_count = sum(1 for char in text if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff')
        
        if chinese_count > len(text) * 0.3:
            language = '中文'
            translation = 'This is a Chinese text. (模拟翻译)'
        elif japanese_count > len(text) * 0.3:
            language = '日文'
            translation = '这是日语文本。(模拟翻译)'
        else:
            language = '英文'
            translation = '这是英文文本。(模拟翻译)'
        
        return {
            'provider': 'Echo (测试模式)',
            'model': 'echo-v1',
            'analysis': {
                'language': language,
                'translation': translation,
                'grammar': f'文本包含 {len(text)} 个字符',
                'vocabulary': ['词汇1', '词汇2', '词汇3'],
                'explanation': '这是一个模拟的分析结果。配置真实的AI API后，将返回实际分析。',
                'note': '⚠️ 当前使用 Echo 测试模式，未调用真实AI API'
            },
            'status': 'success'
        }


# ================================
# 分析器工厂
# ================================
class AnalyzerFactory:
    """分析器工厂类"""
    
    _analyzers = {
        'openai': OpenAIAnalyzer,
        'claude': ClaudeAnalyzer,
        'gemini': GeminiAnalyzer,
        'ollama': OllamaAnalyzer,
        'echo': EchoAnalyzer,
    }
    
    @classmethod
    def create_analyzer(cls, provider: Optional[str] = None) -> BaseAnalyzer:
        """创建分析器实例"""
        provider = provider or Config.AI_PROVIDER
        
        analyzer_class = cls._analyzers.get(provider)
        if not analyzer_class:
            raise ValueError(f"不支持的 AI 提供商: {provider}")
        
        return analyzer_class()
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表"""
        return list(cls._analyzers.keys())


# ================================
# 主要的分析函数
# ================================
async def analyze_text(text: str, provider: Optional[str] = None) -> Dict:
    """
    分析文本的主函数
    
    Args:
        text: 要分析的文本
        provider: AI提供商 (可选)
    
    Returns:
        分析结果字典
    """
    try:
        analyzer = AnalyzerFactory.create_analyzer(provider)
        result = await analyzer.analyze(text)
        return result
        
    except Exception as e:
        return {
            'provider': provider or Config.AI_PROVIDER,
            'error': str(e),
            'status': 'error'
        }


# ================================
# 同步版本（用于非异步环境）
# ================================
def analyze_text_sync(text: str, provider: Optional[str] = None) -> Dict:
    """同步版本的文本分析函数"""
    return asyncio.run(analyze_text(text, provider))


# ================================
# 测试代码
# ================================
if __name__ == '__main__':
    # 测试代码
    test_texts = [
        "Hello, how are you?",
        "今天天气真好。",
        "こんにちは、元気ですか？"
    ]
    
    print("=" * 60)
    print("AI 服务测试")
    print("=" * 60)
    print(f"当前提供商: {Config.AI_PROVIDER}")
    print(f"当前模型: {Config.get_info()['model']}")
    print("=" * 60)
    
    for text in test_texts:
        print(f"\n测试文本: {text}")
        result = analyze_text_sync(text)
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("-" * 60)