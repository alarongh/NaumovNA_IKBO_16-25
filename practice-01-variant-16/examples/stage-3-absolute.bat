@echo off
setlocal
for %%F in (minimal files deep) do (
    call "%~dp0..\run.bat" --vfs "%~dp0%%F.xml" --startup "%~dp0stage-3.txt"
    if errorlevel 1 exit /b 1
)
