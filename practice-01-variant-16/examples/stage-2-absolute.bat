@echo off
setlocal
call "%~dp0..\run.bat" --vfs "%~dp0minimal.xml" --startup "%~dp0stage-2.txt"
