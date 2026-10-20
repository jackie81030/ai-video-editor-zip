"""量真正的靜音（不要只信逐字稿的時間）。用法：python silences.py 影片.mp4 [門檻dB=-35] [最短秒數=0.25]

輸出 工作檔/<影片名>/silences.json：[{"start":秒, "end":秒, "dur":秒}, ...]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import FFMPEG, work_dir


def main():
    video = Path(sys.argv[1]).resolve()
    noise = sys.argv[2] if len(sys.argv) > 2 else "-35"
    min_d = sys.argv[3] if len(sys.argv) > 3 else "0.25"
    err = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(video), "-af", f"silencedetect=noise={noise}dB:d={min_d}", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    out = [{"start": round(s, 3), "end": round(e, 3), "dur": round(e - s, 3)} for s, e in zip(starts, ends)]
    path = work_dir(video) / "silences.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for x in out:
        print(f"靜音 {x['start']:6.2f} - {x['end']:6.2f}（{x['dur']:.2f} 秒）")
    print(f"共 {len(out)} 段，存在 {path}")


if __name__ == "__main__":
    main()
