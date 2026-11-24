$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
    New-Item -ItemType Directory -Force output | Out-Null
    foreach ($name in 'spec','copy','popcnt','vector-1','vector-2','vector-3') {
        & .\run.bat assemble --source "examples/$name.json" --output "output/$name.bin" --test
        if ($LASTEXITCODE -ne 0) { throw "Ошибка ассемблирования $name" }
    }
    foreach ($number in 1,2,3) {
        & .\run.bat run --binary "output/vector-$number.bin" --dump "output/vector-$number.xml" --start 1024 --end 1044
        if ($LASTEXITCODE -ne 0) { throw "Ошибка исполнения вектора $number" }
        Get-Content "output/vector-$number.xml"
    }
    & .\run.bat run --binary output/copy.bin --dump output/copy.xml --start 2048 --end 2056
    if ($LASTEXITCODE -ne 0) { throw 'Ошибка копирования' }
    & .\run.bat run --binary output/popcnt.bin --dump output/popcnt.xml --start 2048 --end 2048
    if ($LASTEXITCODE -ne 0) { throw 'Ошибка popcnt' }
} finally {
    Pop-Location
}
