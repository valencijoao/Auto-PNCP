@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller --noconfirm --distpath . AutoPainel.spec

if errorlevel 1 (
    echo Falha ao gerar o executavel.
    exit /b 1
)

echo Executavel criado em: %~dp0AutoPainel.exe
