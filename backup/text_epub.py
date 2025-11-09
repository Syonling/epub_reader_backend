"""
后端服务测试脚本
用于测试各个API接口的功能
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:5001"
TIMEOUT = 10

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def print_response(response):
    """格式化打印响应"""
    print(f"状态码: {response.status_code}")
    print(f"响应内容:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_health():
    """测试健康检查接口"""
    print_section("测试 1: 健康检查 (/api/health)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_config():
    """测试配置接口"""
    print_section("测试 2: 获取配置 (/api/config)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/config", timeout=TIMEOUT)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_analyze(text, test_name):
    """测试文本分析接口"""
    print_section(f"测试 3.{test_name}: 文本分析")
    print(f"📝 测试文本: {text}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_empty_text():
    """测试空文本"""
    print_section("测试 4: 空文本处理")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={"text": ""},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        print_response(response)
        return response.status_code == 400  # 应该返回错误
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_invalid_endpoint():
    """测试无效接口"""
    print_section("测试 5: 无效接口 (404)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/invalid", timeout=TIMEOUT)
        print_response(response)
        return response.status_code == 404
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 EPUB Reader 后端服务测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 目标地址: {BASE_URL}")
    print("="*60)
    
    # 测试文本样本
    test_texts = [
        ("1", "Hello, how are you?"),
        ("2", "今天天气真好，我们去公园散步吧。"),
        ("3", "こんにちは、元気ですか？今日はいい天気ですね。"),
    ]
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health()))
    results.append(("配置获取", test_config()))
    
    for idx, text in test_texts:
        results.append((f"文本分析 {idx}", test_analyze(text, idx)))
    
    results.append(("空文本处理", test_empty_text()))
    results.append(("404处理", test_invalid_endpoint()))
    
    # 打印总结
    print_section("测试总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总测试数: {total}")
    print(f"通过: {passed} ✅")
    print(f"失败: {total - passed} ❌")
    print(f"成功率: {passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查日志")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()