#!/bin/bash

# EPUB Reader 后端服务启动脚本

echo "================================"
echo "🚀 启动 EPUB Reader 后端服务"
echo "================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查依赖是否安装
if [ ! -d "venv" ]; then
    echo "📦 首次运行，创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
    echo ""
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 检查并安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ 依赖安装完成"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件，从模板复制..."
    cp .env.example .env
    echo "✅ .env 文件已创建"
    echo "💡 提示: 请编辑 .env 文件配置您的 API 密钥"
    echo ""
fi

# 启动服务
echo "🚀 启动后端服务..."
echo ""
python3 backend.py