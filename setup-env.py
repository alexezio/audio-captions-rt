#!/usr/bin/env python3
"""
会议翻译系统安装脚本
自动检查和安装所需依赖
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# 全局变量，用于存储虚拟环境路径
VENV_PYTHON = None
VENV_PIP = None


def print_status(message, status="info"):
    colors = {
        "info": "\033[94m",  # 蓝色
        "success": "\033[92m",  # 绿色
        "warning": "\033[93m",  # 黄色
        "error": "\033[91m",  # 红色
        "reset": "\033[0m",  # 重置
    }

    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

    color = colors.get(status, colors["info"])
    icon = icons.get(status, "")
    reset = colors["reset"]

    print(f"{color}{icon} {message}{reset}")


def run_command(command, description="", check=True):
    """运行命令并处理错误"""
    print_status(f"执行: {description or command}")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=check
        )
        if result.stdout:
            print(f"  输出: {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        if check:
            print_status(f"命令失败: {e}", "error")
            if e.stderr:
                print(f"  错误: {e.stderr.strip()}")
        return False


def check_python_version():
    """检查Python版本"""
    print_status("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_status(
            f"需要Python 3.11+，当前版本: {version.major}.{version.minor}", "error"
        )
        return False
    print_status(
        f"Python版本: {version.major}.{version.minor}.{version.micro}", "success"
    )
    return True


def create_virtual_environment():
    """创建并激活Python虚拟环境"""
    print_status("创建Python虚拟环境...")

    venv_name = "venv"
    venv_path = Path(venv_name)

    # 检查虚拟环境是否已存在
    if venv_path.exists():
        print_status(f"虚拟环境已存在: {venv_path}", "info")

        # 检查是否包含必要的文件
        if (venv_path / "bin" / "python").exists() or (
            venv_path / "Scripts" / "python.exe"
        ).exists():
            print_status("虚拟环境完整，跳过创建", "success")
            return True
        else:
            print_status("虚拟环境不完整，重新创建...", "warning")
            shutil.rmtree(venv_path)

    # 创建虚拟环境
    print_status("正在创建虚拟环境...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", venv_name],
            check=True,
            capture_output=True,
            text=True,
        )
        print_status(f"虚拟环境创建成功: {venv_path.absolute()}", "success")

        # 获取虚拟环境中的Python路径
        if platform.system() == "Windows":
            python_path = venv_path / "Scripts" / "python.exe"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"

        # 验证虚拟环境
        if python_path.exists():
            print_status(f"虚拟环境Python: {python_path}", "success")

            # 升级pip
            print_status("升级虚拟环境中的pip...")
            subprocess.run(
                [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
                check=False,
                capture_output=True,
            )

            # 将虚拟环境路径保存到全局变量，供后续使用
            global VENV_PYTHON, VENV_PIP
            VENV_PYTHON = str(python_path)
            VENV_PIP = str(pip_path)

            return True
        else:
            print_status("虚拟环境创建失败", "error")
            return False

    except subprocess.CalledProcessError as e:
        print_status(f"创建虚拟环境失败: {e}", "error")
        return False
    except Exception as e:
        print_status(f"创建虚拟环境时发生错误: {e}", "error")
        return False


def check_whisper_cpp():
    """检查whisper.cpp是否安装"""
    print_status("检查whisper.cpp...")

    if shutil.which("whisper-cli"):
        print_status("whisper-cli已安装", "success")
        return True

    print_status("whisper-cli未找到", "warning")
    system = platform.system().lower()

    if system == "darwin":  # macOS
        print_status("在macOS上安装whisper.cpp...")
        if shutil.which("brew"):
            return run_command(
                "brew install whisper-cpp", "通过Homebrew安装whisper.cpp", check=False
            )
        else:
            print_status("请先安装Homebrew: https://brew.sh/", "error")
            return False

    elif system == "linux":
        print_status("Linux系统需要手动编译安装whisper.cpp", "warning")
        print_status("请参考: https://github.com/ggerganov/whisper.cpp", "info")
        return False

    elif system == "windows":
        print_status("Windows系统需要手动安装whisper.cpp", "warning")
        print_status("请从官方仓库下载预编译版本", "info")
        return False

    return False


def install_blackhole():
    """安装BlackHole音频驱动"""
    print_status("检查BlackHole音频驱动...")

    system = platform.system().lower()

    if system != "darwin":
        print_status("BlackHole仅支持macOS系统", "info")
        return True

    # 检查是否已安装
    if shutil.which("brew"):
        # 检查BlackHole是否已安装
        result = subprocess.run(
            "brew list | grep blackhole", shell=True, capture_output=True, text=True
        )

        if "blackhole" in result.stdout:
            print_status("BlackHole已安装", "success")
            return True

        print_status("安装BlackHole音频驱动...")
        return run_command(
            "brew install blackhole-2ch", "通过Homebrew安装BlackHole", check=False
        )
    else:
        print_status("Homebrew未安装，无法安装BlackHole", "warning")
        print_status("请先安装Homebrew: https://brew.sh/", "info")
        return False


def install_python_dependencies():
    """安装Python依赖"""
    print_status("安装Python依赖...")

    # 检查虚拟环境是否已创建
    if not VENV_PYTHON:
        print_status("虚拟环境未创建，无法安装依赖", "error")
        return False

    # 检查requirements.txt是否存在
    if not os.path.exists("requirements.txt"):
        print_status("requirements.txt不存在，创建基础依赖文件...", "warning")
        requirements = """# 会议实时翻译系统依赖
