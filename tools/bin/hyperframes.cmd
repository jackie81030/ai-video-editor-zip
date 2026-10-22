@echo off
rem plain 'hyperframes' also runs the bundled version.
node "%KIT%\tools\hyperframes\node_modules\hyperframes\bin\hyperframes.mjs" %*
exit /b %errorlevel%
