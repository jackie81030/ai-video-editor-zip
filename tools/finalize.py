"""把背景音樂混進已經 render 好的影片，輸出成品（舊版 finalize.sh 的 Python 版，Windows 不用 bash）。

用法：python finalize.py <影片.mp4> <背景音樂.mp3> <輸出.mp4> [音樂音量=0.18]

- 音樂自動循環蓋滿整支，開頭淡入 1.0 秒、結尾淡出 1.5 秒
- 音量預設 0.18（壓在人聲底下，0.15～0.25 都算合理）
- HyperFrames render 出來的人聲會比較小，先量一次補回 -14 LUFS（只補 -3～+6dB）
- 畫面直接複製不重新壓縮，約 1 秒，每次重新 render 後都要再跑一次
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import FFMPEG, probe_duration


def voice_gain(video: str) -> float:
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", video, "-vn", "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    found = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", err)
    if not found:
        return 0.0
    i = float(found[-1])
    if i < -70:
        return 0.0
    g = -14 - i
    if g < -3 or g > 6 or -0.3 < g < 0.3:
        g = 0.0
    print(f"人聲 {i:.1f} LUFS → 補 {g:.1f}dB")
    return round(g, 1)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    video, bgm, out = sys.argv[1], sys.argv[2], sys.argv[3]
    vol = float(sys.argv[4]) if len(sys.argv) > 4 else 0.18
    dur = probe_duration(video)
    fade_out = max(0.0, dur - 1.6)
    vg = voice_gain(video)
    graph = (f"[1:a]atrim=0:{dur:.3f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out:.3f}:d=1.5,volume={vol}[bgm];"
             f"[0:a]volume={vg}dB[v0];[v0][bgm]amix=inputs=2:normalize=0[mix];"
             f"[mix]alimiter=limit=0.87:level=disabled:latency=1,volume=0.96[aout]")
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-stream_loop", "-1", "-i", bgm,
                        "-filter_complex", graph, "-map", "0:v", "-map", "[aout]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", out])
    if r.returncode != 0:
        sys.exit(f"ffmpeg 失敗（exit {r.returncode}）")
    print(f"\n完成：{out}（{probe_duration(out):.1f} 秒，音樂音量 {vol}）")


if __name__ == "__main__":
    main()
