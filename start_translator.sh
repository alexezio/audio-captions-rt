#!/bin/bash
# 会议翻译系统启动脚本

echo "🚀 启动会议翻译系统..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查whisper-cli
if ! command -v whisper-cli &> /dev/null; then
    echo "❌ whisper-cli未安装"
    echo "请运行: brew install whisper-cpp (macOS)"
    exit 1
fi

# 启动翻译系统
echo "选择翻译模式:"
echo "1. 英文 → 中文 (默认)"
echo "2. 中文 → 英文"
echo "3. 自动检测 → 中文"
echo "4. 自定义"

read -p "请选择 (1-4): " choice

case $choice in
    1|"")
        python simple_transcirber.py --source en --target zh
        ;;
    2)
        python simple_transcirber.py --source zh --target en
        ;;
    3)
        python simple_transcirber.py --source auto --target zh
        ;;
    4)
        echo "可用语言: en, zh, ru, fr, de, ja, ko, es, it, pt, ar"
        read -p "源语言 (auto为自动检测): " src_lang
        read -p "目标语言: " tgt_lang
        python simple_transcirber.py --source "$src_lang" --target "$tgt_lang"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

# 退出虚拟环境
deactivate
