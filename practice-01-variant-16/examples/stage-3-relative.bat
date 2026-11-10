@echo off
setlocal
pushd "%~dp0" || exit /b 1
for %%F in (minimal files deep) do (
    call "..\run.bat" --vfs "%%F.xml" --startup "stage-3.txt"
    if errorlevel 1 (
        popd
        exit /b 1
    )
)
popd
