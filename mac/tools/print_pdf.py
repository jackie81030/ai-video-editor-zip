"""把 HTML 印成 PDF（長影片選段的交件檔）。用法：python print_pdf.py 選段.html

用工具包內建的 Chrome（run.sh / run.cmd 會設好 HYPERFRAMES_BROWSER_PATH），學員電腦不用裝 Chrome。
PDF 存在 HTML 旁邊，同檔名。
"""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # 免安裝版 Python 不會自動找同資料夾的檔案
import common  # noqa: F401


def main():
    html = Path(sys.argv[1]).resolve()
    pdf = html.with_suffix(".pdf")
    browser = os.environ.get("HYPERFRAMES_BROWSER_PATH", "")
    if not Path(browser).exists():
        sys.exit("找不到內建的 Chrome。請用 run.sh / run.cmd 執行這支程式。")
    pdf.unlink(missing_ok=True)
    subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()],
                   capture_output=True, timeout=180)
    if not pdf.exists() or pdf.stat().st_size < 1000:
        sys.exit(f"PDF 沒印出來。HTML 在 {html}，可以請學員用瀏覽器打開後按「列印 → 另存為 PDF」。")
    print(f"PDF 完成：{pdf}")


if __name__ == "__main__":
    main()
