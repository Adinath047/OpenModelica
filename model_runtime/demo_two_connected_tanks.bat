@echo off
echo Demo OpenModelica executable
echo Received arguments: %*

set first_arg=%~1
echo %first_arg% | findstr /B /C:"-override=" >nul
if %errorlevel%==0 (
    echo Simulation launched with override flag.
    exit /b 0
)

echo Expected an OpenModelica -override argument. 1>&2
exit /b 1
