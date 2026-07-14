@echo off
chcp 65001 >nul
color 0A

echo.
echo  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗
echo  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
echo  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║
echo  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║
echo  ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝██████╔╝██║   ██║
echo.
color 0E
echo  ============================================================
echo   NEUROAUDIT — Shield Edition v6.7.0
echo   Felipe Soluciones IT
echo  ============================================================
echo.
color 0C
echo  [!] AVISO: Esta version de NEUROAUDIT es exclusiva para Linux.
echo.
echo      El soporte para Windows fue discontinuado a partir de v6.5.
echo      Esta edicion (Shield Edition) utiliza herramientas nativas
echo      de Linux como:
echo        - journalctl
echo        - ss / nmap
echo        - dpkg / apt
echo        - /proc / /etc/shadow
echo        - OSV.dev API para CVE scan
echo.
echo      Estas herramientas NO estan disponibles en Windows.
echo.
color 0A
echo  [i] Para usar NEUROAUDIT en Linux:
echo.
echo      1. Clonar el repositorio:
echo         git clone https://github.com/N1x-afl/neuroaudit.git
echo.
echo      2. Instalar:
echo         cd neuroaudit
echo         sudo ./instalar_neuroaudit.sh
echo.
echo      3. Ejecutar:
echo         sudo neuroaudit
echo.
color 07
echo  ============================================================
echo   Si necesitas soporte IT para Windows contacta a:
echo   Felipe Soluciones IT — github.com/N1x-afl
echo  ============================================================
echo.
pause
