@echo off

:: Define colors for output
set "GREEN="
set "YELLOW="
set "RED="
set "NC="

:: Function to display the menu
:show_menu
cls
echo ===============================
echo        DAN CAY AIRDROP - MENU
echo ===============================
echo.
echo 1 : Run Blum tool
echo 2 : Run Yescoin tool
echo 3 : Run Memefi tool
echo 4 : Run Hamster tool
echo 5 : Run Gemz tool
echo 6 : Run CexIO tool
echo 7 : Run Seed tools
echo 8 : Run TimeFarm tool
echo 9 : Run All
echo 0 : Exit
echo.
set /p choice="Please choose an option (0-7): "

:: Main loop
:main
if "%choice%"=="1" goto run_blum
if "%choice%"=="2" goto run_yescoin
if "%choice%"=="3" goto run_memefi
if "%choice%"=="4" goto run_hamster
if "%choice%"=="5" goto run_gemz
if "%choice%"=="6" goto run_cexio
if "%choice%"=="7" goto run_seed
if "%choice%"=="8" goto run_timefarm
if "%choice%"=="9" goto run_all
if "%choice%"=="0" goto exit
echo Invalid choice. Please choose again.
pause
goto show_menu

:run_blum
echo You chose to run the Blum tool.
start cmd /k "cd /d %~dp0/Blumdancay && python blumpyV2.py"
goto pause_and_return

:run_yescoin
echo You chose to run the Yescoin tool.
start cmd /k "cd /d %~dp0\YescoinPythonV2 && python yesV2.py"
goto pause_and_return

:run_memefi
echo You chose to run the Memefi tool.
start cmd /k "cd /d %~dp0/MemeFiPython && python MemeFiV4.py"
goto pause_and_return

:run_hamster
echo You chose to run the Hamster tool.
start cmd /k "cd /d %~dp0/HamsterPythonV2 && python hamsterKombatV3.py"
goto pause_and_return

:run_gemz
echo You chose to run the Gemz tool.
start cmd /k "cd /d %~dp0/GemzPython && python GemzV1.py"
goto pause_and_return

:run_cexio
echo You chose to run the CEXIO tool.
start cmd /k "cd /d %~dp0/CexIOPythonV1 && python cexio.py"
goto pause_and_return

:run_seed
echo You chose to run the SEED tool.
start cmd /k "cd /d %~dp0/SeedPython && python seedV2.py"
goto pause_and_return

:run_timefarm
echo You chose to run the SEED tool.
start cmd /k "cd /d %~dp0/TimeFarmPythonV1 && python TimeFarmV3.py"
goto pause_and_return


:run_all
start cmd /k "cd /d %~dp0/Blumdancay && python blumpyV2.py"
start cmd /k "cd /d %~dp0/HamsterPythonV2 && python hamsterKombatV3.py"
start cmd /k "cd /d %~dp0/YescoinPythonV2 && python yesV2.py"
start cmd /k "cd /d %~dp0/MemeFiPython && python MemeFiV4.py"
start cmd /k "cd /d %~dp0/SeedPython && python seedV2.py"
start cmd /k "cd /d %~dp0/TimeFarmPythonV1 && python TimeFarmV3.py"
start cmd /k "cd /d %~dp0/CexIOPythonV1 && python cexio.py"
start cmd /k "cd /d %~dp0/GemzPython && python GemzV1.py"

goto pause_and_return

:pause_and_return
pause
goto show_menu

:exit
exit /b
