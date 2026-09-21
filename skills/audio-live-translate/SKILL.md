---
name: audio-live-translate
description: 识别/听译电脑正在播放的音频（外语视频、跨国会议、直播、网课），实时语音转文字并翻译成中文，在桌面悬浮窗口滚动显示原文和译文。触发：实时翻译电脑声音 / 视频听译 / 会议同传 / 直播翻译 / 悬浮翻译窗。
---

# 电脑音频实时翻译窗

捕获电脑**音频输出**（扬声器正在播放的任何声音：视频、会议、直播、网课），循环执行「录一段 → 离线语音识别 → 翻译成中文 → 写入悬浮窗」，在置顶窗口中滚动显示原文 + 译文。

## 触发场景

用户说类似：「实时翻译电脑播放的音频」「看英文视频帮我同声传译」「把会议/直播的声音翻成中文显示在窗口里」「悬浮翻译窗」。

## 前置检查（每次会话先做一次）

```bash
python3 -c "import soundcard" 2>/dev/null && python3 -c "import faster_whisper" 2>/dev/null && echo DEPS_OK
```

- 输出 `DEPS_OK` → 继续。
- 否则：告诉用户「插件依赖未装，请先运行插件根目录的 `bash setup.sh`（装 soundcard + faster-whisper，首次识别还会自动下载 whisper 模型）」，等用户装完再继续。**不要自行代跑 setup.sh。**
- 仅支持 Windows（依赖 WASAPI loopback 回放捕获）。

## 运行流程

1. **准备工作目录**：在工作区建 `live-translate/` 目录，feed 文件定为 `live-translate/overlay_feed.jsonl`。
2. **启动悬浮窗**（后台运行，独立于当前会话的常驻进程）：
   ```bash
   cd live-translate && python3 <skill_dir>/scripts/overlay.py overlay_feed.jsonl
   ```
   （`<skill_dir>` 为本 SKILL.md 所在目录。后台启动用 `nohup`/`Start-Process` 均可，记住进程 PID 以便停止。）若悬浮窗启动失败（如无 GUI），退而求其次：每轮把译文追加到一个 `translation.html` 文件并提示用户打开查看。
3. **翻译循环**（每轮约 10 秒，直到用户说「停止/够了」）：
   ```bash
   python3 <skill_dir>/scripts/capture.py --seconds 10 --out live-translate/chunk_NNN.wav
   python3 <skill_dir>/scripts/transcribe.py --wav live-translate/chunk_NNN.wav --model small --language <源语言，如 en/ja/ko；不确定就省略>
   ```
   - 读取 transcribe 输出的 JSON 行（`{"start","end","text"}`），**由 agent 自己把每段 text 翻译成中文**（不要调用外部翻译 API）。
   - 把每段追加写入 feed（一行一个 JSON）：
     `{"original": "<识别原文>", "translation": "<中文译文>"}`
     注意去重：与 feed 中最后几条原文做比对，跳过识别重叠/重复段落。
   - 删除已识别的 `chunk_NNN.wav`（只保留当前一轮），避免占盘。
   - 每 3~5 轮向用户简报一句「已翻译 N 句」，不要每轮都长篇汇报。
4. **停止**：用户说停止时，kill 录音/悬浮窗进程，feed 文件保留在 `live-translate/overlay_feed.jsonl` 供回看；给一段完整译文摘要。

## 参数（用户可指定）

- **目标语言**：默认中文，用户可要求译成英文/日文等。
- **源语言**：默认自动检测；用户明确说「日语直播」等时把 `--language` 传成 ja/ko/en… 提速并提升准确率。
- **机型弱**：`--model tiny`（快但较糙）或 `base`；默认 `small`。
- **chunk 长度**：默认 10 秒；会议场景可用 15 秒减少断句。

## 限制与红线

- **近实时而非毫秒级**：每轮 = 录音 10s + 识别数秒 + 翻译，译文通常落后声音约 15~30 秒。
- 首次识别需下载 whisper 模型（tiny ≈75MB / small ≈460MB）；CPU 识别时占核心较多。
- 识别的是**系统输出混音**——所有正在播放的声音都会被翻；安静/无声段落自动跳过（VAD）。
- 背景音乐会明显降低识别质量，建议提醒用户尽量关音乐。
- 不做逐字字幕文件导出（除非用户要求：此时循环结束后把 feed 整理成 srt）。
- 任何识别/翻译内容仅来自本机音频，不上传任何凭据。
