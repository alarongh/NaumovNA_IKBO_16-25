$ErrorActionPreference = 'Stop'
$env:DOTNET_CLI_TELEMETRY_OPTOUT = '1'
$env:DOTNET_CLI_UI_LANGUAGE = 'en-US'
$env:DOTNET_NOLOGO = 'true'

$source = 'https://api.nuget.org/v3/index.json'
$root = Join-Path $PSScriptRoot '..\output\nuget-check'
$work = Join-Path $root ([Guid]::NewGuid().ToString('N'))
$version = '11.0.0'
$cases = [ordered]@{
    'Microsoft.Extensions.Options' = @(
        'Microsoft.Extensions.DependencyInjection.Abstractions',
        'Microsoft.Extensions.Primitives'
    )
    'Microsoft.Extensions.Configuration' = @(
        'Microsoft.Extensions.Configuration.Abstractions',
        'Microsoft.Extensions.Primitives'
    )
    'Microsoft.Extensions.Logging.Abstractions' = @(
        'Microsoft.Extensions.DependencyInjection.Abstractions',
        'System.Diagnostics.DiagnosticSource'
    )
}

foreach ($package in $cases.Keys) {
    $directory = Join-Path $work $package
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $project = Join-Path $directory 'Compare.csproj'
    @"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <NuGetAudit>false</NuGetAudit>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="$package" Version="[$version]" />
  </ItemGroup>
</Project>
"@ | Set-Content -LiteralPath $project -Encoding utf8

    $log = Join-Path $directory 'restore.log'
    $cache = Join-Path $directory 'packages'
    dotnet restore $project --source $source --packages $cache `
        --disable-parallel --no-http-cache --verbosity normal *> $log
    if ($LASTEXITCODE -ne 0) {
        Get-Content -LiteralPath $log -Tail 35
        exit $LASTEXITCODE
    }
    Write-Output "== $package $version =="
    Select-String -LiteralPath $log -Pattern 'Installed .* from' |
        ForEach-Object { $_.Line.Trim() -replace '\s+from.*', '' }

    Push-Location -LiteralPath $directory
    try {
        foreach ($dependency in $cases[$package]) {
            dotnet nuget why Compare.csproj $dependency --framework net10.0
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        }
    } finally {
        Pop-Location
    }
}
Write-Output "Restore logs: $work"
