@echo off
set PYTHONUTF8=1

:: Check if .venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

:: Install required packages
echo Installing packages...
pip install -r requirements.txt

:: Ensure Playwright browser is ready
echo Installing Playwright Chromium...
playwright install chromium

:: Run script
echo Running the script...
python convert_to_pdf.py

echo.
echo Process Finished.
pause