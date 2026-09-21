#!/usr/bin/env bash
# audio-live-translate 本体/依赖安装脚本（插件登记/安装流程不会自动执行本脚本，请审阅后自行运行: bash setup.sh）
# 依赖：Python 3.9+ 与 pip；仅支持 Windows（WASAPI loopback 捕获）。
set -euo pipefail

PY="${DAIMON_USER_PYTHON:-python3}"
echo "using python: $PY"

"$PY" -c "import soundcard" 2>/dev/null || "$PY" -m pip install -U soundcard
"$PY" -c "import faster_whisper" 2>/dev/null || "$PY" -m pip install -U faster-whisper

echo "done. 首次识别时会自动下载 whisper 模型（tiny 约 75MB / small 约 460MB）。"
