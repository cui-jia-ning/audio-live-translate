# 电脑音频实时翻译窗（audio-live-translate）

捕获电脑正在播放的音频（外语视频、跨国会议、直播、网课），实时语音识别并翻译成中文，在桌面置顶悬浮窗中滚动显示原文与译文。

## 工作原理

Kimi 插件（skill-only）+ 三个本地脚本，翻译本身由 Kimi agent 完成，无需任何 API key：

```
capture.py    每 10 秒通过 WASAPI loopback 录一段系统输出音频（soundcard）
transcribe.py faster-whisper 本地离线转写（默认 small 模型，CPU int8）
SKILL.md 流程  agent 读取识别结果 → 自己翻译成中文 → 追加写入 overlay_feed.jsonl
overlay.py    tkinter 置顶悬浮窗，每秒刷新滚动显示原文 + 译文
```

特点：

- 🎙️ 抓的是**系统输出混音**——任何播放器、会议软件、浏览器的声音都能翻
- 🔒 全本地：识别用 faster-whisper 离线模型，译文由 agent 生成，音频不出本机
- 🪟 置顶悬浮窗显示，可边看视频边看译文
- 🈚 无需 API key / 账号 / 联网（首次下载模型除外）

## 环境要求

- Windows 10/11（依赖 WASAPI loopback 回放捕获）
- Python 3.9+ 与 pip

## 安装

1. 依赖安装（幂等）：

   ```bash
   bash setup.sh
   ```

   安装 `soundcard` 与 `faster-whisper`；首次识别会自动下载 whisper 模型（tiny ≈75MB / small ≈460MB）。huggingface.co 不可达时可设 `HF_ENDPOINT=https://hf-mirror.com`（脚本已默认走该镜像）。

2. 在 Kimi 中登记本目录为个人插件（需已安装 Kimi 桌面版）：

   ```bash
   kimi-daimon kimi-plugin register-personal <本目录> --share-dir <daimon-share> --json
   ```

   然后到插件页「个人」页签点 ＋ 安装。

## 使用

安装后直接对 Kimi 说：

- 「实时翻译电脑声音」——开悬浮窗同传，说「停止」结束
- 「帮我把这个英文会议同传成中文」
- 「看日语直播，翻成中文显示在窗口里」
- 「换 tiny 模型，电脑有点卡」

可选参数：目标语言（默认中文）、源语言（`--language en/ja/ko`，缺省自动检测）、模型大小（tiny/base/small/medium）、录音块长度（默认 10 秒）。

## 限制

- **近实时**：译文通常落后声音约 15~30 秒（录音 10s + 识别数秒 + 翻译）。
- 背景音乐会明显降低识别质量，建议关闭。
- 识别的是全部输出混音，多路声音会互相干扰。
- CPU 识别占用较高；机器弱请用 `--model tiny`。

## License

MIT
