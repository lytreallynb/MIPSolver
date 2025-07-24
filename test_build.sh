#!/bin/bash

echo "🧪 测试单包架构构建"
echo "=================="

# 清理之前的构建
echo "🧹 清理构建文件..."
rm -rf build/ dist/ *.egg-info/

# 检查项目结构
echo ""
echo "📁 验证项目结构..."
if [ ! -d "mipsolver" ]; then
    echo "❌ 错误: mipsolver包目录不存在"
    exit 1
fi

if [ ! -f "mipsolver/__init__.py" ]; then
    echo "❌ 错误: mipsolver/__init__.py不存在"  
    exit 1
fi

if [ ! -f "bindings/python_bindings.cpp" ]; then
    echo "❌ 错误: python_bindings.cpp不存在"
    exit 1
fi

echo "✅ 项目结构验证通过"

# 检查Python环境
echo ""
echo "🐍 检查Python环境..."
python --version || { echo "❌ Python未安装"; exit 1; }

# 安装构建依赖
echo ""
echo "📦 安装构建依赖..."
pip install --upgrade pip setuptools wheel pybind11 cmake

# 构建源分发
echo ""
echo "📋 构建源分发..."
python setup.py sdist

if [ $? -eq 0 ]; then
    echo "✅ 源分发构建成功"
    ls -la dist/*.tar.gz
else
    echo "❌ 源分发构建失败"
    exit 1
fi

# 尝试构建wheel（可能需要C++编译环境）
echo ""
echo "🔨 尝试构建wheel..."
python setup.py bdist_wheel

if [ $? -eq 0 ]; then
    echo "✅ Wheel构建成功"
    ls -la dist/*.whl
else
    echo "⚠️  Wheel构建失败（可能需要C++编译环境）"
    echo "   源分发构建成功，可以在有编译环境的机器上安装"
fi

echo ""
echo "🎉 单包架构测试完成！"
echo ""
echo "📦 生成的分发包:"
ls -la dist/ 2>/dev/null || echo "  (无分发包生成)"

echo ""
echo "💡 使用方法:"
echo "   pip install dist/mipsolver-*.tar.gz  # 从源码安装"
echo "   pip install dist/mipsolver-*.whl     # 从wheel安装（如果存在）"
