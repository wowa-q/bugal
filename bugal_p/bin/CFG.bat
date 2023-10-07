@echo off


rem Ermitteln Sie den Computernamen.
set "COMPUTERNAME=%COMPUTERNAME%"
echo Der Computernamen ist: %COMPUTERNAME%


rem Setzen Sie den Pfad zur Anaconda-Umgebung basierend auf dem Computernamen.
if /i "!COMPUTERNAME!"=="DEL01183" (
    @REM set "ANACONDA_ENV_PATH=C:\Users\wakl8754\Miniconda3\envs\genericEnv"
    set "ANACONDA_ENV_PATH=C:\Users\wakl8754\Miniconda3"
) else if /i "!COMPUTERNAME!"=="Computer2" (
    set "ANACONDA_ENV_PATH=C:\Pfad\zu\Ihrer\Anaconda\Umgebung\genericEnv2"
) else (
    @REM set "ANACONDA_ENV_PATH=C:\Users\wakl8754\Miniconda3\envs\genericEnv"
    set "ANACONDA_ENV_PATH=C:\Users\wakl8754\Miniconda3"
)