torch>=2.8.0
transformers>=4.30.0
sounddevice>=0.4.0
webrtcvad>=2.0.10
numpy>=1.24.0
colorama>=0.4.6
"""
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements)

    # 使用虚拟环境安装依赖
    print_status(f"使用虚拟环境: {VENV_PYTHON}")
    return run_command(
        f"{VENV_PYTHON} -m pip install -r requirements.txt",
        "在虚拟环境中安装Python依赖包",
        check=False,
    )


def create_models_directory():
    """创建模型目录"""
    print_status("创建模型目录...")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    print_status(f"模型目录: {models_dir.absolute()}", "success")
    return True


def download_whisper_models():
    """下载Whisper模型"""
    print_status("检查Whisper模型...")

    models_dir = Path("models")
    models = {
        "small": {
            "file": "ggml-small.bin",
            "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
            "size": "244MB",
            "recommended": True,
        },
        "base": {
            "file": "ggml-base.bin",
            "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
            "size": "147MB",
            "recommended": False,
        },
    }

    downloaded = False

    for model_name, info in models.items():
        model_path = models_dir / info["file"]

        if model_path.exists():
            print_status(f"模型 {model_name} 已存在 ({info['size']})", "success")
            downloaded = True
        elif info["recommended"]:
            print_status(f"下载推荐模型: {model_name} ({info['size']})...")
            success = run_command(
                f"curl -L -o {model_path} {info['url']}",
                f"下载 {model_name} 模型",
                check=False,
            )
            if success:
                print_status(f"模型 {model_name} 下载完成", "success")
                downloaded = True
            else:
                print_status(f"模型 {model_name} 下载失败", "error")

    if not downloaded:
        print_status("没有可用的Whisper模型", "error")
        print_status("请手动下载模型到models/目录", "info")
        for model_name, info in models.items():
            print(f"  {model_name}: curl -L -o models/{info['file']} {info['url']}")
        return False

    return True


def check_audio_setup():
    """检查音频设备设置"""
    print_status("检查音频设备...")

    try:
        import sounddevice as sd

        devices = sd.query_devices()

        print_status("可用音频设备:", "info")
        for i, device in enumerate(devices):
            device_info = f"  [{i}] {device['name']} ({device['max_input_channels']}in/{device['max_output_channels']}out)"
            print(device_info)

        # 检查音频输出设备
        output_devices = []
        for i, device in enumerate(devices):
            if device["max_output_channels"] > 0 and device["max_input_channels"] > 0:
                output_devices.append((i, device["name"]))

        if output_devices:
            print_status("找到支持输入捕获的输出设备:", "success")
            for i, name in output_devices:
                print(f"  [{i}] {name}")
        else:
            print_status("未找到支持输入捕获的输出设备", "warning")
            print_status("系统将使用默认音频设备", "info")

        return True

    except ImportError:
        print_status("sounddevice未安装，无法检查音频设备", "error")
        return False
    except Exception as e:
        print_status(f"音频设备检查失败: {e}", "error")
        return False


def create_startup_scripts():
    """创建启动脚本"""
    print_status("创建启动脚本...")

    # macOS/Linux脚本
    if platform.system() != "Windows":
        script_content = """#!/bin/bash
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
"""

        with open("start_translator.sh", "w", encoding="utf-8") as f:
            f.write(script_content)

        os.chmod("start_translator.sh", 0o755)
        print_status("创建启动脚本: start_translator.sh", "success")

    # Windows脚本
    if platform.system() == "Windows":
        bat_content = """@echo off
