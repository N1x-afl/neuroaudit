@echo off
title NEUROAUDIT - Instalador Windows
color 0A

echo.
echo  +----------------------------------------------------------+
echo  ^|   NEUROAUDIT  --  INSTALADOR DE ENTORNO VIRTUAL         ^|
echo  ^|   Felipe Soluciones IT                                   ^|
echo  +----------------------------------------------------------+
echo.

:: Verificar Administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  ERROR: Ejecutar como Administrador.
    echo  Clic derecho sobre el archivo ^> "Ejecutar como administrador"
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set VENV_DIR=%SCRIPT_DIR%\.venv
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe
set LAUNCHER=%SCRIPT_DIR%\neuroaudit_win.bat

echo  Carpeta del proyecto: %SCRIPT_DIR%
echo.

:: Verificar Python
echo  [1/5] Verificando Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo  ERROR: Python no encontrado.
    echo  Descargar desde: https://www.python.org/downloads/
    echo  Tildar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   OK: %%i

:: Verificar version minima
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if %errorLevel% neq 0 (
    echo  ERROR: Se requiere Python 3.8 o superior.
    pause
    exit /b 1
)

:: Crear venv
echo.
echo  [2/5] Configurando entorno virtual...
if exist "%VENV_DIR%" (
    echo  Ya existe un venv en %VENV_DIR%
    set /p RESP="  Recrear desde cero? (S/N): "
    if /i "%RESP%"=="S" (
        rmdir /s /q "%VENV_DIR%"
        python -m venv "%VENV_DIR%"
        echo   OK: venv recreado
    ) else (
        echo   Usando venv existente.
    )
) else (
    python -m venv "%VENV_DIR%"
    echo   OK: venv creado
)

:: Actualizar pip
echo.
echo  [3/5] Actualizando pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet
echo   OK: pip actualizado

:: Instalar dependencias
echo.
echo  [4/5] Instalando reportlab, pyyaml, Pillow...
"%VENV_PYTHON%" -m pip install reportlab pyyaml Pillow --quiet
if %errorLevel% neq 0 (
    echo  ERROR instalando dependencias. Verificar conexion a internet.
    pause
    exit /b 1
)
"%VENV_PYTHON%" -c "import reportlab, yaml, PIL; print('  OK: dependencias verificadas')"

:: Crear lanzador usando %~dp0 para evitar problemas con rutas
echo.
echo  [5/5] Creando lanzador neuroaudit_win.bat...
(
echo @echo off
echo title NEUROAUDIT v6.1
echo net session ^>nul 2^>^&1
echo if %%errorLevel%% neq 0 ^(
echo     powershell -Command "Start-Process '%%~f0' -Verb RunAs"
echo     exit /b
echo ^)
echo "%%~dp0.venv\Scripts\python.exe" "%%~dp0neuroaudit.py" %%*
echo pause
) > "%LAUNCHER%"
echo   OK: %LAUNCHER%

:: Resumen
echo.
echo  +----------------------------------------------------------+
echo  ^|   INSTALACION COMPLETADA                                 ^|
echo  +----------------------------------------------------------+
echo.
echo   Para ejecutar: doble clic en neuroaudit_win.bat
echo   Reportes en  : %USERPROFILE%\Desktop\NEUROAUDIT_Reportes\
echo.
pause
