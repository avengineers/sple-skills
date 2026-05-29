Param(
    [string]$SrcRoot = ".",
    [string[]]$Roots = @("src", "drivers"),
    [string]$OutDir = "build/gcc-analyzer"
)

$flagsFile = Join-Path "tools" "gcc-analyzer.flags"
if (-not (Test-Path $flagsFile)) {
    Write-Error "ERROR: $flagsFile not found (expected to be installed into project tools/)."
    exit 2
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$flags = Get-Content $flagsFile | Where-Object { $_ -and (-not $_.StartsWith("#")) }

$files = @()
foreach ($r in $Roots) {
    $path = Join-Path $SrcRoot $r
    if (Test-Path $path) {
        $files += Get-ChildItem -Path $path -Recurse -File -Filter *.c | ForEach-Object { $_.FullName }
    }
}

if ($files.Count -eq 0) {
    Write-Host "No .c files found under roots: $($Roots -join ', ') (within $SrcRoot)"
    exit 0
}

Write-Host "Running gcc -fanalyzer..."
Write-Host "  Roots:  $($Roots -join ', ')"
Write-Host "  OutDir: $OutDir"

foreach ($f in $files) {
    $obj = Join-Path $OutDir ("{0}.o" -f ([IO.Path]::GetFileName($f)))
    Write-Host "[gcc -fanalyzer] $f"
    & gcc @flags -c $f -o $obj
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "gcc -fanalyzer OK"
