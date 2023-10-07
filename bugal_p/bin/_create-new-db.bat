@echo off

:: import all environment variables
call bin\CFG.bat
if ERRORLEVEL 1 goto error
color 4
:: log the used Python interpreter
echo Python used: %PYTHON_ENV% >> %LOGFILE%

:: user iterface
:userif
cls
set /p dbname=definiere Name der Datenbank (z.B.: "example.db"):
echo DB name: %dbname% >> %LOGFILE%
set OPERATION=--cmd Import-new-csv --db_name %dbname%
echo %OPERATION% >> %LOGFILE%
%PYTHON_ENV% %RUNNER% %OPERATION%
:: TODO: prüfen ob db erstellt worden ist
 
:: label to finish in case of an error
:error
echo "something went'wrong"

:EOF
echo Neue datenbank erstellt