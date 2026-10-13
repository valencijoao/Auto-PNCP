@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller --noconfirm --clean --distpath . --workpath build AutoPainel.spec

if errorlevel 1 (
    echo Falha ao gerar o executavel.
    exit /b 1
)

echo Executavel criado em: %~dp0AutoPainel_atualizado.exe
