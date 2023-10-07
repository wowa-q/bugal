@echo off
setlocal



rem set environment variable:
rem CLI_PY_PATH, ANACONDA_ENV_PATH

rem Wechseln Sie in den Unterordner, in dem sich die cfg.bat-Datei befindet (Config).
cd /d "%~dp0bugal_p\bin"
rem Rufen Sie die cfg.bat-Datei auf.
call CFG.bat
@REM rem Gehen Sie zurück in das ursprüngliche Verzeichnis.
cd /d "%~dp0"
set "CURRENT_DIR=%CD%"
echo aktuell in: %CURRENT_DIR%
rem Setzen Sie den Pfad zur cli.py-Datei relativ zur Batch-Datei.
set "CLI_PY_PATH=%~dp0bugal\cli.py"

echo Interpreter Pfad: %ANACONDA_ENV_PATH%
@REM echo CLI Pfad: %CLI_PY_PATH%
 
rem Aktivieren Sie die Anaconda-Umgebung.
call %ANACONDA_ENV_PATH%\Scripts\activate

rem Wechseln Sie in das Verzeichnis der cli.py-Datei
cd /d "%~dp0bugal"
set "CURRENT_DIR=%CD%"
echo aktuell in: %CURRENT_DIR%
pause
rem Geben Sie den Befehl zum Ausführen Ihrer cli.py mit den gewünschten Parametern ein.
rem --cmd import-new-csv --csv-name 1001670080.csv
@REM python cli.py --cmd import-new-csv --csv_name 1001670080.csv
python cli.py --cmd test

rem Deaktivieren Sie die Anaconda-Umgebung, wenn Sie fertig sind.
@REM conda deactivate
cd /d "%CURRENT_DIR%"
pause
endlocal
