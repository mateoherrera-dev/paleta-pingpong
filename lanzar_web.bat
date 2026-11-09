@echo off
setlocal

:: Asegurar que el directorio de trabajo sea la raiz del repositorio
cd /d "%~dp0"
if not exist "app\index.html" (
    if exist "index.html" (
        cd ..
    )
)

echo ========================================================
echo   Paleta Ping Pong - Servidor Web Local
echo ========================================================
echo.

:: Detectar comando de Python disponible
set PYTHON_CMD=
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] No se encontro Python instalado en el sistema.
    echo Por favor instala Python desde https://www.python.org/ o la Microsoft Store
    echo y asegurate de marcar "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo Iniciando servidor en: http://localhost:8000/app/
echo (Nota: Para Web Bluetooth usa Chrome o Edge)
echo.
echo Presiona Ctrl + C para detener el servidor.
echo ========================================================
echo.

:: Abrir navegador en la app web
start "" "http://localhost:8000/app/"

:: Iniciar servidor HTTP en el puerto 8000
%PYTHON_CMD% -m http.server 8000

pause
