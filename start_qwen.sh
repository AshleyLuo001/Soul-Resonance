#!/bin/bash

echo "================================"
echo "🎮 灵魂共鸣 AI游戏"
echo "================================"
echo ""

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "请先安装Python 3.8或更高版本"
    exit 1
fi

echo "✅ Python已安装"
echo ""
 export DASHSCOPE_API_KEY='sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# 检查是否已安装依赖
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 正在安装依赖..."
    pip3 install -r requirements_qwen.txt
    echo ""
fi

# 检查dashscope
if ! python3 -c "import dashscope" &> /dev/null; then
    echo "📦 正在安装 dashscope..."
    pip3 install dashscope
    echo ""
fi

# 检查API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "⚠️  警告：未设置DASHSCOPE_API_KEY环境变量"
    echo ""
    echo "请选择一个方式设置API Key："
    echo "1. 运行: export DASHSCOPE_API_KEY='your-key'"
    echo "2. 或在app_qwen.py中直接修改DASHSCOPE_API_KEY变量"
    echo ""
    echo "💡 如何获取API Key："
    echo "   访问: https://bailian.console.aliyun.com/"
    echo ""
    read -p "按Enter继续（如果已在代码中设置）..."
fi

# 启动服务
echo ""
echo "🚀 正在启动服务器..."
echo "使用模型：通义千问 Qwen-Plus"
echo "================================"
python3 app_qwen.py
