# -*- coding: utf-8 -*-
"""桌面悬浮翻译窗：每秒读取 feed JSONL，滚动显示最近的原文与译文。

用法:
    python overlay.py [overlay_feed.jsonl]

feed 每行一个 JSON: {"original": "...", "translation": "..."}
窗口置顶；关闭窗口即退出。要结束翻译会话时直接关掉窗口，或 kill 本进程。
"""
import json
import os
import sys
import tkinter as tk

FEED = sys.argv[1] if len(sys.argv) > 1 else "overlay_feed.jsonl"
KEEP_LAST = 60  # 窗口内最多保留的句对数


def read_feed():
    items = []
    if not os.path.exists(FEED):
        return items
    with open(FEED, encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if obj.get("translation") or obj.get("original"):
                items.append(obj)
    return items


def main() -> int:
    root = tk.Tk()
    root.title("实时翻译窗")
    root.attributes("-topmost", True)
    root.geometry("560x380+60+60")

    text = tk.Text(root, wrap="word", bg="#101418", fg="#e8eaed", spacing3=6)
    text.pack(fill="both", expand=True, padx=8, pady=8)
    text.tag_config("orig", foreground="#9aa4b2", font=("Microsoft YaHei UI", 9))
    text.tag_config("trans", foreground="#ffffff", font=("Microsoft YaHei UI", 12, "bold"))
    text.insert("end", "等待翻译内容…（开始播放外语视频/会议即可）\n", "orig")
    text.config(state="disabled")

    def poll():
        items = read_feed()
        text.config(state="normal")
        text.delete("1.0", "end")
        if not items:
            text.insert("end", "等待翻译内容…（开始播放外语视频/会议即可）\n", "orig")
        for item in items[-KEEP_LAST:]:
            if item.get("original"):
                text.insert("end", item["original"] + "\n", "orig")
            if item.get("translation"):
                text.insert("end", item["translation"] + "\n", "trans")
            text.insert("end", "\n")
        text.see("end")
        text.config(state="disabled")
        root.after(1000, poll)

    root.after(1000, poll)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
