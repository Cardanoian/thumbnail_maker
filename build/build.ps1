$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = "python"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
}

& $Python -m pip install -r requirements.txt
& $Python scripts\create_icon.py
$env:PYTHONPATH = Join-Path $Root "src"
& $Python -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "테스트가 실패해서 빌드를 중단합니다."
}

& $Python -m PyInstaller --noconfirm --clean --distpath dist --workpath build\work build\thumbnail_maker.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller 빌드에 실패했습니다."
}

$Iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($Iscc) {
    & $Iscc build\installer.iss
} else {
    Write-Host "Inno Setup이 없어 dist\ThumbnailMaker\ThumbnailMaker.exe 만 만들었습니다."
    Write-Host "설치 파일을 만들려면 Inno Setup 6을 설치한 뒤 이 스크립트를 다시 실행하세요."
}
