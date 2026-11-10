@echo off
setlocal
pushd "%~dp0" || exit /b 1
call "..\run.bat" --vfs "minimal.xml" --startup "stage-2.txt"
set "result=%errorlevel%"
popd
exit /b %result%
