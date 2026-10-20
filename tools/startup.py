"""每次對話開始跑一次：檢查更新 → 確認模型 → 裝字型。用法：python startup.py

三步合成一個指令，AI 才不會漏做其中一步（實測：分開寫時，AI 會跳過裝字型）。
每一步失敗都不會擋住下一步，最後印一行總結。
"""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401

STEPS = [("檢查更新", "update"), ("確認模型", "setup_model"), ("安裝字型", "setup_font")]


def main():
    results = []
    for label, mod in STEPS:
        print(f"── {label}", flush=True)
        try:
            importlib.import_module(mod).main()  # update 可能剛換掉其他小程式，所以每一步現在才載入
            results.append(f"{label} OK")
        except SystemExit as e:
            results.append(f"{label} 失敗：{e}")
        except Exception as e:  # noqa: BLE001
            results.append(f"{label} 失敗：{type(e).__name__}: {e}")
    print("\n總結：" + "；".join(results))


if __name__ == "__main__":
    main()