REM 会议翻译系统启动脚本

echo 🚀 启动会议翻译系统...

REM 检查虚拟环境
if not exist "venv" (
    echo ❌ 虚拟环境不存在，请先运行安装脚本
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\\Scripts\\activate.bat

echo 选择翻译模式:
echo 1. 英文 → 中文 (默认)
echo 2. 中文 → 英文  
echo 3. 自动检测 → 中文
echo 4. 自定义

set /p choice=请选择 (1-4): 

if "%choice%"=="1" goto en_zh
if "%choice%"=="2" goto zh_en
if "%choice%"=="3" goto auto_zh
if "%choice%"=="4" goto custom
if "%choice%"=="" goto en_zh

:en_zh
python simple_transcirber.py --source en --target zh
goto end

:zh_en
python simple_transcirber.py --source zh --target en
goto end

:auto_zh
python simple_transcirber.py --source auto --target zh
goto end

:custom
echo 可用语言: en, zh, ru, fr, de, ja, ko, es, it, pt, ar
set /p src_lang=源语言 (auto为自动检测): 
set /p tgt_lang=目标语言: 
python simple_transcirber.py --source %src_lang% --target %tgt_lang%
goto end

:end
pause
"""

        with open("start_translator.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)

        print_status("创建启动脚本: start_translator.bat", "success")

    return True


def main():
    """主安装流程"""
    print("=" * 60)
    print("🎯 会议实时翻译系统 - 安装程序")
    print("=" * 60)

    # 检查步骤
    steps = [
        ("检查Python版本", check_python_version),
        ("创建Python虚拟环境", create_virtual_environment),
        ("检查whisper.cpp", check_whisper_cpp),
        ("安装BlackHole音频驱动", install_blackhole),
        ("安装Python依赖", install_python_dependencies),
        ("创建模型目录", create_models_directory),
        ("下载Whisper模型", download_whisper_models),
        ("检查音频设备", check_audio_setup),
        ("创建启动脚本", create_startup_scripts),
    ]

    success_count = 0
    total_steps = len(steps)

    for step_name, step_func in steps:
        print(f"\n{'-' * 40}")
        print(f"步骤: {step_name}")
        print(f"{'-' * 40}")

        try:
            if step_func():
                success_count += 1
                print_status(f"✅ {step_name} - 完成", "success")
            else:
                print_status(f"⚠️ {step_name} - 失败", "warning")
        except Exception as e:
            print_status(f"❌ {step_name} - 错误: {e}", "error")

    # 安装总结
    print(f"\n{'=' * 60}")
    print("📊 安装总结")
    print(f"{'=' * 60}")

    print_status(f"完成步骤: {success_count}/{total_steps}")

    if success_count == total_steps:
        print_status("🎉 安装完成！系统已准备就绪", "success")
        print("\n🚀 启动方法:")
        if platform.system() != "Windows":
            print("  ./start_translator.sh")
        else:
            print("  start_translator.bat")
        print(
            "  或者: source venv/bin/activate && python simple_transcirber.py --source en --target zh"
        )

    elif success_count >= total_steps - 2:
        print_status("⚠️ 基本安装完成，部分功能可能受限", "warning")
        print("\n💡 建议:")
        print("  - 手动安装缺失的组件")
        print("  - 检查错误信息并解决")

    else:
        print_status("❌ 安装失败，请检查错误信息", "error")
        print("\n🔧 故障排除:")
        print("  1. 确保网络连接正常")
        print("  2. 检查Python版本 >= 3.8")
        print("  3. 安装whisper.cpp")
        print("  4. 重新运行安装程序")

    print(f"\n📚 更多帮助:")
    print("  - GitHub: https://github.com/your-repo")
    print("  - 文档: README.md")
    print("  - 第一次安装完成blackhole音频驱动后需要重启,否则无法看到音频设备")


if __name__ == "__main__":
    main()
