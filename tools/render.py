"""剪接 + 燒字幕 + 輸出 MP4。用法：python render.py 影片.mp4 edit.json [--no-subs]

edit.json 格式（所有時間都用「原始影片」的秒數，不用自己換算成品時間）：
{
  "keep": [[0.00, 3.20], [3.85, 10.40], ...],          要留下的片段，照順序
  "captions": [{"start": 0.10, "end": 1.60, "text": "包包是挺的", "hl": "挺的"}, ...],
  "font": "宋體"                                          可省略：宋體（預設）或 黑體
}
  hl（可省略）：這句裡要塗黃的字，要跟 text 裡的字一模一樣。
  hl_color（可省略）：塗黃以外的顏色，例如講到藍色時用 "#4DA3FF"。

這支程式會：
  1. 檢查每個剪點有沒有切到字的中間（用 words.json），有就印出警告
  2. 自動把字幕時間換算成剪完後的時間
  3. 輸出 <原檔名>_剪好.mp4，放在原影片旁邊
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import FFMPEG, TOOLS, probe_duration, work_dir

# 字型：預設思源宋體（工具包內建，setup_font.py 會裝好）；edit.json 寫 "font": "黑體" 就換成系統黑體
FONTS = {"宋體": "Source Han Serif TC",
         "黑體": "Microsoft JhengHei" if os.name == "nt" else "PingFang TC"}
FONT_DIR = TOOLS / "fonts"


HL_DEFAULT = "#FFD84D"


def ass_color(hex_rgb):
    """#RRGGBB → ASS 的 &HBBGGRR&"""
    h = hex_rgb.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def caption_text(c):
    text = c["text"].replace("\n", " ").replace("{", "（").replace("}", "）")
    hl = (c.get("hl") or "").strip()
    if hl and hl in text:
        color = ass_color(c.get("hl_color") or HL_DEFAULT)
        text = text.replace(hl, f"{{\\1c{color}}}{hl}{{\\1c&HFFFFFF&}}", 1)
    elif hl:
        print(f"警告：塗黃的字「{hl}」不在字幕「{text}」裡，這句不塗")
    return text


def ass_time(t):
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def video_size(path):
    out = subprocess.run(
        [common.FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
         "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    ).stdout
    st = json.loads(out)["streams"][0]
    w, h = st["width"], st["height"]
    rot = 0
    for sd in st.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    return (h, w) if abs(rot) in (90, 270) else (w, h)


def map_captions(captions, keep):
    """把原始時間的字幕，換算成剪完後的時間。跨過剪點的字幕會被接起來。"""
    offsets, acc = [], 0.0
    for a, b in keep:
        offsets.append(acc - a)
        acc += b - a
    mapped = []
    for c in captions:
        pieces = []
        for (a, b), off in zip(keep, offsets):
            s, e = max(c["start"], a), min(c["end"], b)
            if e - s > 0.05:
                pieces.append((s + off, e + off))
        if pieces:
            s, e = pieces[0][0], pieces[-1][1]
            if e - s >= 0.2:
                mapped.append({**c, "start": s, "end": e})
    # 時間不重疊
    for i in range(len(mapped) - 1):
        if mapped[i]["end"] > mapped[i + 1]["start"]:
            mapped[i]["end"] = mapped[i + 1]["start"]
    return mapped, acc


def check_cuts(video, keep):
    wpath = work_dir(video) / "words.json"
    if not wpath.exists():
        return []
    words = [w for seg in json.loads(wpath.read_text(encoding="utf-8")) for w in seg["words"]]
    warnings = []
    for a, b in keep:
        for t in (a, b):
            for w in words:
                if w["start"] + 0.04 < t < w["end"] - 0.04:
                    warnings.append(f"剪點 {t:.2f} 秒切在「{w['word'].strip()}」中間（{w['start']:.2f}-{w['end']:.2f}）")
    return warnings


def main():
    video = Path(sys.argv[1]).resolve()
    edit = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    burn = "--no-subs" not in sys.argv
    font_key = edit.get("font", "宋體")
    if font_key == "宋體" and not FONT_DIR.exists():
        font_key = "黑體"  # 沒有內建字型（例如舊版工具包）就退回系統黑體
    FONT = FONTS.get(font_key, font_key)
    dur = probe_duration(video)
    keep = [[max(0.0, float(a)), min(dur, float(b))] for a, b in edit["keep"] if float(b) > float(a)]
    keep.sort()
    for i in range(len(keep) - 1):
        if keep[i][1] > keep[i + 1][0]:
            sys.exit(f"錯誤：片段 {keep[i]} 和 {keep[i + 1]} 重疊了")

    for w in check_cuts(video, keep):
        print("警告：" + w)

    caps, total = map_captions(edit.get("captions", []), keep)
    wd = work_dir(video)
    W, H = video_size(video)

    if burn and caps:
        size = round(H * 0.038)
        ass = [
            "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 2", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV",
            f"Style: Default,{FONT},{size},&H00FFFFFF,&H00000000,&H64000000,1,1,{max(3, round(size * 0.08))},0,2,60,60,{round(H * 0.14)}",
            "", "[Events]", "Format: Layer, Start, End, Style, Text",
        ]
        for c in caps:
            ass.append(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Default,{caption_text(c)}")
        (wd / "subs.ass").write_text("\n".join(ass), encoding="utf-8")

    parts = []
    for i, (a, b) in enumerate(keep):
        parts.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}];")
        parts.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}];")
    parts.append("".join(f"[v{i}][a{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[vc][ac];")
    # fontsdir 直接指向工具包的字型資料夾：就算系統字型還沒裝好也找得到。用相對路徑，避開 Windows 的 C: 冒號
    fontsdir = os.path.relpath(FONT_DIR, wd).replace("\\", "/") if FONT_DIR.exists() else ""
    sub_filter = f"subtitles=subs.ass:fontsdir={fontsdir}" if fontsdir else "subtitles=subs.ass"
    parts.append(f"[vc]{sub_filter}[vo]" if burn and caps else "[vc]null[vo]")
    (wd / "filter.txt").write_text("\n".join(parts), encoding="utf-8")

    out = video.parent / f"{video.stem}_剪好.mp4"
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-stats", "-y", "-i", str(video),
           "-/filter_complex", "filter.txt", "-map", "[vo]", "-map", "[ac]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    print(f"輸出中：{len(keep)} 段，預計長度 {total:.1f} 秒…", flush=True)
    r = subprocess.run(cmd, cwd=wd)
    if r.returncode != 0:
        sys.exit(f"ffmpeg 失敗（exit {r.returncode}）。filter 在 {wd / 'filter.txt'}")
    real = probe_duration(out)
    (wd / "captions_final.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"完成：{out}")
    print(f"原本 {dur:.1f} 秒 → 成品 {real:.1f} 秒，字幕 {len(caps)} 句")


if __name__ == "__main__":
    main()
