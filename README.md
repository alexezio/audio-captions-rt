# 🎯 音频实时转录系统 (Audio Real-time Transcription)

[English](#english) | [中文](#中文)

---

## 中文

一个基于 macOS 的音频输出流实时转录系统，专为会议、聊天等场景设计，能够实时捕获设备音频输出并进行语音识别和转录。

### 🌟 项目特色

- **实时转录**: 支持音频流的实时语音识别和转录
- **音频捕获**: 使用 BlackHole + Multi-Output Device 技术捕获系统音频输出
- **智能检测**: 集成 WebRTC VAD 进行说话检测，提高转录准确性
- **多语言支持**: 支持多种语言的语音识别和转录
- **虚拟环境**: 使用 Python 虚拟环境确保依赖隔离
- **一键安装**: 自动化安装脚本，简化部署流程

### 🔧 技术原理

#### 音频捕获架构

```
系统音频输出 → Multi-Output Device → 同时输出到两个目标
                    ├── 扬声器/耳机 (正常播放，无影响)
                    └── BlackHole → 转录系统 (后台捕获)
```

**工作原理说明：**

1. **Multi-Output Device**: 创建虚拟音频设备，能够将同一音频流同时输出到多个目标
   - ✅ **扬声器/耳机**: 正常播放音频，用户听到声音，完全不受影响
   - ✅ **BlackHole**: 同时捕获音频流，用于转录系统处理

2. **BlackHole**: 虚拟音频驱动，捕获音频流而不产生实际输出
   - 不会产生任何声音，完全静默运行
   - 不影响正常的音频播放体验

3. **音频处理**: 使用 WebRTC VAD 检测语音活动，过滤静音
   - 智能识别说话片段，提高转录效率
   - 减少噪音干扰，提升转录质量

4. **转录引擎**: 基于 Whisper.cpp 进行实时语音识别
   - 后台运行，不影响音频播放
   - 实时生成转录文本

#### 核心组件

- **BlackHole 2ch**: 虚拟音频驱动，用于音频流捕获
- **WebRTC VAD**: 语音活动检测，识别说话片段
- **Whisper.cpp**: 高效的语音识别引擎
- **Python 虚拟环境**: 依赖管理和环境隔离

### 📋 系统要求

- **操作系统**: macOS 10.15+ (Catalina 及以上)
- **Python**: 3.11+
- **内存**: 建议 8GB+
- **存储**: 至少 500MB 可用空间
- **网络**: 首次安装需要下载模型文件

### 🚀 快速开始

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/audio-captions-rt.git
cd audio-captions-rt
```

#### 2. 运行安装脚本

```bash
python3 setup-env.py
```

安装脚本会自动完成以下操作：
- ✅ 检查 Python 版本
- ✅ 创建 Python 虚拟环境
- ✅ 安装 whisper.cpp
- ✅ 安装 BlackHole 音频驱动
- ✅ 安装 Python 依赖包
- ✅ 下载 Whisper 模型
- ✅ 检查音频设备
- ✅ 创建启动脚本

#### 3. 启动转录系统

##### 方法一：使用启动脚本（推荐）

```bash
# macOS/Linux
./start_translator.sh

# Windows
start_translator.bat
```

##### 方法二：手动启动

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动转录系统
python simple_transcriber.py --source en --target zh
```

### ⚙️ 配置选项

#### 语言设置

支持的语言代码：
- `en`: 英语
- `zh`: 中文
- `ja`: 日语
- `ko`: 韩语
- `fr`: 法语
- `de`: 德语
- `es`: 西班牙语
- `it`: 意大利语
- `pt`: 葡萄牙语
- `ru`: 俄语
- `ar`: 阿拉伯语
- `auto`: 自动检测

#### 转录模式

1. **英文 → 中文**: 英语音频转录为中文文本
2. **中文 → 英文**: 中文音频转录为英文文本
3. **自动检测 → 中文**: 自动识别语言并转录为中文
4. **自定义**: 手动指定源语言和目标语言

#### 音频设备配置

系统会自动检测可用的音频设备，并推荐支持输入捕获的输出设备。您可以在系统偏好设置中配置音频设备：

1. 打开 **系统偏好设置** → **声音**
2. 创建 **Multi-Output Device**
3. 添加 **BlackHole 2ch** 和您的扬声器
4. 设置为默认输出设备

查阅此[wiki](https://github.com/ExistentialAudio/BlackHole/wiki/Multi-Output-Device)获得更详细的说明

### 📁 项目结构

```
audio-captions-rt/
├── README.md                 # 项目说明文档
├── setup-env.py             # 自动化安装脚本
├── simple_transcriber.py    # 主要转录程序
├── requirements.txt         # Python 依赖列表
├── start_translator.sh     # macOS/Linux 启动脚本
├── start_translator.bat    # Windows 启动脚本
├── venv/                   # Python 虚拟环境
└── models/                 # Whisper 模型文件
    ├── ggml-small.bin     # 推荐模型 (244MB)
    └── ggml-base.bin      # 基础模型 (147MB)
```

### 🚧 开发计划 (TODO List)

我们正在积极开发以下功能，敬请期待：

#### 🔄 实时翻译
- [ ] 在转录基础上实现实时翻译功能
- [ ] 支持多种语言之间的互译
- [ ] 集成高质量翻译模型
- [ ] 实时字幕显示

#### 📊 音频汇总
- [ ] 会议音频内容智能总结
- [ ] 关键点提取和标记
- [ ] 时间轴标注
- [ ] 导出多种格式（文本、PDF、Markdown）

#### 🎤 智能语音系统
- [ ] **麦克风拦截**: 实时捕获麦克风输入
- [ ] **音色克隆**: 学习并复制特定说话人的音色特征
- [ ] **TTS 翻译**: 将说话人的语言实时翻译成其他语音
- [ ] **跨语言对话**: 支持不同语言用户之间的实时对话

#### 🌟 高级功能
- [ ] 多说话人识别和分离
- [ ] 情感分析和语调识别
- [ ] 自定义词汇和专业术语支持
- [ ] 云端同步和协作功能

---

**💡 欢迎贡献**: 如果您对这些功能感兴趣，欢迎提交 Issue 或 Pull Request 来帮助实现！

### 🔍 故障排除

#### 常见问题

##### 1. BlackHole 安装失败
```bash
# 手动安装 BlackHole
brew install blackhole-2ch
```

##### 2. 音频设备未检测到
- 确保 BlackHole 已正确安装
- 检查系统音频权限设置
- 重启音频服务

##### 3. 转录质量不佳
- 使用更高质量的 Whisper 模型
- 调整音频输入音量
- 确保环境噪音较低

##### 4. 虚拟环境问题
```bash
# 重新创建虚拟环境
rm -rf venv
python3 setup-env.py
```

#### 日志和调试

系统运行时会显示详细的日志信息，包括：
- 音频设备检测结果
- 转录进度和状态
- 错误信息和警告

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

#### 开发环境设置

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

#### 代码规范

- 使用 Python 3.11+ 语法
- 遵循 PEP 8 代码风格
- 添加适当的注释和文档
- 确保代码通过测试

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

### 🙏 致谢

- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - 高效的语音识别引擎
- [BlackHole](https://github.com/ExistentialAudio/BlackHole) - 虚拟音频驱动
- [WebRTC VAD](https://github.com/wiseman/py-webrtcvad) - 语音活动检测
- [Homebrew](https://brew.sh/) - macOS 包管理器

### 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/your-username/audio-captions-rt)
- **问题反馈**: [Issues](https://github.com/your-username/audio-captions-rt/issues)
- **功能建议**: [Discussions](https://github.com/your-username/audio-captions-rt/discussions)

---

## English

A real-time audio output stream transcription system based on macOS, designed for meetings, chats, and other scenarios. It can capture device audio output in real-time and perform speech recognition and transcription.

### 🌟 Features

- **Real-time Transcription**: Supports real-time speech recognition and transcription of audio streams
- **Audio Capture**: Uses BlackHole + Multi-Output Device technology to capture system audio output
- **Smart Detection**: Integrates WebRTC VAD for speech detection, improving transcription accuracy
- **Multi-language Support**: Supports speech recognition and transcription in multiple languages
- **Virtual Environment**: Uses Python virtual environment to ensure dependency isolation
- **One-click Installation**: Automated installation script to simplify deployment

### 🔧 Technical Principles

#### Audio Capture Architecture

```
System Audio Output → Multi-Output Device → Outputs to Two Destinations
                           ├── Speakers/Headphones (Normal playback, no impact)
                           └── BlackHole → Transcription System (Background capture)
```

**Working Principle:**

1. **Multi-Output Device**: Creates virtual audio devices that can output the same audio stream to multiple destinations simultaneously
   - ✅ **Speakers/Headphones**: Normal audio playback, users hear sound without any interference
   - ✅ **BlackHole**: Simultaneously captures audio stream for transcription system processing

2. **BlackHole**: Virtual audio driver that captures audio streams without producing actual output
   - Generates no sound, runs completely silently
   - Does not affect normal audio playback experience

3. **Audio Processing**: Uses WebRTC VAD to detect speech activity and filter silence
   - Intelligently identifies speech segments, improving transcription efficiency
   - Reduces noise interference, enhancing transcription quality

4. **Transcription Engine**: Real-time speech recognition based on Whisper.cpp
   - Runs in background without affecting audio playback
   - Generates transcription text in real-time

#### Core Components

- **BlackHole 2ch**: Virtual audio driver for audio stream capture
- **WebRTC VAD**: Voice Activity Detection for identifying speech segments
- **Whisper.cpp**: Efficient speech recognition engine
- **Python Virtual Environment**: Dependency management and environment isolation

### 📋 System Requirements

- **Operating System**: macOS 10.15+ (Catalina and above)
- **Python**: 3.11+
- **Memory**: Recommended 8GB+
- **Storage**: At least 500MB available space
- **Network**: Required for downloading model files on first installation

### 🚀 Quick Start

#### 1. Clone the Project

```bash
git clone https://github.com/your-username/audio-captions-rt.git
cd audio-captions-rt
```

#### 2. Run Installation Script

```bash
python3 setup-env.py
```

The installation script will automatically complete the following operations:
- ✅ Check Python version
- ✅ Create Python virtual environment
- ✅ Install whisper.cpp
- ✅ Install BlackHole audio driver
- ✅ Install Python dependencies
- ✅ Download Whisper models
- ✅ Check audio devices
- ✅ Create startup scripts

#### 3. Start Transcription System

##### Method 1: Use Startup Script (Recommended)

```bash
# macOS/Linux
./start_translator.sh

# Windows
start_translator.bat
```

##### Method 2: Manual Startup

```bash
# Activate virtual environment
source venv/bin/activate

# Start transcription system
python simple_transcriber.py --source en --target zh
```

### ⚙️ Configuration Options

#### Language Settings

Supported language codes:
- `en`: English
- `zh`: Chinese
- `ja`: Japanese
- `ko`: Korean
- `fr`: French
- `de`: German
- `es`: Spanish
- `it`: Italian
- `pt`: Portuguese
- `ru`: Russian
- `ar`: Arabic
- `auto`: Auto-detect

#### Transcription Modes

1. **English → Chinese**: Transcribe English audio to Chinese text
2. **Chinese → English**: Transcribe Chinese audio to English text
3. **Auto-detect → Chinese**: Automatically detect language and transcribe to Chinese
4. **Custom**: Manually specify source and target languages

#### Audio Device Configuration

The system automatically detects available audio devices and recommends output devices that support input capture. You can configure audio devices in System Preferences:

1. Open **System Preferences** → **Sound**
2. Create **Multi-Output Device**
3. Add **BlackHole 2ch** and your speakers
4. Set as default output device

### 📁 Project Structure

```
audio-captions-rt/
├── README.md                 # Project documentation
├── setup-env.py             # Automated installation script
├── simple_transcriber.py    # Main transcription program
├── requirements.txt         # Python dependency list
├── start_translator.sh     # macOS/Linux startup script
├── start_translator.bat    # Windows startup script
├── venv/                   # Python virtual environment
└── models/                 # Whisper model files
    ├── ggml-small.bin     # Recommended model (244MB)
    └── ggml-base.bin      # Basic model (147MB)
```

### 🚧 Development Roadmap (TODO List)

We are actively developing the following features. Stay tuned!

#### 🔄 Real-time Translation
- [ ] Implement real-time translation based on transcription
- [ ] Support translation between multiple languages
- [ ] Integrate high-quality translation models
- [ ] Real-time subtitle display

#### 📊 Audio Summarization
- [ ] Intelligent meeting audio content summarization
- [ ] Key point extraction and tagging
- [ ] Timeline annotation
- [ ] Export to multiple formats (Text, PDF, Markdown)

#### 🎤 Intelligent Voice System
- [ ] **Microphone Interception**: Real-time capture of microphone input
- [ ] **Voice Cloning**: Learn and replicate specific speaker's voice characteristics
- [ ] **TTS Translation**: Real-time translation of speaker's language into other voices
- [ ] **Cross-language Dialogue**: Support real-time conversation between users of different languages

#### 🌟 Advanced Features
- [ ] Multi-speaker identification and separation
- [ ] Emotion analysis and tone recognition
- [ ] Custom vocabulary and professional terminology support
- [ ] Cloud synchronization and collaboration features

---

**💡 Welcome Contributions**: If you're interested in these features, feel free to submit Issues or Pull Requests to help implement them!

### 🔍 Troubleshooting

#### Common Issues

##### 1. BlackHole Installation Failed
```bash
# Manually install BlackHole
brew install blackhole-2ch
```

##### 2. Audio Device Not Detected
- Ensure BlackHole is properly installed
- Check system audio permission settings
- Restart audio services

##### 3. Poor Transcription Quality
- Use higher quality Whisper models
- Adjust audio input volume
- Ensure low environmental noise

##### 4. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 setup-env.py
```

#### Logging and Debugging

The system displays detailed log information during operation, including:
- Audio device detection results
- Transcription progress and status
- Error messages and warnings

### 🤝 Contributing

We welcome Issue submissions and Pull Requests!

#### Development Environment Setup

1. Fork the project
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

#### Code Standards

- Use Python 3.11+ syntax
- Follow PEP 8 code style
- Add appropriate comments and documentation
- Ensure code passes tests

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Efficient speech recognition engine
- [BlackHole](https://github.com/ExistentialAudio/BlackHole) - Virtual audio driver
- [WebRTC VAD](https://github.com/wiseman/py-webrtcvad) - Voice Activity Detection
- [Homebrew](https://brew.sh/) - macOS package manager

### 📞 Contact

- **Project Homepage**: [GitHub Repository](https://github.com/your-username/audio-captions-rt)
- **Issue Feedback**: [Issues](https://github.com/your-username/audio-captions-rt/issues)
- **Feature Suggestions**: [Discussions](https://github.com/your-username/audio-captions-rt/discussions)

---

⭐ If this project helps you, please give us a star!
