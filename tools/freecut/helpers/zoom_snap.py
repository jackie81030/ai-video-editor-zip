#!/usr/bin/env python3
"""
zoom_snap.py — 重點句瞬間放大的時間點,吸到剪接點上(「跳在剪接點」規則)。

為什麼(2026-11-26,專業剪輯看學員片-04 說 zoom「有延遲、不俐落」):
  逐格量過,我們的放大本身就是 1 格瞬間切(tl.set),不是慢。問題在「落點」:
  - 放大/拉回跟剪接點差 1 格 → 觀眾看到兩次跳動,像卡一下(88.70 拉回、88.73 剪接)。
  - 放大時間用 Whisper 的字幕開頭 → 常常比真的開口晚 0.1-0.2 秒。
  參考片(IG 專業剪輯)量到:放大 1.0→1.2 只用 1 格,而且跟剪接點、新句子第一個字是同一格;
  不會自己拉回,下一個剪接點才回 1.0。Edits 內建的 Zoom / Super Zoom 都是動畫推近,不是這種。

規則:
  進(放大):想放大的句首 ±snap 秒內有剪接點 → 就用剪接點那一格。
             沒有 → 量音軌,找句首附近「音量從低谷升起」那一刻,往前 1 格。
  出(拉回):放大後的下一個剪接點那一格。拉回永遠跟剪接同一格,不自己單獨拉回。
  太長(下個剪接點 > --max 秒):有給句尾(--want 開頭-句尾)→ 句尾拉回(一次跳,沒關係);
             但句尾離剪接點 < 0.34 秒就改到剪接點那一格,不要差一點點跳兩次。沒給句尾 → 標 LONG。

用法:
  python3 zoom_snap.py 工作檔/edl.json --want 2.6-4.46,87.27,95.11 [--audio 原始檔.mp4] [--fps 30] [--snap 0.35] [--max 4]
  --want 想放大的句子:開頭 或 開頭-句尾(成品時間軸,通常就是 captions.json 的 start/end)。
  --audio edl 指的直式來源被清掉時,給原始檔(同一條時間軸,只是沒裁切)。
  --words 來源逐字稿(工作檔/transcripts/<原始檔名>.json,有字級時間)。**有就一定要給**:
          用「句首第一個字」當錨點再找最近的開口,比只看音量準。只看音量會抓到上一句的尾巴
          (學員片-04 字幕 2.60:「的話」2.40-2.60、「皮」2.80,只看音量抓成 2.47 =「的話」,放大早了一拍;教練 看 B/A 說舊的比較好)。
輸出:每句一行 zoom(FACE, 1.18, 進, 出); 直接貼進 creative 的 index.html,外加量法說明。
"""
import argparse, json, subprocess, sys
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")   # 繁中 Windows 主控台 cp950
except Exception:
    pass


AUDIO = None
WORDS = None   # [(source_start, text)]


def load_words(path):
    d = json.load(open(path, encoding="utf-8"))
    ws = d.get("words") or [w for seg in d.get("segments", []) for w in seg.get("words", [])]
    out = []
    for w in ws:
        t = (w.get("word") or w.get("text") or "").strip(" ,，。.!?！？、")
        if t:
            out.append((float(w.get("start", w.get("s"))), t))
    return sorted(out)


def first_word(spans, want):
    """成品時間 want 之後(同一段內)第一個真的字的成品時間。"""
    for a, b, r in spans:
        if a <= want < b:
            sw = r["start"] + (want - a)
            for st, t in WORDS:
                if st >= sw - 0.05 and st < r["end"]:
                    return a + (st - r["start"]), t
    return None, None


def cut_points(edl, fps):
    """成品時間軸上的剪接點(對齊到格)。回傳 [(t, range_index_after)]"""
    acc, cuts, spans = 0.0, [], []
    for i, r in enumerate(edl["ranges"]):
        d = r["end"] - r["start"]
        spans.append((acc, acc + d, r))
        acc += d
        if i < len(edl["ranges"]) - 1:
            cuts.append(round(acc * fps) / fps)
    return cuts, spans


def src_audio(edl, spans, t0, t1, sr=16000):
    """取成品時間 t0..t1 的音軌(可能跨剪接點,逐段接起來)。"""
    out = []
    for a, b, r in spans:
        lo, hi = max(a, t0), min(b, t1)
        if hi <= lo:
            continue
        src = AUDIO or edl["sources"][r["source"]]
        ss = r["start"] + (lo - a)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{hi-lo:.3f}", "-i", src,
                              "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
        out.append(np.frombuffer(raw, np.int16).astype(float))
    return np.concatenate(out) if out else np.zeros(0)


