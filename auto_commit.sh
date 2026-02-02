#!/bin/bash

# 股票预测系统 - 自动提交脚本
# 每日凌晨4点自动执行，提交可运行版本到GitHub

set -e  # 遇到错误立即退出

# 配置
REPO_DIR="/home/parallels/.openclaw/workspace/Stock-testing-project"
COMMIT_MSG="📊 股票预测系统 - 自动提交 $(date +'%Y-%m-%d %H:%M:%S')"
BRANCH="main"

echo "========================================"
echo "📈 股票预测系统 - 自动提交"
echo "========================================"
echo ""

# 进入项目目录
cd "$REPO_DIR"

echo "📅 时间: $(date)"
echo "📂 目录: $REPO_DIR"
echo ""

# 1. 测试代码是否可运行
echo "🧪 测试代码可运行性..."
python3 main.py "600519" > /dev/null 2>&1 || {
    echo "❌ 代码测试失败，跳过本次提交"
    exit 1
}
echo "✅ 代码测试通过"
echo ""

# 2. 检查是否有改动
echo "🔍 检查代码改动..."
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️ 没有代码改动，跳过提交"
    exit 0
fi
echo "✅ 检测到代码改动"
echo ""

# 3. 添加所有文件
echo "📦 添加文件到Git..."
git add .
echo "✅ 文件已添加"
echo ""

# 4. 提交
echo "💾 提交代码..."
git commit -m "$COMMIT_MSG"
echo "✅ 代码已提交"
echo ""

# 5. 推送到GitHub
echo "🚀 推送到GitHub..."
git push origin "$BRANCH"
echo "✅ 已推送到GitHub"
echo ""

echo "========================================"
echo "✅ 自动提交完成！"
echo "========================================"
echo ""
