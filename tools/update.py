"""檢查並套用更新。用法：python update.py        （有新版就自動更新小檔案）
                       python update.py --check（只檢查，不更新）

更新分兩種：
  小檔案（說明書、小程式、特效技能）→ 這支程式直接從 GitHub 抓下來覆蓋，幾秒鐘
  大檔案（Python、Chrome、模型）    → 很少換；換的時候印出提示，請學員重新下載 zip
學員自己的東西（我的剪輯偏好.md、我的影片、錯誤回報、素材庫裡他加的檔案）永遠不會被動到。
沒網路、GitHub 連不到、還沒設定網址 → 安靜跳過，不影響剪片。
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import KIT, TOOLS

NEVER_TOUCH = {"我的剪輯偏好.md"}


def ver(s: str):
    return tuple(int(x) for x in s.strip().split("."))


def get(url: str, timeout=8) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


def main():
    cfg = json.loads((TOOLS / "config.json").read_text(encoding="utf-8"))
    base = cfg.get("update_base", "")
    if not base.startswith("http"):
        return  # 還沒設定更新來源
    local = (KIT / "VERSION").read_text().strip() if (KIT / "VERSION").exists() else "0.0.0"
    try:
        remote = get(base + "VERSION").decode().strip()
    except Exception:
        return  # 沒網路就跳過
    if ver(remote) <= ver(local):
        print(f"已經是最新版（{local}）。")
        return
    if "--check" in sys.argv:
        print(f"有新版：{local} → {remote}")
        return

    manifest = json.loads(get(base + "manifest.json"))
    kit_ver = (TOOLS / "KIT_VERSION").read_text().strip() if (TOOLS / "KIT_VERSION").exists() else "0"
    if int(manifest.get("min_kit_version", 0)) > int(kit_ver):
        print(f"新版（{remote}）需要新的工具包本體。請到下載頁重新下載「AI-Cut-Kit-Windows.zip」，"
              "解壓縮後把舊資料夾裡的「我的剪輯偏好.md」和「我的影片」搬過去。")
        return

    changed = []
    for rel, sha in manifest["files"].items():
        if rel in NEVER_TOUCH or ".." in rel:
            continue
        p = KIT / rel
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == sha:
            continue
        data = get(base + urllib.request.quote(rel), timeout=30)
        if hashlib.sha256(data).hexdigest() != sha:
            print(f"更新失敗：{rel} 下載不完整，這次先不更新。")
            return
        changed.append((p, data))
    for p, data in changed:  # 全部下載成功才一起寫入，不會更新一半
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (KIT / "VERSION").write_text(remote + "\n")
    print(f"已更新到 {remote}（{len(changed)} 個檔案）。")


if __name__ == "__main__":
    main()
