#!/usr/bin/env python3
"""
简化版实时转录系统
基于sounddevice官方示例，只保留转录功能
"""

import sounddevice as sd
import numpy as np
import queue
import threading
import time
import subprocess
import tempfile
import wave
import json
import os
import sys
import webrtcvad
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)


class SimpleTranscriber:
    def __init__(self, whisper_model="small"):
        print(f"{Fore.CYAN}🚀 初始化简化版转录系统{Style.RESET_ALL}")

        # 音频设置
        self.sample_rate = None
        self.frame_duration = 30  # ms
        self.frame_size = None

        # 分段参数 - 提高转录频率
        self.min_segment_duration = 1  # 秒 - 从2.0降到1.5
        self.max_segment_duration = 3.0  # 秒 - 从8.0降到4.0
        self.silence_threshold = 10  # 静音帧数 - 从50降到20

        # 计算帧数
        self.min_segment_frames = None
        self.max_segment_frames = None

        # 音频缓冲
        self.speech_frames = []
        self.silence_count = 0

        # 队列和状态
        self.audio_queue = queue.Queue()
        self.listening = False
        self.transcription_history = []
        self.segment_counter = 0

        # 设置Whisper
        self.setup_whisper(whisper_model)

        # 设置音频设备
        self.setup_audio_device()

        # 设置WebRTC VAD
        self.setup_vad()

        print(f"{Fore.GREEN}✓ 转录系统就绪{Style.RESET_ALL}")

    def setup_whisper(self, whisper_model):
        """设置Whisper模型"""
        try:
            result = subprocess.run(
                ["../whisper.cpp/build/bin/whisper-cli", "--help"],
                capture_output=True,
                text=True,
            )
            print(f"{Fore.GREEN}✓ whisper-cli 可用{Style.RESET_ALL}")

            model_configs = {
                "tiny": {"file": "ggml-tiny.bin", "size": "39MB"},
                "base": {"file": "ggml-base.bin", "size": "147MB"},
                "small": {"file": "ggml-small.bin", "size": "244MB"},
                "small.en": {"file": "ggml-small.en.bin", "size": "244MB"},
                "medium": {"file": "ggml-medium.bin", "size": "769MB"},
                "large-v3": {"file": "ggml-large-v3.bin", "size": "1.55GB"},
            }

            if whisper_model not in model_configs:
                print(f"{Fore.RED}❌ 不支持的模型: {whisper_model}{Style.RESET_ALL}")
                sys.exit(1)

            config = model_configs[whisper_model]
            self.whisper_model_path = f'./models/{config["file"]}'

            if not os.path.exists(self.whisper_model_path):
                print(
                    f"{Fore.RED}❌ 模型文件不存在: {self.whisper_model_path}{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.YELLOW}请下载模型: curl -L -o {self.whisper_model_path} https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{config['file']}{Style.RESET_ALL}"
                )
                sys.exit(1)

            # 检查模型文件大小
            file_size = os.path.getsize(self.whisper_model_path)
            expected_sizes = {
                "tiny": 39 * 1024 * 1024,  # 39MB
                "base": 147 * 1024 * 1024,  # 147MB
                "small": 244 * 1024 * 1024,  # 244MB
                "medium": 769 * 1024 * 1024,  # 769MB
                "large-v3": 1.55 * 1024 * 1024 * 1024,  # 1.55GB
            }

            expected_size = expected_sizes.get(whisper_model, 0)
            if file_size < expected_size * 0.9:  # 允许10%的误差
                print(
                    f"{Fore.RED}❌ 模型文件可能损坏: {self.whisper_model_path}{Style.RESET_ALL}"
                )
                print(f"   当前大小: {file_size / (1024*1024):.1f}MB")
                print(f"   期望大小: {expected_size / (1024*1024):.1f}MB")
                print(f"{Fore.YELLOW}请重新下载模型文件{Style.RESET_ALL}")
                sys.exit(1)

            print(
                f"{Fore.CYAN}🧠 使用Whisper模型: {whisper_model} ({config['size']}){Style.RESET_ALL}"
            )

        except FileNotFoundError:
            print(f"{Fore.RED}❌ whisper-cli 未安装{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}macOS安装: brew install whisper-cpp{Style.RESET_ALL}")
            sys.exit(1)

    def setup_audio_device(self):
        """设置音频设备"""
        print(f"{Fore.CYAN}🎵 设置音频设备...{Style.RESET_ALL}")

        # 列出可用设备
        devices = sd.query_devices()
        print(f"{Fore.YELLOW}可用音频设备:{Style.RESET_ALL}")

        blackhole_id = None
        multi_output_id = None

        for i, device in enumerate(devices):
            device_info = f"  [{i}] {device['name']} - {device['max_input_channels']}in/{device['max_output_channels']}out"
            print(device_info)

            # 查找BlackHole和Multi-Output Device
            device_name = device["name"].lower()
            if "blackhole" in device_name:
                blackhole_id = i
            elif "multi" in device_name and "output" in device_name:
                multi_output_id = i

        print()

        # 选择BlackHole作为捕获设备
        if blackhole_id is not None:
            self.audio_device = blackhole_id
            print(
                f"{Fore.GREEN}✓ 选择BlackHole设备: [{blackhole_id}] {devices[blackhole_id]['name']}{Style.RESET_ALL}"
            )
        else:
            print(f"{Fore.RED}❌ 未找到BlackHole设备{Style.RESET_ALL}")
            sys.exit(1)

        # 获取设备信息并设置采样率
        try:
            device_info = sd.query_devices(self.audio_device, "input")
            self.sample_rate = int(device_info["default_samplerate"])
            print(
                f"{Fore.GREEN}✓ 音频设备采样率: {self.sample_rate} Hz{Style.RESET_ALL}"
            )
        except Exception as e:
            print(
                f"{Fore.YELLOW}⚠️ 无法获取设备采样率，使用默认值: {e}{Style.RESET_ALL}"
            )
            self.sample_rate = 48000

        # 计算帧大小和分段参数
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        frames_per_second = 1000 / self.frame_duration
        self.min_segment_frames = int(self.min_segment_duration * frames_per_second)
        self.max_segment_frames = int(self.max_segment_duration * frames_per_second)

        print(f"{Fore.GREEN}✓ 音频帧大小: {self.frame_size} 样本{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}✓ 分段参数: {self.min_segment_duration}s-{self.max_segment_duration}s{Style.RESET_ALL}"
        )

        # 检查Multi-Output Device配置
        if multi_output_id is not None:
            print(
                f"{Fore.GREEN}✓ 发现Multi-Output Device: [{multi_output_id}] {devices[multi_output_id]['name']}{Style.RESET_ALL}"
            )
            print(
                f"{Fore.CYAN}💡 建议将系统输出设置为Multi-Output Device{Style.RESET_ALL}"
            )
            print(
                f"{Fore.CYAN}   这样音频会同时输出到Speakers和BlackHole{Style.RESET_ALL}"
            )

        print()

    def setup_vad(self):
        """设置WebRTC VAD"""
        try:
            # 创建VAD实例，敏感度设置为2（中等）
            self.vad = webrtcvad.Vad(2)
            print(f"{Fore.GREEN}✓ WebRTC VAD 初始化成功{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ WebRTC VAD 初始化失败: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}请确保已安装: pip install webrtcvad{Style.RESET_ALL}")
            sys.exit(1)

    def audio_callback(self, indata, frames, time, status):
        """音频回调函数 - 基于sounddevice官方示例"""
        if status:
            print(f"⚠️ 音频状态: {status}")
        if self.listening:
            self.audio_queue.put(indata.copy())

    def detect_speech(self, audio_chunk):
        """使用WebRTC VAD进行语音活动检测"""
        try:
            # WebRTC VAD支持的采样率和对应的帧长度
            vad_configs = {
                8000: 80,  # 10ms @ 8kHz
                16000: 160,  # 10ms @ 16kHz
                32000: 320,  # 10ms @ 32kHz
                48000: 480,  # 10ms @ 48kHz
            }

            # 选择最接近的采样率
            if self.sample_rate in vad_configs:
                vad_sample_rate = self.sample_rate
                vad_frame_size = vad_configs[vad_sample_rate]
            else:
                # 重采样到16000Hz
                vad_sample_rate = 16000
                vad_frame_size = vad_configs[vad_sample_rate]

                # 计算重采样因子
                downsample_factor = self.sample_rate // vad_sample_rate
                if downsample_factor > 1:
                    audio_chunk = audio_chunk[::downsample_factor]
                else:
                    # 如果采样率太低，进行上采样
                    upsample_factor = vad_sample_rate // self.sample_rate
                    audio_chunk = np.repeat(audio_chunk, upsample_factor)

            # 确保音频长度是VAD帧大小的整数倍
            if len(audio_chunk) < vad_frame_size:
                # 如果太短，用零填充
                audio_chunk = np.pad(
                    audio_chunk, (0, vad_frame_size - len(audio_chunk))
                )
            elif len(audio_chunk) > vad_frame_size:
                # 如果太长，截取到最近的帧边界
                num_frames = len(audio_chunk) // vad_frame_size
                audio_chunk = audio_chunk[: num_frames * vad_frame_size]

            # 转换为int16格式，确保范围正确
            audio_float = np.clip(audio_chunk, -1.0, 1.0)
            audio_int16 = (audio_float * 32767).astype(np.int16)

            # 使用WebRTC VAD检测语音
            return self.vad.is_speech(audio_int16.tobytes(), vad_sample_rate)

        except Exception as e:
            print(f"VAD错误: {e}")
            # VAD失败时，回退到简单的能量检测
            try:
                rms = np.sqrt(np.mean(audio_chunk**2))
                threshold = 0.001
                return rms > threshold
            except:
                return False

    def save_audio_segment(self, audio_data):
        """保存音频片段为临时文件"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_int16 = (audio_data * 32767).astype(np.int16)

            with wave.open(f.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_int16.tobytes())

            return f.name

    def transcribe_with_whisper(self, audio_file):
        """使用Whisper进行语音识别"""
        try:
            # 构建whisper-cli命令
            cmd = [
                "whisper-cli",
                "-m",
                self.whisper_model_path,
                "-f",
                audio_file,
                "--output-json",
                "--language",
                "auto",
                "--no-timestamps",
                "--threads",
                "4",
            ]

            print(cmd)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                # 尝试解析JSON输出
                json_file = audio_file.replace(".wav", ".json")

                if os.path.exists(json_file):
                    try:
                        with open(json_file, "r") as f:
                            data = json.load(f)
                            if "transcription" in data and data["transcription"]:
                                text = data["transcription"][0]["text"].strip()
                                if text and len(text) > 3:
                                    return text
                        os.unlink(json_file)
                    except Exception as e:
                        pass

                # Fallback: 解析标准输出
                if result.stdout:
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if (
                            line
                            and len(line) > 3
                            and not line.startswith("[")
                            and "whisper" not in line.lower()
                        ):
                            return line

            return None

        except Exception as e:
            print(f"❌ Whisper转录失败: {e}")
            return None

    def process_audio_segment(self, audio_data, segment_id):
        """处理音频片段"""
        try:
            start_time = time.time()

            # 保存音频文件
            audio_file = self.save_audio_segment(audio_data)

            # 使用Whisper转录
            transcription = self.transcribe_with_whisper(audio_file)

            # 清理临时文件
            try:
                os.unlink(audio_file)
            except:
                pass

            if transcription:
                processing_time = time.time() - start_time

                # 记录转录结果
                result = {
                    "segment_id": segment_id,
                    "transcription": transcription,
                    "duration": len(audio_data) / self.sample_rate,
                    "processing_time": processing_time,
                    "timestamp": time.strftime("%H:%M:%S"),
                }

                self.transcription_history.append(result)

                # 显示结果
                print(
                    f"\n{Fore.GREEN}📝 片段 {segment_id} ({result['duration']:.1f}s):{Style.RESET_ALL}"
                )
                print(f"{Fore.CYAN}{transcription}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}处理时间: {processing_time:.2f}s{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}❌ 片段 {segment_id} 转录失败{Style.RESET_ALL}")

        except Exception as e:
            print(f"❌ 处理音频片段失败: {e}")

    def start_transcription(self):
        """开始转录"""
        print(f"{Fore.CYAN}🎤 开始音频转录...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 请播放音频或说话...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 按 Ctrl+C 停止转录{Style.RESET_ALL}")
        print()

        # 音频缓冲
        speech_frames = []
        silence_count = 0

        self.listening = True

        try:
            # 启动音频流 - 基于sounddevice官方示例
            with sd.InputStream(
                device=self.audio_device,
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocksize=self.frame_size,
                callback=self.audio_callback,
            ):
                print(f"{Fore.GREEN}🎧 开始监听音频...{Style.RESET_ALL}")

                while True:
                    try:
                        # 从队列获取音频数据
                        audio_chunk = self.audio_queue.get(timeout=0.1)
                        is_speech = self.detect_speech(audio_chunk.flatten())

                        if is_speech:
                            speech_frames.append(audio_chunk.flatten())
                            silence_count = 0

                            # 显示进度
                            if len(speech_frames) % 10 == 0:  # 更频繁的进度显示
                                duration = (
                                    len(speech_frames) * self.frame_duration / 1000
                                )
                                print(
                                    f"\r{Fore.CYAN}🗣️ 录音中: {duration:.1f}s{Style.RESET_ALL}",
                                    end="",
                                    flush=True,
                                )
                        else:
                            silence_count += 1

                        # 判断是否处理片段
                        should_process = False

                        if speech_frames:
                            # 达到最小时长且有足够静音
                            if (
                                len(speech_frames) >= self.min_segment_frames
                                and silence_count >= self.silence_threshold
                            ):
                                should_process = True
                            # 或者达到最大时长
                            elif len(speech_frames) >= self.max_segment_frames:
                                should_process = True

                        if should_process:
                            duration = len(speech_frames) * self.frame_duration / 1000
                            print(
                                f"\r{Fore.GREEN}📝 处理片段 ({duration:.1f}s)...{Style.RESET_ALL}"
                            )

                            full_audio = np.concatenate(speech_frames)
                            self.segment_counter += 1

                            # 异步处理
                            threading.Thread(
                                target=self.process_audio_segment,
                                args=(full_audio, self.segment_counter),
                                daemon=True,
                            ).start()

                            # 重置
                            speech_frames = []
                            silence_count = 0

                    except queue.Empty:
                        continue

        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}🛑 停止转录...{Style.RESET_ALL}")
            self.listening = False
            time.sleep(1)
            print(f"{Fore.GREEN}👋 转录结束！{Style.RESET_ALL}")

            # 显示统计信息
            if self.transcription_history:
                total_segments = len(self.transcription_history)
                avg_time = (
                    sum(item["processing_time"] for item in self.transcription_history)
                    / total_segments
                )
                print(
                    f"{Fore.YELLOW}📊 统计: 共处理 {total_segments} 个片段，平均处理时间 {avg_time:.2f}s{Style.RESET_ALL}"
                )


def main():
    """主函数"""
    print("🚀 简化版实时转录系统")
    print("=" * 40)

    # 创建转录器
    transcriber = SimpleTranscriber(whisper_model="small")

    # 开始转录
    transcriber.start_transcription()


if __name__ == "__main__":
    main()
