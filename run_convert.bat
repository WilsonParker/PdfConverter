@echo off
rem 파일명: run_convert.bat
rem 프로젝트 루트에서 더블클릭하여 실행

rem 스크립트 위치로 이동
cd /d %~dp0

rem 파이썬 가상환경이 없으면 생성하고 필요한 패키지와 playwright 브라우저 설치
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Ensure Python is installed and on PATH.
        pause
        exit /b 1
    )

    echo Installing required packages...
    .venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 echo Warning: pip install returned non-zero code.

    echo Installing Playwright browsers...
    .venv\Scripts\python.exe -m playwright install chromium
    if errorlevel 1 echo Warning: playwright install returned non-zero code.
)

rem 가상환경 활성화 및 스크립트 실행
echo Activating virtual environment and running convert_to_pdf.py...
call .venv\Scripts\activate.bat
if errorlevel 1 echo Warning: activate returned non-zero code.

python convert_to_pdf.py %*

echo.
echo Done. Press any key to exit.
pause
