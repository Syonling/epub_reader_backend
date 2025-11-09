# epub_reader_backend

一个支持多种 LLM API 的文本分析后端服务，为 Flutter EPUB 阅读器提供 AI 驱动的文本分析功能。

## 🌟 特性

- ✅ 支持多种 AI 提供商（OpenAI, Claude, Gemini, Ollama）
- ✅ Echo 测试模式（无需 API 密钥即可测试）
- ✅ 灵活的配置管理
- ✅ RESTful API 设计
- ✅ CORS 支持
- ✅ 完整的错误处理

## 📦 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 选择 AI 提供商
AI_PROVIDER=echo  # 可选: openai, claude, gemini, ollama, echo

# 如果使用 OpenAI
OPENAI_API_KEY=your-api-key-here

# 如果使用 Claude
ANTHROPIC_API_KEY=your-api-key-here

# 如果使用 Gemini
GEMINI_API_KEY=your-api-key-here
```

### 3. 启动服务

```bash
python backend.py
```

服务将在 `http://localhost:5001` 启动。

## 🚀 快速开始

### Echo 测试模式（无需 API 密钥）

默认配置使用 `echo` 模式，可以直接测试而无需配置真实的 API 密钥：

```bash
python backend.py
```

### 使用真实 AI API

1. 在 `.env` 文件中配置 API 密钥
2. 修改 `AI_PROVIDER` 为相应的提供商
3. 重启服务

## 📡 API 接口

### 1. 健康检查

```bash
GET /api/health
```

响应：
```json
{
  "status": "ok",
  "message": "✅ 后端运行正常",
  "config": {
    "ai_provider": "echo",
    "model": "echo-v1",
    "max_tokens": 1024,
    "temperature": 0.7
  },
  "available_providers": ["openai", "claude", "gemini", "ollama", "echo"],
  "timestamp": "2025-11-09T19:00:00"
}
```

### 2. 文本分析

```bash
POST /api/analyze
Content-Type: application/json

{
  "text": "Hello, how are you?"
}
```

响应：
```json
{
  "original_text": "Hello, how are you?",
  "analysis": {
    "provider": "Echo (测试模式)",
    "model": "echo-v1",
    "result": {
      "language": "英文",
      "translation": "这是英文文本。(模拟翻译)",
      "grammar": "文本包含 19 个字符",
      "vocabulary": ["词汇1", "词汇2", "词汇3"],
      "explanation": "这是一个模拟的分析结果。",
      "note": "⚠️ 当前使用 Echo 测试模式"
    },
    "status": "success",
    "stats": {
      "character_count": 19,
      "word_count": 4
    }
  },
  "timestamp": "2025-11-09T19:00:00"
}
```

### 3. 获取配置

```bash
GET /api/config
```

### 4. 切换 AI 提供商（可选）

```bash
POST /api/switch-provider
Content-Type: application/json

{
  "provider": "openai"
}
```

## 🤖 支持的 AI 提供商

### 1. OpenAI (GPT-4)

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

获取 API 密钥：https://platform.openai.com/api-keys

### 2. Anthropic Claude

```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

获取 API 密钥：https://console.anthropic.com/

### 3. Google Gemini

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-pro
```

获取 API 密钥：https://makersuite.google.com/app/apikey

### 4. Ollama (本地模型)

首先安装并启动 Ollama：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama2

# 启动服务（默认端口 11434）
ollama serve
```

然后配置：

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 5. Echo (测试模式)

```env
AI_PROVIDER=echo
```

无需任何 API 密钥，返回模拟的分析结果。

## 🔧 配置说明

### config.py

核心配置文件，管理所有环境变量和设置。

### ai_service.py

AI 服务模块，提供统一的文本分析接口。包含：
- `BaseAnalyzer`: 分析器基类
- `OpenAIAnalyzer`: OpenAI 分析器
- `ClaudeAnalyzer`: Claude 分析器
- `GeminiAnalyzer`: Gemini 分析器
- `OllamaAnalyzer`: Ollama 分析器
- `EchoAnalyzer`: 测试分析器
- `AnalyzerFactory`: 分析器工厂

### backend.py

Flask 应用主文件，提供 RESTful API。

## 🧪 测试

### 测试健康检查

```bash
curl http://localhost:5001/api/health
```

### 测试文本分析

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "今天天气真好。"}'
```

### Python 测试脚本

```python
import requests

# 测试分析
response = requests.post(
    'http://localhost:5001/api/analyze',
    json={'text': 'Hello, how are you?'}
)

print(response.json())
```

## 📝 前端集成

Flutter 前端已经配置好相应的接口，只需确保：

1. `env.dart` 中的 `backendUrl` 指向后端地址
2. 后端服务正在运行
3. 网络连接正常

前端代码示例（已提供）：

```dart
// services/api_service.dart
final response = await http.post(
  url,
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'text': selectedText}),
);
```

## 🐛 故障排除

### 问题：无法连接到后端

- 检查后端服务是否在运行
- 检查 Flutter 的 `env.dart` 中的 URL 配置
- 如果使用模拟器，确保使用正确的 IP 地址：
  - Android: `http://10.0.2.2:5001`
  - iOS: `http://localhost:5001`
  - 真机: `http://你的电脑IP:5001`

### 问题：AI API 调用失败

- 检查 `.env` 中的 API 密钥是否正确
- 检查网络连接
- 查看后端控制台的错误信息
- 先使用 `echo` 模式测试基本功能

### 问题：返回格式不正确

- 确保前端的 `AnalysisResult` 模型与后端返回的 JSON 格式匹配
- 查看后端控制台的输出日志

## 📚 扩展开发

### 添加新的 AI 提供商

1. 在 `ai_service.py` 中创建新的分析器类：

```python
class NewAIAnalyzer(BaseAnalyzer):
    async def analyze(self, text: str) -> Dict:
        # 实现分析逻辑
        pass
```

2. 在 `AnalyzerFactory` 中注册：

```python
_analyzers = {
    'newai': NewAIAnalyzer,
    # ...
}
```

3. 在 `config.py` 中添加配置。

### 自定义提示词

修改 `ai_service.py` 中的 `_build_prompt` 方法来自定义 AI 提示词。

## 📄 许可证

本项目采用 CC BY-NC 4.0 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，欢迎联系。

---

**Happy Coding! 🎉**