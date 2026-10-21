"""確認轉逐字稿模型在不在；不在就自動裝好。用法：python setup_model.py

工具包拆成兩個檔下載（GitHub 單一檔案上限 2GB）：
  AI-Cut-Kit-Windows.zip / AI-Cut-Kit-Mac.zip   工具包本體（學員解壓縮的那個）
  AI-Cut-Model-medium.zip    轉逐字稿模型（約 1.5GB）
這支程式依序：
  1. 模型已經在 tools/models/faster-whisper-medium → 什麼都不做
  2. 到「下載」「桌面」和工具包資料夾找 AI-Cut-Model*.zip → 解壓縮到對的位置
     Mac 的 Safari 會自動把 zip 解開成資料夾（faster-whisper-medium），所以也找這種資料夾
  3. 都找不到 → 從 config.json 的 model_url 下載（印進度）再解壓縮
"""
import json
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import KIT, TOOLS, MODEL_DIR

MODEL = Path(MODEL_DIR)
MIN_BYTES = 1_400_000_000  # model.bin 約 1.53GB，小於這個代表沒下載完整


def model_ok() -> bool:
    b = MODEL / "model.bin"
    return b.exists() and b.stat().st_size > MIN_BYTES and (MODEL / "tokenizer.json").exists()


PLACES = [Path.home() / "Downloads", Path.home() / "下載", Path.home() / "Desktop", KIT, KIT.parent]


def find_zip():
    found = []
    for d in PLACES:
        if d.exists():
            for pat in ("AI-Cut-Model*.zip", "AI剪片-模型*.zip"):
                found += [p for p in d.glob(pat) if p.stat().st_size > MIN_BYTES]
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def find_folder():
    """Safari／雙擊解開的模型資料夾。zip 裡只有一層 faster-whisper-medium，所以通常就叫這個名字"""
    for d in PLACES:
        if d.exists() and d != KIT:
            for m in [*d.glob("faster-whisper-medium*/model.bin"), *d.glob("AI-Cut-Model*/**/model.bin")]:
                if m.stat().st_size > MIN_BYTES and (m.parent / "tokenizer.json").exists():
                    return m.parent
    return None


def move_folder(src: Path):
    """用搬的不用複製：同一顆硬碟上是瞬間完成，也不會多佔 1.5GB"""
    import shutil
    print(f"找到模型資料夾：{src}\n搬進工具包…", flush=True)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    if MODEL.exists():
        shutil.rmtree(MODEL)  # 上次沒裝完整的殘骸（model_ok 已經判定不能用）
    shutil.move(str(src), str(MODEL))


def extract(zpath: Path):
    print(f"找到模型檔：{zpath}\n解壓縮中（約 1 分鐘）…", flush=True)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            name = info.filename.replace("\\", "/")
            if info.is_dir() or "faster-whisper-medium/" not in name:
                continue
            rel = name.split("faster-whisper-medium/", 1)[1]
            target = MODEL / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target, "wb") as dst:
                while chunk := src.read(8 << 20):
                    dst.write(chunk)


def download(url: str) -> Path:
    dest = Path.home() / "Downloads" / Path(url).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"沒找到模型檔，從網路下載（約 1.5GB，看網速 2～15 分鐘）…", flush=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done, last = 0, 0.0
        while chunk := r.read(4 << 20):
            f.write(chunk)
            done += len(chunk)
            if time.time() - last > 5:
                pct = f"{done / total * 100:.0f}%" if total else f"{done >> 20} MB"
                print(f"  下載中 {pct}", flush=True)
                last = time.time()
    tmp.replace(dest)
    return dest


def main():
    if model_ok():
        print("模型已就位。")
        return
    z = find_zip()
    folder = None if z else find_folder()
    if folder:
        move_folder(folder)
    elif not z:
        cfg = json.loads((TOOLS / "config.json").read_text(encoding="utf-8"))
        url = cfg.get("model_url", "")
        if "--download" not in sys.argv:  # 預設不在背景下載：AI 會用瀏覽器開這個網址，學員看得到進度條
            sys.exit(f"找不到模型。請用瀏覽器下載：{url}\n下載到「下載」資料夾後再跑一次。")
        if not url.startswith("http"):
            sys.exit("找不到模型檔，也還沒設定下載網址。請學員把「AI-Cut-Model-medium.zip」下載到「下載」資料夾後再試一次。")
        z = download(url)
    if not folder:
        extract(z)
    if not model_ok():
        sys.exit("模型解壓縮後檢查不通過（檔案可能沒下載完整）。請重新下載「AI-Cut-Model-medium.zip」再試一次。")
    print("模型已裝好。")


if __name__ == "__main__":
    main()
