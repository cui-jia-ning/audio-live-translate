# -*- coding: utf-8 -*-
"""用 faster-whisper 离线识别 WAV，逐段输出 JSON 行到 stdout。

用法:
    python transcribe.py --wav chunk_001.wav [--model small] [--language en]

每行输出: {"start": 0.0, "end": 3.2, "text": "..."}
--language 缺省时自动检测（建议外语视频显式指定，如 en/ja/ko，更快更准）。

依赖: pip install faster-whisper（首次运行会下载模型，small 约 460MB，tiny 约 75MB）。
"""
import argparse
import json
import os
import sys

# huggingface.co 在本机网络不可达，默认走国内镜像下载模型（可用 HF_ENDPOINT 覆盖）
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--model", default="small", help="tiny / base / small / medium，机器弱就用 tiny")
    ap.add_argument("--language", default=None, help="如 en ja ko fr de；缺省自动检测")
    args = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: 缺少依赖 faster-whisper，请先运行插件根目录的 setup.sh", file=sys.stderr)
        return 2

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        args.wav,
        language=args.language,
        vad_filter=True,
        beam_size=5,
    )
    for seg in segments:
        text = seg.text.strip()
        if text:
            print(
                json.dumps(
                    {"start": round(seg.start, 2), "end": round(seg.end, 2), "text": text},
                    ensure_ascii=False,
                ),
                flush=True,
            )
    print(f"# detected_language={info.language} p={info.language_probability:.2f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
