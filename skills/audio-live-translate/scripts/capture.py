# -*- coding: utf-8 -*-
"""捕获电脑音频输出（loopback 回放），保存为 16kHz 单声道 WAV。

用法:
    python capture.py --seconds 10 --out chunk_001.wav

依赖: pip install soundcard numpy（Windows 下通过 WASAPI loopback 抓取扬声器输出）。
"""
import argparse
import sys
import wave

import numpy as np


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=10.0, help="录制时长（秒），建议 8~15")
    ap.add_argument("--out", required=True, help="输出 WAV 路径")
    args = ap.parse_args()

    try:
        import soundcard as sc
    except ImportError:
        print("ERROR: 缺少依赖 soundcard，请先运行插件根目录的 setup.sh", file=sys.stderr)
        return 2

    mics = list(sc.all_microphones(include_loopback=True))
    if not mics:
        print("ERROR: 未找到 loopback 录音设备（需要 Windows WASAPI 回放捕获）", file=sys.stderr)
        return 2
    mic = None
    for m in mics:
        if "loopback" in m.name.lower():
            mic = m
            break
    if mic is None:
        mic = mics[0]

    samplerate = 16000
    numframes = int(samplerate * args.seconds)
    print(f"recording {args.seconds}s from loopback device: {mic.name}", file=sys.stderr)
    try:
        data = mic.record(samplerate=samplerate, numframes=numframes)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: 录音失败: {exc}", file=sys.stderr)
        return 2

    pcm = np.clip(data[:, 0] if data.ndim > 1 else data, -1.0, 1.0)
    pcm16 = (pcm * 32767).astype("<i2")
    with wave.open(args.out, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(pcm16.tobytes())
    print(f"saved: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
