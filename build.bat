py -3.8 -m PyInstaller --log-level=WARN "Splatoon_Randomizer.spec"
if %errorlevel% neq 0 exit /b %errorlevel%
py -3.8 build.py
if %errorlevel% neq 0 exit /b %errorlevel%