"""共用設定：工具路徑、UTF-8 輸出。其他腳本都先 import 這個。"""
import os
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
KIT = TOOLS.parent
EXE = ".exe" if os.name == "nt" else ""

FFMPEG = str(TOOLS / "ffmpeg" / f"ffmpeg{EXE}") if (TOOLS / "ffmpeg" / f"ffmpeg{EXE}").exists() else "ffmpeg"
FFPROBE = str(TOOLS / "ffmpeg" / f"ffprobe{EXE}") if (TOOLS / "ffmpeg" / f"ffprobe{EXE}").exists() else "ffprobe"
MODEL_DIR = str(TOOLS / "models" / "faster-whisper-medium")

# 中文不亂碼
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ctranslate2 載入時會印一大段 pkg_resources 警告，不影響功能，但學員看了會以為壞掉
import warnings
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

# 有 NVIDIA 顯卡但沒裝 cuDNN 的電腦會直接崩潰，一律用 CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def work_dir(video: Path) -> Path:
    """每支影片一個工作資料夾，放逐字稿和中間檔。"""
    d = video.parent / "工作檔" / video.stem
    d.mkdir(parents=True, exist_ok=True)
    return d


def probe_duration(path) -> float:
    import subprocess
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    ).stdout.strip()
    return float(out)
