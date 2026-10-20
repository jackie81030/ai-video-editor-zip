"""把內建的思源宋體裝給目前使用者。用法：python setup_font.py

Mac：複製到 ~/Library/Fonts 就好（不用密碼，系統自己會認）。
Windows：
- 裝在使用者字型資料夾（%LOCALAPPDATA%\\Microsoft\\Windows\\Fonts）+ 使用者登錄檔，不需要系統管理員，不會跳 UAC
- 做法跟舊版 install-font.ps1 一樣：每個檔案只複製一次、登錄檔用檔名當 key（不會互相蓋掉）
- 裝過就跳過，可以重複執行
- 通知系統用「最多等 1 秒」的廣播（舊版用同步廣播，學員實測卡了近 4 小時）
"""
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401
from common import TOOLS

FONTS = TOOLS / "fonts"


def main_mac():
    files = sorted(FONTS.glob("*.otf"))
    dest_dir = Path.home() / "Library" / "Fonts"
    dest_dir.mkdir(parents=True, exist_ok=True)
    new = 0
    for f in files:
        if not (dest_dir / f.name).exists():
            shutil.copy2(f, dest_dir / f.name)
            new += 1
    print(f"思源宋體已裝好（{new} 個檔案）。" if new else "思源宋體已就位。")


def main():
    if sys.platform == "darwin":
        return main_mac()
    if os.name != "nt":
        print("不是 Windows 或 Mac，跳過字型安裝。")
        return
    import ctypes
    import winreg

    files = sorted(FONTS.glob("*.otf"))
    if not files:
        print("工具包裡沒有字型檔，跳過。")
        return
    dest_dir = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts"
    dest_dir.mkdir(parents=True, exist_ok=True)
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts")
    new = 0
    for f in files:
        dest = dest_dir / f.name
        if not dest.exists():
            shutil.copy2(f, dest)
            new += 1
        winreg.SetValueEx(key, f"{f.stem} (OpenType)", 0, winreg.REG_SZ, str(dest))
        ctypes.windll.gdi32.AddFontResourceW(str(dest))
    winreg.CloseKey(key)
    if new:
        HWND_BROADCAST, WM_FONTCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x001D, 0x0002
        res = ctypes.c_size_t()
        ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, ctypes.byref(res))
        print(f"思源宋體已裝好（{new} 個檔案）。")
    else:
        print("思源宋體已就位。")


if __name__ == "__main__":
    main()
