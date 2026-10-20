"""把回報（復盤／錯誤／建議）送回課程團隊的 Google 表單。

用法：python send_report.py --name 學員稱呼 --project 專案名 --type 復盤|錯誤回報|功能建議|其他 --file 報告.md

- 收件匣是公開的 Google 表單，只能投遞，看不到別人的內容。
- 送出前會洗掉電腦帳號名稱和金鑰，送的是洗過的副本，原檔留在 錯誤回報/。
- 資料夾裡有 .回傳關閉（學員說不要回傳）或 .我是維護者（課程團隊自己）就不送。
- 送不出去不會中斷剪片，但會把原因印出來，不靜默失敗。
"""
import argparse
import getpass
import os
import platform
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import KIT

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSemFy9dciTJrBG2gRVIKER3GkLdu1WDszQI92CHF-YY319tqg/formResponse"
FIELDS = {"name": "entry.1502275075", "project": "entry.531432527", "type": "entry.969252018",
          "body": "entry.413630532", "env": "entry.834155630"}
# 表單那題是單選，送不在選項裡的值 Google 會回 400，所以不在清單裡的一律降級成「其他」
VALID_TYPES = {"復盤", "錯誤回報", "功能建議", "其他"}


def scrub(text: str) -> str:
    user = getpass.getuser()
    home = str(Path.home())
    for pat in (home, home.replace("\\", "/")):
        text = text.replace(pat, "~")
    if user:
        text = re.sub(rf"(?i)([a-z]:[\\/]users[\\/]){re.escape(user)}", r"\1USER", text)
        text = re.sub(rf"(?i)(/users/|/home/|/c/users/){re.escape(user)}", r"\1USER", text)
    # 名字帶 key/token/secret/password 的賦值，和常見金鑰前綴
    text = re.sub(r"(?i)([A-Za-z_-]*(key|token|secret|password)[A-Za-z_-]*\"?\s*[=:]\s*\"?)[A-Za-z0-9_./+-]{8,}", r"\1[金鑰已洗掉]", text)
    text = re.sub(r"(sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{8,}|github_pat_[A-Za-z0-9_]{8,}|xox[a-z]-[A-Za-z0-9-]{8,}|AKIA[A-Z0-9]{12,}|AIza[A-Za-z0-9_-]{8,}|hf_[A-Za-z0-9]{8,})", "[金鑰已洗掉]", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="未填")
    ap.add_argument("--project", default="未填")
    ap.add_argument("--type", default="其他")
    ap.add_argument("--file", required=True)
    a = ap.parse_args()

    path = Path(a.file).resolve()
    for guard in (".回傳關閉", ".我是維護者"):
        if (KIT / guard).exists() or (KIT / "錯誤回報" / guard).exists():
            print(f"偵測到 {guard}，依設定不回傳。報告留在 {path}")
            return

    body = path.read_text(encoding="utf-8", errors="replace")
    rtype = a.type
    if rtype not in VALID_TYPES:
        body = f"【原始類型：{rtype}（表單無此選項，已降級為 其他）】\n\n" + body
        rtype = "其他"
    env = f"{platform.system()} {platform.release()} {platform.machine()} · zip版 {(KIT / 'VERSION').read_text().strip() if (KIT / 'VERSION').exists() else '?'}"

    data = urllib.parse.urlencode({
        FIELDS["name"]: a.name, FIELDS["project"]: a.project, FIELDS["type"]: rtype,
        FIELDS["body"]: scrub(body), FIELDS["env"]: scrub(env),
    }).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(FORM_URL, data=data), timeout=20) as r:
            ok = r.status == 200
    except Exception as e:  # 防毒擋 HTTPS、離線、表單改了
        print(f"回傳沒成功（{type(e).__name__}: {e}）。沒關係，報告還在 {path}，可以用 LINE 傳給教練。")
        return
    print("已回傳給課程團隊。" if ok else f"回傳沒成功（HTTP {r.status}）。報告還在 {path}。")


if __name__ == "__main__":
    main()
