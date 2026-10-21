"""轉逐字稿。用法：python transcribe.py 影片.mp4

輸出到 工作檔/<影片名>/：
  words.json      每句和每個字的時間點（秒，原始影片時間）
  transcript.txt  好讀版，一句一行，前面有時間
  <影片名>.srt    字幕檔格式（長影片選段用）
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401  (設定 UTF-8、關掉 GPU)
from common import FFMPEG, MODEL_DIR, work_dir

import numpy as np


def srt_time(s: float) -> str:
    ms = max(0, round(s * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def main():
    video = Path(sys.argv[1]).resolve()
    out = work_dir(video)
    t0 = time.time()

    print("讀取聲音中…", flush=True)
    # 一律用 ffmpeg 解碼，不讓 faster-whisper 用 PyAV 讀檔（PyAV 新版會出 metadata_errors 錯誤）
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", str(video), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    total = len(audio) / 16000
    print(f"影片長度 {total:.1f} 秒，開始轉文字（第一次載入模型要等一下）…", flush=True)

    from faster_whisper import WhisperModel
    import opencc

    cc = opencc.OpenCC("s2tw")  # 只換字不換詞：s2twp 會把「腳本」改成「指令碼」
    model = WhisperModel(MODEL_DIR, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        audio,
        language="zh",
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=False,
        initial_prompt="以下是繁體中文的句子，包含口語停頓，例如：嗯、呃、那個。",
    )

    data, lines = [], []
    for s in segments:
        text = cc.convert(s.text.strip())
        words = [
            {"start": round(w.start, 3), "end": round(w.end, 3), "word": cc.convert(w.word), "p": round(w.probability, 2)}
            for w in (s.words or [])
        ]
        data.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": text, "words": words})
        line = f"[{s.start:6.2f} - {s.end:6.2f}] {text}"
        lines.append(line)
        print(f"{line}   （進度 {min(100, s.end / total * 100):.0f}%）", flush=True)

    (out / "words.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "transcript.txt").write_text("\n".join(lines), encoding="utf-8")
    srt = [f"{i}\n{srt_time(d['start'])} --> {srt_time(d['end'])}\n{d['text']}\n" for i, d in enumerate(data, 1)]
    (out / f"{video.stem}.srt").write_text("\n".join(srt), encoding="utf-8")
    print(f"完成，花了 {time.time() - t0:.0f} 秒。檔案在 {out}", flush=True)


if __name__ == "__main__":
    main()