def voice_onset(edl, spans, want, sr=16000):
    """句首附近,音量從低谷升起的那一刻(20ms 一格)。找不到回 None。
    兩種情況分開(學員片-04 實測):
    - 字幕時間那一刻是安靜的 → 還在停頓裡。Whisper 常把句首放在停頓開頭,真的開口晚到 0.55 秒
      (字幕 8.32,真的開口 8.86)→ 取字幕時間之後、停頓結束的第一個升起。
      只找最近的會抓到上一句的尾巴(8.15)。
    - 字幕時間那一刻已經在講(連著講沒停)→ 取最近的升起(字幕 2.60 → 2.47)。
      這時不能去找後面的停頓,會跳到句子中間(3.03)。"""
    t0 = max(0.0, want - 0.35)
    s = src_audio(edl, spans, t0, want + 0.8, sr)   # Whisper 句首常落在停頓開頭,真的開口晚到 0.55 秒
    w = sr // 50
    if len(s) < w * 4:
        return None
    db = np.array([20 * np.log10(np.sqrt((s[i:i + w] ** 2).mean()) + 1) for i in range(0, len(s) - w, w)])
    quiet = db.max() - 15                                       # 比最大聲低 15dB 算安靜
    rises = []
    for i in range(2, len(db)):
        dip = db[max(0, i - 4):i].min()
        if db[i] - dip >= 8 and db[i - 1] - dip < 8:            # 剛升起來的那一格
            gap = 0
            while i - 1 - gap >= 0 and db[i - 1 - gap] < quiet:
                gap += 1
            rises.append((t0 + i * 0.02, gap))
    if not rises:
        return None
    k = int(round((want - t0) / 0.02))
    in_pause = np.median(db[k:k + 5]) < quiet       # 字幕時間「之後」0.1 秒安靜 = 停頓剛開始(8.32 前一格還有尾音)
    if in_pause:
        later = [r for r in rises if r[0] >= want - 0.02 and r[1] >= 3]
        if later:
            return later[0][0]
    near = [r for r in rises if abs(r[0] - want) <= 0.2]
    pool = near or rises
    return min(pool, key=lambda r: abs(r[0] - want))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl")
    ap.add_argument("--want", required=True, help="想放大的句首秒數(成品時間軸),逗號分隔")
    ap.add_argument("--fps", type=float, default=30)
    ap.add_argument("--snap", type=float, default=0.35, help="句首這麼近內有剪接點就直接用剪接點")
    ap.add_argument("--max", type=float, default=4.0, help="放大超過幾秒還沒遇到剪接點就標 LONG")
    ap.add_argument("--scale", default="1.35", help="倍數要看臉多大算(SKILL 5.1),這只是中景的預設")
    ap.add_argument("--audio", help="量開口用的影片(edl 的來源檔不在時)")
    ap.add_argument("--words", help="來源逐字稿 json(字級時間),有就給")
    a = ap.parse_args()
    global AUDIO, WORDS
    AUDIO = a.audio
    if a.words:
        WORDS = load_words(a.words)
    else:
        print("// ⚠ 沒給 --words:只靠音量找開口,連著講的句子可能抓到上一句尾巴", file=sys.stderr)

    edl = json.load(open(a.edl, encoding="utf-8"))
    fps = a.fps
    cuts, spans = cut_points(edl, fps)
    import os
    if not AUDIO:
        miss = [v for v in edl["sources"].values() if not os.path.exists(v)]
        if miss:
            print(f"// ⚠ 來源檔不在({miss[0]}),量不到開口。用 --audio 給原始檔", file=sys.stderr)
    total = spans[-1][1]
    fr = lambda t: round(t * fps) / fps

    print("// zoom_snap.py:放大跳在剪接點上;拉回永遠在下一個剪接點(同一格)")
    for item in [x.strip() for x in a.want.split(",") if x.strip()]:
        want, _, end = item.partition("-")
        want = float(want)
        end = float(end) if end else None
        near = [c for c in cuts if abs(c - want) <= a.snap]
        if near:
            tin = min(near, key=lambda c: abs(c - want))
            how = f"剪接點 {tin:.3f}"
        elif WORDS and first_word(spans, want)[0] is not None:
            anchor, word = first_word(spans, want)
            on = voice_onset(edl, spans, anchor) or anchor   # 字的時間也可能落在停頓裡(54.34 的「所以」,真的開口 54.88)
            tin = fr(on - 1 / fps)
            how = f"第一個字「{word}」{anchor:.2f},開口 {on:.2f} 前 1 格"
        else:
            on = voice_onset(edl, spans, want)
            if on is None:
                tin, how = fr(want), "量不到開口,用字幕時間(請自己看一下)"
            else:
                tin = fr(on - 1 / fps)
                how = f"開口 {on:.2f} 前 1 格(附近沒剪接點)"
        nxt = [c for c in cuts if c > tin + 0.5]
        tout = nxt[0] if nxt else fr(total)
        how_out, flag = "下個剪接點", ""
        if tout - tin > a.max:
            if end is None:
                flag = f"  ⚠ LONG {tout-tin:.1f}s:給句尾(開頭-句尾)就會在句尾拉回"
            else:
                near_c = [c for c in cuts if abs(c - end) < 0.34]
                if near_c:
                    tout, how_out = near_c[0], f"句尾 {end:.2f} 旁的剪接點"
                else:
                    tout, how_out = fr(end), f"句尾 {end:.2f}(離剪接點遠,一次跳)"
        close = [c for c in cuts if 0 < abs(c - tin) < 0.34 and c != tin]
        if close:
            flag += f"  ⚠ 進點旁 {close[0]:.3f} 還有一個剪接點,會跳兩次,考慮直接用它"
        print(f"zoom(FACE, {a.scale}, {tin:.3f}, {tout:.3f});   // 想要 {want:.2f} → 進:{how};出:{how_out}{flag}")


if __name__ == "__main__":
    main()
