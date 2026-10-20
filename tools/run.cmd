@echo off
rem run.cmd - run any command with the kit's bundled python / node / ffmpeg / hyperframes.
rem usage (PowerShell, in the kit folder): .\tools\run.cmd python .\tools\freecut\helpers\xxx.py ...
rem                                         .\tools\run.cmd npx hyperframes render . -o out.mp4
rem Nothing is installed; PATH changes apply to this one command only.
setlocal
set "KIT=%~dp0.."
for %%I in ("%KIT%") do set "KIT=%%~fI"
set "PATH=%KIT%\tools\bin;%KIT%\tools\python;%KIT%\tools\node;%KIT%\tools\ffmpeg;%PATH%"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
rem NVIDIA GPU without cuDNN crashes transcription natively: force CPU
set "CUDA_VISIBLE_DEVICES=-1"
rem model is bundled: never fetch from the network
set "HF_HUB_OFFLINE=1"
rem HyperFrames: bundled Chrome, no update check, no telemetry
set "HYPERFRAMES_SKIP_SKILLS=1"
set "HYPERFRAMES_NO_UPDATE_CHECK=1"
set "HYPERFRAMES_NO_TELEMETRY=1"
set "DO_NOT_TRACK=1"
for /d %%D in ("%KIT%\tools\chrome\chrome-headless-shell\*") do set "HYPERFRAMES_BROWSER_PATH=%%D\chrome-headless-shell-win64\chrome-headless-shell.exe"
set "AIKIT_MODEL=%KIT%\tools\models\faster-whisper-medium"
%*
exit /b %errorlevel%
