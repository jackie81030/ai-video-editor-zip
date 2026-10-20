@echo off
rem npx shim: 'npx hyperframes ...' runs the bundled HyperFrames instead of downloading it.
rem Anything else goes to the bundled Node's npx. Only works inside run.cmd's environment.
setlocal enabledelayedexpansion
if /i not "%~1"=="hyperframes" (
  call "%KIT%\tools\node\npx.cmd" %*
  exit /b !errorlevel!
)
set "ARGS="
:collect
shift
if "%~1"=="" goto run
set ARGS=!ARGS! %1
goto collect
:run
node "%KIT%\tools\hyperframes\node_modules\hyperframes\bin\hyperframes.mjs" !ARGS!
exit /b !errorlevel!
