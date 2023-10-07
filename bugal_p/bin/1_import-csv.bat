@echo off

:: import all environment variables
call bin\CFG.bat
if ERRORLEVEL 1 goto error
color 4


:: user iterface
:userif
cls
set /p dbname=definiere Name der Datenbank (z.B.: "example.db"):
echo DB name: %dbname% >> %LOGFILE%
set /p csvname=definiere Name der csv Datei (z.B.: "test.csv"):
echo CSV Datei: %csvname% >> %LOGFILE%
set OPERATION=--cmd Import-new-csv --db_name %dbname% --csv_name %csvname% 
echo %OPERATION% >> %LOGFILE%
%PYTHON_ENV% %RUNNER% %OPERATION%
::%PYTHON_ENV% %RUNNER% --cmd Create-new-DB --db_name %dbname%
:: TODO: prüfen ob db erstellt worden ist
 
:: label to finish in case of an error
:error
echo "something went'wrong"

:EOF
echo Neue datenbank erstellt