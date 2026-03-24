@echo off
setlocal

:: Script de inicio rápido para WebApp (Windows)

echo ==========================================
echo      WebApp - Inicio Rapido
echo ==========================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [91mX Python no esta instalado[0m
    echo Por favor, instala Python 3.7 o superior
    pause
    exit /b 1
)

echo [92m* Python detectado[0m
python --version
echo.

:: Verificar si el entorno virtual existe
if not exist "venv\" (
    echo [94mCreando entorno virtual...[0m
    python -m venv venv
    echo [92m* Entorno virtual creado[0m
    echo.
) else (
    echo [92m* Entorno virtual ya existe[0m
    echo.
)

:: Activar entorno virtual
echo [94mActivando entorno virtual...[0m
call venv\Scripts\activate.bat
echo [92m* Entorno virtual activado[0m
echo.

:: Instalar dependencias
echo [94mInstalando dependencias...[0m
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [92m* Dependencias instaladas[0m
echo.

:: Iniciar la aplicación
echo ==========================================
echo [92mIniciando WebApp...[0m
echo ==========================================
echo.
echo [94mLa aplicacion estara disponible en:[0m
echo [92m   http://localhost:5000[0m
echo.
echo [93mPresiona Ctrl+C para detener el servidor[0m
echo.

python app.py

pause
