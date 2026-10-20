#!/bin/bash
# run.sh - run any command with the kit's bundled python / node / ffmpeg / hyperframes (Mac).
# usage (in the kit folder): bash tools/run.sh python tools/xxx.py ...
#                            bash tools/run.sh npx hyperframes render . -o out.mp4
# Nothing is installed; PATH changes apply to this one command only.
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Files unzipped from a browser download are quarantined: macOS then blocks the bundled
# python with an "Apple could not verify" dialog. Clearing the flag on our own folder needs no password.
if [ ! -f "$KIT/tools/.unquarantined" ]; then
  xattr -dr com.apple.quarantine "$KIT" 2>/dev/null
  chmod +x "$KIT"/tools/python/bin/* "$KIT"/tools/node/bin/* "$KIT"/tools/ffmpeg/* "$KIT"/tools/bin/* 2>/dev/null
  touch "$KIT/tools/.unquarantined"
fi
export PATH="$KIT/tools/bin:$KIT/tools/python/bin:$KIT/tools/node/bin:$KIT/tools/ffmpeg:$PATH"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
export HF_HUB_OFFLINE=1
export HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1
for d in "$KIT"/tools/chrome/chrome-headless-shell/*/chrome-headless-shell-mac-arm64; do
  [ -x "$d/chrome-headless-shell" ] && export HYPERFRAMES_BROWSER_PATH="$d/chrome-headless-shell"
done
export AIKIT_MODEL="$KIT/tools/models/faster-whisper-medium"
export KIT
exec "$@"
